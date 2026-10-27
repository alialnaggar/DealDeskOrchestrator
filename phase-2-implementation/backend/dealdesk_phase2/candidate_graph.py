"""Binding candidate nodes attached to the original assessment LangGraph.

The graph records an AI hypothesis, then invokes the pinned Phase 1C verifier.
No node performs its own stock, schedule, commercial or approval calculation.
"""

from .candidate_contract import (CANDIDATE_VERSION, construct_candidate,
                                 validate_binding_proposal)
from .evidence_bundle import seal, unseal
from .fixed_specialists import domain_result
from .fulfillment_agent import eligible_line, restricted_input
from .graph_state import SPECIALISTS, pinned_from_state, validate_result
from .phase1c_adapter import EvidenceMismatch


def _proposal(state, adapter):
    pinned = pinned_from_state(state)
    pool = adapter.validate_pinned_context(pinned)
    selected, reason = eligible_line(state, pool)
    if selected is None:
        raise EvidenceMismatch("Candidate eligibility changed: " + reason)
    ai = state.get("ai_fulfillment_result", {})
    contribution = ai.get("contribution") or {}
    if (ai.get("execution") != "completed" or ai.get("producer_type") != "AI"
            or ai.get("specialist") != "fulfillment" or ai.get("assessment_id") != state["assessment_id"]
            or ai.get("phase1c_run_id") != state["phase1c_run_id"]
            or ai.get("subject_id") != pinned.context.original_deal_id
            or ai.get("bundle_sha256") != pinned.context.bundle_sha256
            or ai.get("source_input_digest") != pinned.context.source_input_digest
            or contribution.get("schema_version") != "3"
            or contribution.get("kind") != "binding_proposal"
            or contribution.get("verification") != "unverified"):
        raise EvidenceMismatch("AI binding contribution identity or status differs")
    used = sum(bool(e.get("counted")) for e in state.get("tool_access_ledger", []))
    input = restricted_input(pinned.context, pool, selected, max(0, 12 - used))
    raw = contribution["payload"]
    if raw.get("version") != CANDIDATE_VERSION or raw.get("verification") != "unverified":
        raise EvidenceMismatch("Binding proposal version differs")
    checked = validate_binding_proposal({"line_id": raw["line_id"],
        "delivery_slices": raw["delivery_slices"], "tradeoff_code": raw["tradeoff_code"]},
        input, state.get("tool_access_ledger", []))
    if checked != raw:
        raise EvidenceMismatch("Persisted binding proposal changed after validation")
    if state.get("hybrid_investigation_start"):
        from .hybrid_contracts import strict_binding
        if strict_binding({"line_id": raw["line_id"], "delivery_slices": raw["delivery_slices"],
                           "tradeoff_code": raw["tradeoff_code"]}, input,
                          state.get("tool_access_ledger", [])) != checked:
            raise EvidenceMismatch("Hybrid proposal changed at candidate handoff")
    return pinned, checked


def _record(state):
    records = state.get("candidate_records", {})
    if len(records) != 1:
        raise EvidenceMismatch("M1.7 requires exactly one isolated candidate")
    return next(iter(records.values()))


def _update(state, record, event):
    update = {"candidate_records": {record["candidate_id"]: record},
             "candidate_status": record["status"],
             "trace": [*state["trace"], event]}
    correction = state.get("fulfillment_correction", {})
    if (len(correction.get("attempts", [])) == 2 and record["status"] in
            ("fixed_checked", "fixed_rejected", "evidence_mismatch", "technical_error")):
        update["fulfillment_correction"] = {**correction, "attempts": [
            correction["attempts"][0], {**correction["attempts"][1],
                                         "candidate_status": record["status"],
                                         "fixed_supply_status": record.get("fixed_supply_status")} ]}
    return update


