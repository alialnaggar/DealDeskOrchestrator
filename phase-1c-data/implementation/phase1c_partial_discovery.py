"""One bounded, read-only partial-delivery proposal from reader-selected facts.

Call within a stable REPEATABLE READ READ ONLY transaction. This is a
deterministic development experiment, not an autonomous agent or a promise.
"""

from datetime import date
from decimal import Decimal
from hashlib import sha256

from phase1c_candidate import (Candidate, DeliverySlice, FieldChange,
                               reader_input_digest)
from phase1c_candidate_batch import compare_candidate_set


def _whole_quantity(value):
    number = Decimal(value)
    return int(number) if number > 0 and number == int(number) else None


def _source_ids(option):
    return tuple(sorted(set(option["supply_ids"]) |
                        ({option["stock_id"]} if option.get("stock_id") else set())))


def discover_partial_delivery(bundle):
    """Return (candidate, reason); reason explains why discovery stopped."""
    run, deal, lines = bundle["run"], bundle["deal"], bundle["lines"]
    if (len(lines) != 1 or lines[0]["fulfillment_mode"] not in
            {"stocked_finished", "supplier_finished"}):
        return None, "Only one finished-product line is in this trial"
    line = lines[0]
    if line["fulfillment_group_code"]:
        return None, "A grouped configuration cannot be split in this trial"
    if deal["terms_json"].get("allow_partial_delivery") is not True:
        return None, "The customer did not permit partial delivery"
    requested = deal["requested_delivery_date"]
    if not isinstance(requested, date) or requested < run["as_of_at"].date():
        return None, "No usable future original requested date"
    quantity = _whole_quantity(line["quantity"])
    if quantity is None or quantity < 2:
        return None, "A positive whole-unit split is required"

    options = bundle["facts"]["lines"][0].get("shipping_options", [])
    possibilities = []
    for early in options:
        first = _whole_quantity(early["quantity"])
        if (early["arrival"] > requested or first is None or first >= quantity or
                not _source_ids(early)):
            continue
        for late in options:
            if (late["location"] != early["location"] or late["arrival"] <= requested or
                    late["quantity"] < quantity or not _source_ids(late)):
                continue
            possibilities.append((early, late, first))
    if not possibilities:
        return None, "No one location has a dated early slice and binding full supply later"

    # Prefer more units by the customer's date, then the earliest later arrival.
    early, late, first = min(possibilities, key=lambda p: (
        -p[2], p[1]["arrival"], p[0]["arrival"], p[0]["location"],
        _source_ids(p[0]), _source_ids(p[1])))
    first_ids = _source_ids(early)
    second_ids = tuple(x for x in _source_ids(late) if x not in first_ids)
    if not second_ids:
        return None, "Later slice has no distinct binding supply source"
    line_id = line["deal_line_id"]
    slices = (DeliverySlice(line_id, first, requested, first_ids, "confirmed"),
              DeliverySlice(line_id, quantity - first, late["arrival"], second_ids,
                            "confirmed"))
    digest = reader_input_digest(bundle)
    candidate = Candidate(
        candidate_id="C-DISC-" + sha256((digest + str(first) +
            late["arrival"].isoformat()).encode()).hexdigest()[:16],
        parent_deal_id=deal["deal_id"], parent_run_id=run["run_id"],
        proposal_kind="partial_delivery",
        changes=(FieldChange(None, "proposed_delivery_slices",
                             ((line_id, quantity, requested),),
                             tuple((s.line_id, s.quantity, s.arrival_date) for s in slices)),),
        customer_constraints=(f"{quantity} units", "original_requested_delivery_date",
                              "partial delivery permitted"),
        unmet_constraints=("original_requested_delivery_date",),
        delivery_slices=slices, evidence_ids=tuple(sorted(set(first_ids + second_ids))),
        as_of_at=run["as_of_at"], catalog_version=run["catalog_version_used"],
        policy_set_code=run["applied_policy_set_code"],
        data_snapshot_ref=run["data_snapshot_ref"],
        assumptions=("Customer acceptance of the later slice is pending",),
        tradeoff=(f"{first} units by the original request; {quantity - first} by "
                  f"{late['arrival'].isoformat()}, subject to customer acceptance."))
    return candidate, "Proposal formed from dated reader shipping options; full recheck required"


def discover_and_recheck(conn, run_id, *, reader_kwargs=None):
    """Produce one review package only after independent reader-backed recheck."""
    from phase1c_reader import read_run

    options = dict(reader_kwargs or {})
    if "candidate" in options:
        raise ValueError("Reader options cannot supply a candidate")
    original = read_run(conn, run_id, **options)
    candidate, reason = discover_partial_delivery(original)
    if candidate is None:
        return {"status": "no_proposal", "reason": reason, "selected_candidate_id": None}
    package = compare_candidate_set(conn, run_id, [candidate], reader_kwargs=options)
    if not package["validated_supply_option_ids"]:
        return {"status": "no_proposal", "reason": "Full reader recheck did not support the slices",
                "selected_candidate_id": None}
    return {"status": "review_option", "reason": reason, "candidate": candidate,
            "comparison": package, "selected_candidate_id": None}
