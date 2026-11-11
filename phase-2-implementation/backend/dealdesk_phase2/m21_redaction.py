"""Provider-independent minimum-necessary M2.1 original evidence view.

The internal PostgreSQL ledger keeps exact selected references. A model sees
opaque per-bundle aliases and an allowlisted projection; the verifier alone
maps an alias back to the ledger's exact reference after a response.
"""

from hashlib import sha256

from .hybrid_pack import _canonical
from .m21_specialists import CREDIT_FIXED_VIEW, TOOLS, VERSION


_CREDIT_FIELDS = frozenset(("credit_limit", "unbilled_committed_amount",
    "commitments_as_of_at", "credit_status", "risk_rating", "last_review_date",
    "next_review_date", "fixed_commitments_fresh"))
_AR_FIELDS = frozenset(("as_of_date", "due_date", "outstanding_amount", "status"))
_PAYMENT_FIELDS = frozenset(("paid_date", "paid_amount", "due_date"))
CREDIT_VIEW_VERSION = "credit-invoice-match-v1"


def alias(bundle_sha256: str, kind: str, original: str) -> str:
    if not bundle_sha256 or not original or not kind:
        raise ValueError("m21_redaction_invalid_identity")
    return kind + ":" + sha256(_canonical([bundle_sha256, kind, original]).encode()).hexdigest()[:24]


def model_view(input: dict, observations: tuple[dict, ...]) -> tuple[dict, tuple[dict, ...], dict]:
    """Allowlist fields and bind model-visible refs to exact returned refs."""
    specialist = input["specialist"]
    if specialist not in TOOLS or input["permitted_tool"] != TOOLS[specialist]:
        raise ValueError("m21_redaction_wrong_specialist")
    fixed_credit_view = input.get("credit_fixed_view_version")
    if fixed_credit_view not in (None, CREDIT_FIXED_VIEW) or (
            fixed_credit_view is not None and specialist != "credit"):
        raise ValueError("m21_redaction_unapproved_credit_view")
    digest = input["bundle_sha256"]
    public = {key: input[key] for key in ("version", "prompt_version", "assessment_id",
        "phase1c_run_id", "bundle_sha256", "source_input_digest", "as_of_at",
        "specialist", "fixed_execution", "fixed_finding", "permitted_tool")}
    public["subject_id"] = alias(digest, "subject", input["subject_id"])
    if specialist == "credit":
        public["credit_view_version"] = CREDIT_VIEW_VERSION
        if fixed_credit_view:
            public["credit_fixed_view_version"] = CREDIT_FIXED_VIEW
    # Do not send customer ID, applied policy set, raw snapshot identifier,
    # invoice number, payment match or commitment evidence reference.
    ref_map = {}
    visible = []
    for observation in observations:
        if (observation.get("version") != VERSION or
                observation.get("execution") != "completed" or
                observation.get("tool") != TOOLS[specialist] or
                len(observation.get("records", [])) > 25):
            raise ValueError("m21_redaction_untrusted_observation")
        records = []
        for record in observation["records"]:
            original = record["ref"]
            kind = original.split(":", 1)[0]
            if specialist == "credit":
                allowed = {"credit_profile": _CREDIT_FIELDS, "receivable": _AR_FIELDS,
                           "payment": _PAYMENT_FIELDS,
                           "fixed_credit": frozenset(("credit_exposure",
                               "credit_over_limit_pct")) if fixed_credit_view else None}.get(kind)
            elif specialist == "policy":
                allowed = frozenset(("rule_id", "policy_area", "severity",
                    "required_action", "scope", "scope_type", "scope_value")) if kind == "policy_rule" else None
            else:
                allowed = (frozenset(("route_withheld", "roles_available_from_fixed_interface"))
                    if kind == "fixed_route" else frozenset(("rule_id", "role", "sequence"))
                    if kind == "fixed_role" else None)
            if allowed is None or not set(record["fields"]).issubset(allowed):
                # Extra fields must be reviewed, not silently shipped or dropped.
                # Known sensitive fields are removed explicitly below.
                sensitive = {"commitment_evidence_ref"} if kind == "credit_profile" else {
                    "invoice_number"} if kind in ("receivable", "payment") else set()
                if allowed is None or not set(record["fields"]).issubset(allowed | sensitive):
                    raise ValueError("m21_redaction_unreviewed_field")
            ref = alias(digest, kind, original)
            if ref in ref_map and ref_map[ref] != original:
                raise ValueError("m21_redaction_alias_collision")
            ref_map[ref] = original
            shown = {"ref": ref, "fields": {key: value for key, value in
                record["fields"].items() if key in allowed}}
            if specialist == "credit" and kind in ("receivable", "payment"):
                invoice = record["fields"].get("invoice_number")
                if type(invoice) is not str or not invoice:
                    raise ValueError("m21_redaction_missing_invoice_match_source")
                # Model-visible correlation only; this is not an evidence field
                # and cannot be submitted as a citable source value.
                shown["invoice_match_key"] = alias(digest, "invoice", invoice)
            records.append(shown)
        returned = [alias(digest, ref.split(":", 1)[0], ref)
                    for ref in observation["returned_refs"]]
        if (set(returned) != {r["ref"] for r in records} or len(returned) != len(records)
                or len(ref_map) != len(records)):
            raise ValueError("m21_redaction_returned_refs_mismatch")
        visible.append({"version": observation["version"], "tool": observation["tool"],
                        "execution": "completed", "records": records, "returned_refs": returned})
    if len(visible) > 1 or len(_canonical(visible).encode()) > 8192:
        raise ValueError("m21_redaction_request_evidence_oversize")
    wire = _canonical([public, visible])
    identifiers = {input["subject_id"], input["customer_id"], input["data_snapshot_ref"]}
    for observation in observations:
        identifiers.update(row["ref"] for row in observation["records"])
        for row in observation["records"]:
            identifiers.update(str(row["fields"][field]) for field in (
                "invoice_number", "commitment_evidence_ref") if field in row["fields"])
    if any(len(value) >= 5 and value in wire for value in identifiers):
        raise ValueError("m21_redaction_identifier_in_model_view")
    return public, tuple(visible), ref_map