def _package(state, record=None):
    original = {"deal_id": state.get("context", {}).get("original_deal_id"),
        "run_id": state.get("phase1c_run_id"), "review_status": state.get("review_status"),
        "specialists": {k: {"execution": v["execution"], "finding": v["finding"]}
                        for k, v in state.get("specialist_results", {}).items()}}
    original["fulfillment_finding"] = state.get("specialist_results", {}).get(
        "fulfillment", {}).get("payload")
    ai = state.get("ai_fulfillment_result", {})
    contribution = ai.get("contribution") or {}
    ai_payload = contribution.get("payload") or {}
    item = None
    if record is not None:
        routing = record.get("specialist_results", {}).get("approval_routing", {}).get("payload", {})
        item = {k: record.get(k) for k in ("candidate_id", "parent_deal_id",
            "parent_candidate_id", "parent_run_id", "original_requested_date", "proposed_slices",
            "status", "fixed_supply_status", "fixed_business_status", "error",
            "source_input_digest", "bundle_sha256")}
        item["unmet_customer_requirements"] = ["original_requested_delivery_date",
                                                "customer_acceptance_of_revised_schedule"]
        item["specialists"] = {k: {"execution": v["execution"], "finding": v["finding"]}
                               for k, v in record.get("specialist_results", {}).items()}
        item["fulfillment_finding"] = record.get("specialist_results", {}).get(
            "fulfillment", {}).get("payload")
        cited = {ref for sl in record["proposed_slices"] for ref in sl["source_refs"]}
        sources = {}
        for event in state.get("tool_access_ledger", []):
            if event.get("status") != "completed" or event.get("tool") != "inspect_fulfillment_paths":
                continue
            for row in event.get("result", {}).get("records", []):
                ref = row["category"] + ":" + str(row["id"])
                if ref in cited and ref in event.get("returned_refs", []):
                    sources[ref] = {"reference": ref, "fields": row["fields"],
                                    "tool_evidence_status": event["result"].get("evidence")}
        item["returned_source_provenance"] = [sources[ref] for ref in sorted(cited) if ref in sources]
        item["verification_outcome"] = (
            "binding_supply_supported_unreserved"
            if record.get("status") == "fixed_checked"
            and record.get("fixed_supply_status") == "supply_supported_unreserved"
            else "not_confirmed_by_fixed_verifier")
        item["customer_acceptance"] = "pending"
        item["routing"] = {"eligible_for_ordinary_routing": bool(
            record.get("fixed_supply_status") == "supply_supported_unreserved"
            and record.get("fixed_business_status") == "approval_required"
            and not routing.get("route_withheld", True)),
            "required_roles": routing.get("required_roles") if routing.get(
                "roles_available_from_fixed_interface") else None,
            "roles_status": "fixed_interface" if routing.get(
                "roles_available_from_fixed_interface") else "unavailable_from_fixed_interface"}
    correction = state.get("fulfillment_correction", {})
    correction_summary = None
    if correction.get("failure") or len(correction.get("attempts", [])) > 1:
        correction_summary = {"version": correction["version"],
            "status": correction["status"],
            "first_failure_code": correction.get("failure", {}).get("code"),
            "attempts": [{"ordinal": item["ordinal"], "status": item["status"],
                          "candidate_status": item.get("candidate_status")}
                         for item in correction["attempts"]]}
    # Raw rejected hybrid responses remain private in the checkpoint. Expose
    # only counts/codes in the reviewer projection, never model prose or JSON.
    hybrid = state.get("hybrid_execution", {}) if state.get(
        "hybrid_investigation_start") else {}
    rejected = hybrid.get("rejections", [])
    hybrid_audit = {"rejection_count": len(rejected), "rejection_codes": [
        item.get("code") or item.get("reason", "unknown") for item in rejected]}
    if hybrid and not rejected and hybrid.get("result", {}).get("execution") == "error":
        hybrid_audit["execution_error"] = hybrid["result"].get("error")
    return {"version": "m1.7-review-v1", "assessment_id": state["assessment_id"],
        "bundle_sha256": state.get("context", {}).get("bundle_sha256"),
        "original": original, "candidates": [item] if item else [],
        "candidate_workflow_status": state.get("candidate_status", "not_started"),
        "stopping_reason": state.get("stop_reason"),
        "ai_execution": ai.get("execution", "not_run"),
        "ai_contribution": contribution.get("kind"),
        "validated_ai_summary": (ai_payload.get("review_summary", [])
                                 if contribution.get("schema_version") == "2" else []),
        "unverified_planning_ideas": ([claim for claim in ai_payload.get("validated_claims", [])
                                       if claim.get("type") == "candidate_idea"]
                                      if contribution.get("schema_version") == "2" else []),
        "audit_rejection_count": len(state.get("ai_claim_audit", [])) + len(rejected),
        **({"hybrid_audit": hybrid_audit} if hybrid else {}),
        "fulfillment_correction": correction_summary,
        "reviewer_action": "Human review required; no approval, reservation or delivery promise"}


