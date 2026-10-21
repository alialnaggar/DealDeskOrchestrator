"""M1.7 binding-only proposal boundary; Phase 1C decides business validity."""

from datetime import date
from hashlib import sha256
import json
from typing import Literal, TypedDict

from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import entries


CANDIDATE_VERSION = "m1.7-binding-v1"
TRADEOFF = "partial_delivery_requires_customer_acceptance"


class ProposedSliceV1(TypedDict):
    quantity: str
    delivery_date: str
    source_refs: list[str]


class BindingProposalV1(TypedDict):
    line_id: str
    delivery_slices: list[ProposedSliceV1]
    tradeoff_code: Literal["partial_delivery_requires_customer_acceptance"]


def validate_binding_proposal(raw: object, input, ledger: list[dict]) -> dict:
    """Check an untrusted proposal's shape and exposed sources, not its supply.

    The fixed reader alone checks cumulative quantities, dates, location and
    business rules. A visible binding option is required before construction;
    a supplier offer cannot be promoted by a model's commitment assertion.
    """
    if not isinstance(raw, dict) or set(raw) != {"line_id", "delivery_slices", "tradeoff_code"}:
        raise ValueError("Malformed binding proposal")
    if raw["line_id"] != input.line_id:
        raise EvidenceMismatch("Binding proposal line identity differs")
    if raw["tradeoff_code"] != TRADEOFF or not input.allow_partial_delivery:
        raise ValueError("Unsupported tradeoff or customer partial permission")
    slices = raw["delivery_slices"]
    if not isinstance(slices, list) or len(slices) != 2:
        raise ValueError("M1.7 supports exactly two delivery slices")
    parsed = []
    for item in slices:
        if not isinstance(item, dict) or set(item) != {"quantity", "delivery_date", "source_refs"}:
            raise ValueError("Malformed binding delivery slice")
        qty = item["quantity"]
        if not isinstance(qty, str) or not qty.isascii() or not qty.isdecimal() or int(qty) <= 0:
            raise ValueError("Binding slice requires a positive whole quantity")
        try:
            when = date.fromisoformat(item["delivery_date"])
            if when.isoformat() != item["delivery_date"]:
                raise ValueError("Noncanonical date")
        except (TypeError, ValueError) as exc:
            raise ValueError("Binding slice requires an ISO delivery date") from exc
        refs = item["source_refs"]
        if (not isinstance(refs, list) or not refs or len(refs) > 25
                or any(not isinstance(ref, str) or ":" not in ref for ref in refs)
                or len(refs) != len(set(refs))):
            raise ValueError("Binding slice requires distinct source references")
        parsed.append({"quantity": str(int(qty)), "delivery_date": when.isoformat(),
                       "source_refs": sorted(refs)})
    # A missing or truncated path projection is not evidence that a proposal
    # is supportable. The path options are only source authorization context.
    visible = set()
    for event in ledger:
        identity = event.get("identity", {})
        if event.get("status") != "completed" or event.get("args", {}).get("line_id") != input.line_id:
            continue
        if (identity.get("assessment_id") != input.assessment_id
                or identity.get("phase1c_run_id") != input.phase1c_run_id
                or identity.get("subject_id") != input.subject_id
                or identity.get("bundle_sha256") != input.bundle_sha256
                or identity.get("source_input_digest") != input.source_input_digest
                or identity.get("specialist") != "fulfillment"):
            raise EvidenceMismatch("Binding proposal tool ledger identity differs")
        result = event["result"]
        if (event["tool"] != "inspect_fulfillment_paths" or result.get("execution") != "completed"
                or result.get("evidence") != "eligible_binding"
                or result.get("more_in_sealed_pool")):
            continue
        exposed = set(event.get("returned_refs", []))
        for option in result.get("findings", {}).get("binding_options", []):
            refs = set()
            if option.get("stock_id"):
                refs.add("inventory:" + str(option["stock_id"]))
            refs.update("inbound_supply:" + str(x) for x in option.get("supply_ids", []))
            visible.update(refs & exposed)
    for item in parsed:
        if set(item["source_refs"]) - visible:
            raise EvidenceMismatch("Binding proposal cites a source not returned by authorized binding paths")
    if not visible:
        raise ValueError("No complete eligible binding path was returned")
    return {"version": CANDIDATE_VERSION, "line_id": input.line_id,
            "delivery_slices": parsed, "tradeoff_code": TRADEOFF,
            "verification": "unverified"}


def validate_from_graph(raw: object, input, graph, config) -> dict:
    return validate_binding_proposal(raw, input,
        entries(graph, config, input.assessment_id, input.bundle_sha256))


def construct_candidate(adapter, pinned, proposal: dict) -> tuple[object, dict]:
    """Trusted identity and exact Phase 1C dataclass; no business rule here."""
    pool = adapter.validate_pinned_context(pinned)
    if proposal.get("version") != CANDIDATE_VERSION or proposal.get("verification") != "unverified":
        raise EvidenceMismatch("Binding proposal version or unverified status differs")
    if len(pool["lines"]) != 1 or pool["lines"][0]["deal_line_id"] != proposal["line_id"]:
        raise ValueError("Pinned candidate reader supports one matching finished line")
    line, deal, context = pool["lines"][0], pool["deal"], pinned.context
    requested = deal["requested_delivery_date"]
    canonical = json.dumps(proposal, sort_keys=True, separators=(",", ":"))
    candidate_id = "M17-" + sha256((context.assessment_id + ":" + context.bundle_sha256
                                    + ":" + canonical).encode()).hexdigest()[:24]
    slices = tuple(adapter.candidate.DeliverySlice(
        proposal["line_id"], int(item["quantity"]), date.fromisoformat(item["delivery_date"]),
        tuple(ref.split(":", 1)[1] for ref in item["source_refs"]), "confirmed")
        for item in proposal["delivery_slices"])
    before = ((line["deal_line_id"], line["quantity"], requested),)
    after = tuple((x.line_id, x.quantity, x.arrival_date) for x in slices)
    candidate = adapter.candidate.Candidate(
        candidate_id=candidate_id, parent_deal_id=context.original_deal_id,
        parent_run_id=context.phase1c_run_id, proposal_kind="partial_delivery",
        changes=(adapter.candidate.FieldChange(None, "proposed_delivery_slices", before, after),),
        customer_constraints=("original_requested_delivery_date", "partial_delivery_permission"),
        unmet_constraints=("original_requested_delivery_date",), delivery_slices=slices,
        evidence_ids=tuple(sorted({ref.split(":", 1)[1] for item in proposal["delivery_slices"]
                                   for ref in item["source_refs"]})),
        as_of_at=context.as_of_at, catalog_version=context.catalog_version,
        policy_set_code=context.policy_set_code, data_snapshot_ref=context.data_snapshot_ref,
        assumptions=("Customer acceptance of the revised schedule is pending.",),
        tradeoff="Partial delivery requires customer acceptance; supply is unreserved.")
    return candidate, {"version": CANDIDATE_VERSION, "candidate_id": candidate_id,
        "parent_deal_id": context.original_deal_id, "parent_candidate_id": None,
        "parent_run_id": str(context.phase1c_run_id), "line_id": proposal["line_id"],
        "proposed_slices": proposal["delivery_slices"], "original_requested_date": requested.isoformat(),
        "source_input_digest": context.source_input_digest, "bundle_sha256": context.bundle_sha256,
        "status": "unverified", "specialist_results": {}, "error": None}
