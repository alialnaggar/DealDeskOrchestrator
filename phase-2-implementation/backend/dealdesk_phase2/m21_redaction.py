"""Provider-independent minimum-necessary M2.1 original evidence view.

The internal PostgreSQL ledger keeps exact selected references. A model sees
opaque per-bundle aliases and an allowlisted projection; the verifier alone
maps an alias back to the ledger's exact reference after a response.
"""

from hashlib import sha256

from .hybrid_pack import _canonical
from .m21_specialists import CREDIT_FIXED_VIEW, POLICY_HIT_VIEW, ROUTE_VIEW, TOOLS, VERSION


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
    policy_hit_view = input.get("policy_hit_view_version")
    if policy_hit_view not in (None, POLICY_HIT_VIEW) or (
            policy_hit_view is not None and specialist != "policy"):
        raise ValueError("m21_redaction_unapproved_policy_view")
    route_view = input.get("route_view_version")
    if route_view not in (None, ROUTE_VIEW) or (
            route_view is not None and specialist != "approval_routing"):
        raise ValueError("m21_redaction_unapproved_route_view")
    digest = input["bundle_sha256"]
    public = {key: input[key] for key in ("version", "prompt_version", "assessment_id",
        "phase1c_run_id", "bundle_sha256", "source_input_digest", "as_of_at",
        "specialist", "fixed_execution", "fixed_finding", "permitted_tool")}
    public["subject_id"] = alias(digest, "subject", input["subject_id"])
    if specialist == "credit":
        public["credit_view_version"] = CREDIT_VIEW_VERSION
        if fixed_credit_view:
            public["credit_fixed_view_version"] = CREDIT_FIXED_VIEW
    elif policy_hit_view:
        public["policy_hit_view_version"] = POLICY_HIT_VIEW
    elif route_view:
        public["route_view_version"] = ROUTE_VIEW
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
        if specialist == "approval_routing" and route_view:
            source = observation["records"]
            if (not source or source[0].get("ref") != "fixed_route:" + input["subject_id"]
                    or source[0].get("fields", {}).get("route_withheld") is not True
                    and source[0].get("fields", {}).get("route_withheld") is not False):
                raise ValueError("m21_redaction_invalid_route_source")
            gate = source[0]["fields"]
            withheld = gate["route_withheld"]
            if (set(gate) != {"route_withheld", "roles_available_from_fixed_interface",
                    "fixed_business_status"} or gate["roles_available_from_fixed_interface"]
                    is not (not withheld) or gate["fixed_business_status"] not in (
                    "blocked", "needs_revision", "needs_evidence", "needs_commitment",
                    "approval_required") or (gate["fixed_business_status"] == "approval_required")
                    is not (not withheld) or not withheld and len(source) == 1):
                raise ValueError("m21_redaction_invalid_route_gate")
            sequence = -1
            for ordinal, row in enumerate(source[1:]):
                kind = row["ref"].split(":", 1)[0]
                fields = row["fields"]
                if kind == "fixed_route_step":
                    parts = row["ref"].split(":", 2)
                    if (withheld or len(parts) != 3 or set(fields) != {
                            "rule_id", "role", "sequence", "step_type"} or
                            type(fields["sequence"]) is not int or fields["sequence"] <= sequence
                            or fields["sequence"] < 0 or str(fields["sequence"]) != parts[1]
                            or fields["rule_id"] != parts[2] or
                            fields["step_type"] != "required_human_review"):
                        raise ValueError("m21_redaction_invalid_route_step")
                    sequence = fields["sequence"]
                elif kind == "fixed_route_reason":
                    if (not withheld or set(fields) != {"reason_code", "subject_scope_ref"}
                            or not fields["reason_code"] or
                            not fields["subject_scope_ref"].startswith("deal_line:") or
                            row["ref"] != "fixed_route_reason:" + str(ordinal)):
                        raise ValueError("m21_redaction_invalid_route_reason")
                else:
                    raise ValueError("m21_redaction_invalid_route_record")
        if specialist == "policy" and policy_hit_view:
            source_records = {r["ref"]: r["fields"] for r in observation["records"]}
            if len(source_records) != len(observation["records"]):
                raise ValueError("m21_redaction_duplicate_policy_ref")
        for record in observation["records"]:
            original = record["ref"]
            kind = original.split(":", 1)[0]
            if specialist == "policy" and policy_hit_view and kind == "policy_hit":
                fields = record["fields"]
                parts = original.split(":", 2)
                if (len(parts) != 3 or set(fields) != {"rule_id", "subject_scope_ref",
                        "result", "severity"} or fields["result"] != "triggered" or
                        fields["rule_id"] != parts[1] or
                        fields["subject_scope_ref"] != ("deal" if parts[2] == "deal"
                            else "deal_line:" + parts[2]) or
                        parts[2] != "deal" and not parts[2] or
                        source_records.get("policy_rule:" + parts[1], {}).get("rule_id")
                        != parts[1] or source_records["policy_rule:" + parts[1]].get(
                            "severity") != fields["severity"]):
                    raise ValueError("m21_redaction_invalid_policy_hit")
            if specialist == "credit":
                allowed = {"credit_profile": _CREDIT_FIELDS, "receivable": _AR_FIELDS,
                           "payment": _PAYMENT_FIELDS,
                           "fixed_credit": frozenset(("credit_exposure",
                               "credit_over_limit_pct")) if fixed_credit_view else None}.get(kind)
            elif specialist == "policy":
                allowed = (frozenset(("rule_id", "policy_area", "severity",
                    "required_action", "scope", "scope_type", "scope_value"))
                    if kind == "policy_rule" else frozenset(("rule_id",
                    "subject_scope_ref", "result", "severity")) if kind == "policy_hit"
                    and policy_hit_view else None)
            else:
                allowed = (frozenset(("route_withheld", "roles_available_from_fixed_interface",
                    "fixed_business_status")) if kind == "fixed_route" and route_view else
                    frozenset(("route_withheld", "roles_available_from_fixed_interface"))
                    if kind == "fixed_route" else frozenset(("rule_id", "role", "sequence"))
                    if kind == "fixed_role" else frozenset(("rule_id", "role", "sequence",
                    "step_type")) if kind == "fixed_route_step" and route_view else
                    frozenset(("reason_code", "subject_scope_ref")) if kind ==
                    "fixed_route_reason" and route_view else None)
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
            if specialist == "approval_routing" and route_view and kind == "fixed_route_reason":
                line = record["fields"]["subject_scope_ref"].removeprefix("deal_line:")
                shown["fields"]["subject_scope_ref"] = alias(digest, "deal_line", line)
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