def add_candidate_nodes(builder, adapter, connection_factory):
    """Register sequential nodes; the original graph remains the sole run state."""
    def construct(state):
        try:
            pinned, proposal = _proposal(state, adapter)
            if state.get("candidate_records"):
                raise EvidenceMismatch("Candidate slot already occupied")
            _, record = construct_candidate(adapter, pinned, proposal)
            return {**_update(state, record, "candidate_constructed:unverified"),
                    "candidate_state_version": CANDIDATE_VERSION}
        except Exception as exc:
            return {"candidate_status": "construction_rejected", "stop_reason":
                "candidate_construction:" + type(exc).__name__,
                "trace": [*state["trace"], "candidate_construction_rejected:" + type(exc).__name__]}

    def verify(state):
        try:
            pinned, proposal = _proposal(state, adapter)
            record = _record(state)
            candidate, recreated = construct_candidate(adapter, pinned, proposal)
            if record != recreated:
                raise EvidenceMismatch("Candidate identity or exact changes differ from checkpoint")
            checked, decision = adapter.verify_candidate(connection_factory, pinned, candidate)
            trace = checked.get("candidate_trace", {})
            if trace.get("candidate_id") != record["candidate_id"]:
                raise EvidenceMismatch("Fixed candidate trace has a different identity")
            if state.get("hybrid_investigation_start") and trace.get("assessment", {}).get(
                    "status") == "supply_supported_unreserved":
                from .hybrid_contracts import verified_source_slices
                verified_source_slices({"line_id": proposal["line_id"],
                                       "delivery_slices": proposal["delivery_slices"]}, checked)
            raw, digest, _ = seal(decision)
            record = {**record, "status": "fixed_checked",
                "fixed_supply_status": trace["assessment"]["status"],
                "fixed_business_status": decision["status"],
                "candidate_input_digest": trace["candidate_input_digest"],
                "fixed_decision": raw, "fixed_decision_sha256": digest}
            return _update(state, record, "candidate_fixed_checked:" + record["fixed_supply_status"])
        except Exception as exc:
            label = ("evidence_mismatch" if isinstance(exc, EvidenceMismatch) else
                     "fixed_rejected" if isinstance(exc, ValueError) else "technical_error")
            record = _record(state)
            record = {**record, "status": label, "error": type(exc).__name__}
            return _update(state, record, "candidate_verification:" + label)

    def specialist(name):
        def run(state):
            try:
                pinned = pinned_from_state(state)
                adapter.validate_pinned_context(pinned)
                record = _record(state)
                decision = unseal(record["fixed_decision"], record["fixed_decision_sha256"])
                if (decision.get("candidate_trace", {}).get("candidate_id") != record["candidate_id"]
                        or decision.get("run_id") != pinned.context.phase1c_run_id
                        or decision.get("deal_id") != pinned.context.original_deal_id):
                    raise EvidenceMismatch("Candidate fixed decision identity differs")
                prior = record["specialist_results"]
                result = domain_result(name, pinned, decision, state["assessment_id"], prior,
                                       subject_id=record["candidate_id"])
                if name == "approval_routing" and record["fixed_business_status"] != "approval_required":
                    result["payload"]["route_withheld"] = True
                    result["payload"]["roles_available_from_fixed_interface"] = False
                    result["finding"] = "withheld"
                validate_result(result, state, name, subject_id=record["candidate_id"])
                record = {**record, "specialist_results": {**prior, name: result}}
                return _update(state, record, "candidate_" + name + ":" + result["execution"])
            except Exception as exc:
                return {"candidate_status": "incomplete", "stop_reason":
                        "candidate_" + name + ":" + type(exc).__name__,
                        "trace": [*state["trace"], "candidate_" + name + ":error"]}
        return run

    def reconcile(state):
        record = _record(state)
        if any(key not in record["specialist_results"] for key in SPECIALISTS[:-1]):
            return {"candidate_status": "incomplete", "stop_reason": "candidate_results_missing"}
        if any(x["execution"] != "completed" for x in record["specialist_results"].values()):
            record = {**record, "status": "fixed_checked_incomplete"}
        return _update(state, record, "candidate_reconciled")

    def review(state):
        record = next(iter(state.get("candidate_records", {}).values()), None)
        return {"reviewer_package": _package(state, record),
                "trace": [*state["trace"], "candidate_review_prepared"]}

    def next_or_review(state):
        return "review" if state.get("stop_reason") or state.get("candidate_status") in (
            "construction_rejected", "evidence_mismatch", "fixed_rejected", "technical_error",
            "incomplete") else "continue"

    builder.add_node("candidate_construct", construct)
    builder.add_node("candidate_verify", verify)
    for name in SPECIALISTS[:-1]:
        builder.add_node("candidate_" + name, specialist(name))
    builder.add_node("candidate_reconcile", reconcile)
    builder.add_node("candidate_approval_routing", specialist("approval_routing"))
    builder.add_node("candidate_review", review)
    names = ("candidate_construct", "candidate_verify", *("candidate_" + n for n in SPECIALISTS[:-1]),
             "candidate_reconcile", "candidate_approval_routing")
    for current, following in zip(names, names[1:]):
        builder.add_conditional_edges(current, next_or_review,
                                      {"review": "candidate_review", "continue": following})
    builder.add_edge("candidate_approval_routing", "candidate_review")
    return "candidate_construct", "candidate_review"


def original_only_package(state):
    return _package(state)
