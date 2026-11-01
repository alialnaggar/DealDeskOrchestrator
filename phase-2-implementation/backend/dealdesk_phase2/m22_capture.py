"""Read-only M2.2 checkpoint observation, not an answer key or an approval."""

from .candidate_graph import _package
from .evidence_bundle import unseal
from .fixed_specialists import domain_result
from .graph_state import SPECIALISTS, pinned_from_state, validate_result
from .m21_specialists import checked_candidate_context
from .phase1c_adapter import PHASE1C_COMMIT, EvidenceMismatch

VERSION = "m22-checkpoint-observation-v1"
HUMAN_ACTION = "Human review required; no approval, reservation or delivery promise"


def _attempts(rows, ctx, *, family):
    if type(rows) is not list:
        raise EvidenceMismatch("M2.2 attempt ledger is not a list")
    reserved = {}
    projected = []
    for row in rows:
        if type(row) is not dict or row.get("status") not in (
                ("reserved", "completed", "failed") if family == "fulfillment"
                else ("reserved", "returned")):
            raise EvidenceMismatch("M2.2 attempt status differs: " + str((family, row.get("status"))))
        name = row.get("specialist") if family != "fulfillment" else "fulfillment"
        if name not in SPECIALISTS or (family == "m20" and name not in (
                "configuration", "pricing")) or (family == "m21" and name not in (
                "credit", "policy", "approval_routing")) or (family == "typed" and
                name not in ("pricing", "credit")):
            raise EvidenceMismatch("M2.2 attempt specialist differs")
        if family in ("m20", "m21") and any(row.get(k) != v for k, v in (
                ("assessment_id", ctx.assessment_id),
                ("phase1c_run_id", str(ctx.phase1c_run_id)),
                ("subject_id", ctx.original_deal_id),
                ("bundle_sha256", ctx.bundle_sha256),
                ("source_input_digest", ctx.source_input_digest),
                ("specialist", name))):
            raise EvidenceMismatch("M2.2 attempt original identity differs")
        if family == "fulfillment" and any(row.get(k) != v for k, v in (
                ("assessment_id", ctx.assessment_id),
                ("subject_id", ctx.original_deal_id),
                ("bundle_sha256", ctx.bundle_sha256))):
            raise EvidenceMismatch("M2.2 fulfillment attempt identity differs")
        key = ((name, row.get("stage"), row.get("ordinal")) if family == "typed"
               else row.get("attempt_id") if family == "fulfillment"
               else (name, row.get("ordinal")))
        if key is None or isinstance(key, tuple) and any(v is None for v in key):
            raise EvidenceMismatch("M2.2 attempt key missing")
        if row["status"] == "reserved":
            if key in reserved:
                raise EvidenceMismatch("M2.2 repeated attempt reservation")
            reserved[key] = row
        else:
            prior = reserved.pop(key, None)
            if prior is None or any(prior.get(k) != row.get(k) for k in (
                    ("request_sha256", "model", "provider", "prompt_version")
                    if family in ("m20", "m21") else
                    ("request_sha256", "protocol_version") if family == "typed" else
                    ("attempt_id", "prompt_digest", "provider", "model"))):
                raise EvidenceMismatch("M2.2 returned attempt lacks matching reservation")
        usage = row.get("usage") if row["status"] != "reserved" else None
        if family == "fulfillment" and usage == {}:
            usage = None
        if family == "fulfillment" and type(usage) is dict and set(usage) == {
                "input_tokens", "output_tokens"}:
            usage = {"prompt_tokens": usage["input_tokens"],
                     "completion_tokens": usage["output_tokens"]}
        if usage is not None and (type(usage) is not dict or any(
                type(usage.get(k)) is not int or usage[k] < 0 for k in (
                    "prompt_tokens", "completion_tokens"))):
            raise EvidenceMismatch("M2.2 reported usage differs")
        elapsed = row.get("elapsed_ms", row.get("latency_ms")) if row[
            "status"] != "reserved" else None
        if elapsed is not None and (type(elapsed) is not int or elapsed < 0):
            raise EvidenceMismatch("M2.2 measured duration differs")
        projected.append({"specialist": name, "family": family,
            "status": row["status"], "stage": row.get("stage"),
            "ordinal": row.get("ordinal"), "action_kind": row.get("action_kind"),
            "provider": row.get("provider"), "model": row.get("model"),
            "prompt_version": row.get("prompt_version"),
            "contract_version": row.get("version", row.get("protocol_version")),
            "request_sha256": row.get("request_sha256"),
            "error_code": row.get("error_code"),
            "elapsed_ms": elapsed,
            "tokens": ({k: usage[k] for k in ("prompt_tokens", "completion_tokens")}
                       if usage is not None else None)})
    pending = ({key[0] for key in reserved} if family != "fulfillment" else
               {"fulfillment"} if reserved else set())
    return projected, pending


def capture_m22(state: dict, adapter, *, checkpoint_pending: bool = False) -> dict:
    """Project a stored checkpoint without contacting a model or modifying state.

    Reserved-only attempts are *uncertain*, not proof that a response completed.
    On-disk receipt verification is deliberately not claimed by this projection.
    """
    if type(state) is not dict or type(checkpoint_pending) is not bool:
        raise EvidenceMismatch("M2.2 checkpoint input differs")
    pinned = pinned_from_state(state)
    adapter.validate_pinned_context(pinned)
    ctx = pinned.context
    fixed = state.get("specialist_results")
    if type(fixed) is not dict or set(fixed) != set(SPECIALISTS):
        raise EvidenceMismatch("M2.2 requires all six original fixed slots")
    decision = unseal(state["fixed_decision"], state["fixed_decision_sha256"])
    if (str(decision.get("run_id")) != str(ctx.phase1c_run_id) or
            decision.get("deal_id") != ctx.original_deal_id):
        raise EvidenceMismatch("M2.2 original fixed decision identity differs")
    prior = {}
    for name in SPECIALISTS:
        validate_result(fixed[name], state, name)
        try:
            expected_result = domain_result(name, pinned, decision, ctx.assessment_id, prior)
            if name == "approval_routing" and state.get("review_status") != "approval_required":
                expected_result["payload"]["route_withheld"] = True
                expected_result["payload"]["roles_available_from_fixed_interface"] = False
                expected_result["finding"] = "withheld"
        except (KeyError, TypeError, ValueError) as exc:
            raise EvidenceMismatch("M2.2 original fixed mapping unavailable") from exc
        if expected_result != fixed[name]:
            raise EvidenceMismatch("M2.2 original fixed mapping differs")
        prior[name] = expected_result
    records = state.get("candidate_records", {})
    status = state.get("candidate_status")
    if type(records) is not dict or status not in ("not_started", "fixed_checked"):
        raise EvidenceMismatch("M2.2 candidate state incomplete or unsupported")
    if status == "fixed_checked":
        candidate_context = checked_candidate_context(state)
        candidate_id = candidate_context["candidate_id"]
        candidate = records[candidate_id]
        candidate_decision = unseal(candidate["fixed_decision"],
                                    candidate["fixed_decision_sha256"])
        prior_candidate = {}
        for name in SPECIALISTS:
            try:
                expected_result = domain_result(name, pinned, candidate_decision,
                    ctx.assessment_id, prior_candidate, subject_id=candidate_id)
                if name == "approval_routing" and candidate["fixed_business_status"] != (
                        "approval_required"):
                    expected_result["payload"]["route_withheld"] = True
                    expected_result["payload"]["roles_available_from_fixed_interface"] = False
                    expected_result["finding"] = "withheld"
            except (KeyError, TypeError, ValueError) as exc:
                raise EvidenceMismatch("M2.2 candidate fixed mapping unavailable") from exc
            if candidate["specialist_results"][name] != expected_result:
                raise EvidenceMismatch("M2.2 candidate fixed mapping differs")
            prior_candidate[name] = expected_result
    elif records:
        raise EvidenceMismatch("M2.2 unexpected candidate records")
    else:
        candidate_id, candidate = None, None
    package = state.get("reviewer_package", {})
    if type(package) is not dict:
        raise EvidenceMismatch("M2.2 reviewer package changed")
    expected = _package(state, candidate)
    if any(package.get(k) != expected.get(k) for k in (
            "assessment_id", "bundle_sha256", "original", "candidates",
            "candidate_workflow_status", "stopping_reason", "reviewer_action",
            "ai_execution", "ai_contribution", "typed_final_ai", "configuration_ai")):
        raise EvidenceMismatch("M2.2 original/candidate reviewer summary differs")
    if package.get("reviewer_action") != HUMAN_ACTION or package.get(
            "original", {}).get("review_status") != state.get("review_status"):
        raise EvidenceMismatch("M2.2 governed review unavailable")
    attempts = []
    uncertain = set()
    for family, key in (("m20", "m20_model_attempts"), ("typed", "typed_final_attempts"),
                        ("m21", "m21_model_attempts"),
                        ("fulfillment", "model_attempt_ledger")):
        rows, pending = _attempts(state.get(key, []), ctx, family=family)
        attempts.extend(rows)
        uncertain.update(pending)
    ledger = state.get("tool_access_ledger", [])
    if type(ledger) is not list:
        raise EvidenceMismatch("M2.2 tool ledger changed")
    exposed = {name: {} for name in SPECIALISTS}
    for event in ledger:
        if type(event) is not dict or type(event.get("identity")) is not dict:
            raise EvidenceMismatch("M2.2 tool event changed")
        identity = event["identity"]
        name = identity.get("specialist")
        if (name not in exposed or event.get("status") not in (
                "reserved", "completed", "budget_exhausted") or any(
                identity.get(k) != v for k, v in (
                    ("assessment_id", ctx.assessment_id),
                    ("phase1c_run_id", str(ctx.phase1c_run_id)),
                    ("subject_id", ctx.original_deal_id),
                    ("bundle_sha256", ctx.bundle_sha256),
                    ("source_input_digest", ctx.source_input_digest)))):
            raise EvidenceMismatch("M2.2 tool evidence identity differs")
        if event["status"] == "completed":
            result = event.get("result", {})
            rows = result.get("records", [])
            if (type(result) is not dict or type(rows) is not list or
                    type(event.get("returned_refs")) is not list or
                    "returned_refs" in result and event.get("returned_refs") !=
                    result["returned_refs"] or
                    name != "fulfillment" and "records" in result and event.get("returned_refs") !=
                    [row.get("ref") for row in rows if type(row) is dict]):
                raise EvidenceMismatch("M2.2 returned evidence changed")
            if name == "fulfillment":
                continue  # Fulfillment records use category/id, not scalar-claim refs.
            for row in rows:
                if type(row.get("fields")) is not dict:
                    raise EvidenceMismatch("M2.2 returned fields changed")
                ref = row["ref"]
                if ref in exposed[name] and exposed[name][ref] != row["fields"]:
                    raise EvidenceMismatch("M2.2 returned ref has conflicting values")
                exposed[name][ref] = row["fields"]
    m20 = state.get("m20_ai_results", {})
    m21 = state.get("m21_ai_results", {})
    typed = state.get("typed_final_results", {})
    if (any(type(x) is not dict for x in (m20, m21, typed)) or
            set(m20) - {"configuration", "pricing"} or
            set(m21) - {"credit", "policy", "approval_routing"} or
            set(typed) - {"pricing", "credit"} or
            any(name in m20 or name in m21 for name in typed)):
        raise EvidenceMismatch("M2.2 AI result slots overlap or differ")
    ai = {**m20, **typed, **m21}
    fulfillment = state.get("ai_fulfillment_result")
    if fulfillment:
        if (type(fulfillment) is not dict or fulfillment.get("execution") not in (
                "completed", "abstained", "skipped", "error") or any(
                fulfillment.get(k) != v for k, v in (
                    ("assessment_id", ctx.assessment_id),
                    ("phase1c_run_id", str(ctx.phase1c_run_id)),
                    ("subject_id", ctx.original_deal_id),
                    ("bundle_sha256", ctx.bundle_sha256)))):
            raise EvidenceMismatch("M2.2 Fulfillment result differs")
        ai["fulfillment"] = fulfillment
    handoff = (not state.get("stop_reason") and
               set(ai) == set(SPECIALISTS) and state.get("m21_review") is not None)
    if handoff:
        review = state["m21_review"]
        if (package.get("m21_ai") != review or review.get("subject_id") !=
                ctx.original_deal_id or review.get("fixed_review_status") !=
                state["review_status"] or review.get("specialists") != {name: {
                    "execution": ai[name]["execution"], "reason": ai[name]["reason"],
                    "validated_claims": ai[name]["validated_claims"]} for name in (
                        "credit", "policy", "approval_routing")} or
                review.get("fixed_route_withheld") != fixed[
                    "approval_routing"]["payload"]["route_withheld"]):
            raise EvidenceMismatch("M2.2 completed M2.1 review differs")
    elif state.get("m21_review") is not None:
        raise EvidenceMismatch("M2.2 partial run claims completed M2.1 review")
    elif package.get("m21_ai") is not None:
        stopped = package["m21_ai"]
        name = stopped.get("specialist") if type(stopped) is dict else None
        if (name not in ("credit", "policy", "approval_routing") or
                stopped.get("execution") != "stopped" or
                stopped.get("validated_claims") != [] or
                name not in ai or ai[name].get("execution") != "error" or
                stopped.get("reason") != ai[name].get("reason")):
            raise EvidenceMismatch("M2.2 partial review differs from failed specialist")
    complete = handoff and not checkpoint_pending and all(
        result.get("execution") != "error" for result in ai.values())
    contributions = {}
    for name in SPECIALISTS:
        result = ai.get(name)
        if result is None:
            contributions[name] = None
            continue
        if type(result) is not dict or result.get("execution") not in (
                "completed", "abstained", "skipped", "error"):
            raise EvidenceMismatch("M2.2 AI original result differs")
        if name in uncertain and result["execution"] in ("completed", "abstained"):
            raise EvidenceMismatch("M2.2 uncertain attempt cannot validate a contribution")
        if result["execution"] in ("completed", "abstained") and any(
                row["specialist"] == name and row["action_kind"] == "invalid"
                for row in attempts):
            raise EvidenceMismatch("M2.2 rejected terminal presented as validated")
        if name != "fulfillment":
            identity = state.get("typed_final_protocol", {}) if name in typed else result
            if (type(identity) is not dict or any(identity.get(k) != v for k, v in (
                    ("assessment_id", ctx.assessment_id),
                    ("phase1c_run_id", str(ctx.phase1c_run_id)),
                    ("subject_id", ctx.original_deal_id),
                    ("bundle_sha256", ctx.bundle_sha256),
                    ("source_input_digest", ctx.source_input_digest))) or
                    name in typed and identity.get("specialist") != name or
                    name not in typed and (result.get("specialist") != name or
                    result.get("producer_type") != "AI")):
                raise EvidenceMismatch("M2.2 AI original identity differs")
        claims = result.get("validated_claims", []) if name != "fulfillment" else []
        if (type(claims) is not list or result["execution"] != "completed" and claims):
            raise EvidenceMismatch("M2.2 non-completed result has findings")
        for claim in claims:
            if (type(claim) is not dict or set(claim) != {"ref", "field", "value"}
                    or claim.get("field") not in exposed[name].get(claim.get("ref"), {})
                    or type(claim["value"]) is not type(exposed[name][claim["ref"]][claim["field"]])
                    or claim["value"] != exposed[name][claim["ref"]][claim["field"]]):
                raise EvidenceMismatch("M2.2 unsupported validated claim")
        contributions[name] = {"execution": result["execution"],
            "reason": result.get("reason") or result.get("error"),
            "validated_claims": [dict(c) for c in claims],
            "contribution_kind": (result.get("contribution") or {}).get("kind")
                if name == "fulfillment" else None,
            "provider": result.get("provider"), "model": result.get("model"),
            "prompt_version": result.get("prompt_version"),
            "contract_version": result.get("version")}
    if uncertain:
        complete = False  # an orphan reservation cannot prove a completed assessment
    return {"version": VERSION, "assessment_id": ctx.assessment_id,
        "phase1c_pin": PHASE1C_COMMIT, "phase1c_run_id": str(ctx.phase1c_run_id),
        "original_deal_id": ctx.original_deal_id, "candidate_id": candidate_id,
        "bundle_sha256": ctx.bundle_sha256, "source_input_digest": ctx.source_input_digest,
        "data_snapshot_ref": ctx.data_snapshot_ref, "as_of_at": ctx.as_of_at.isoformat(),
        "fixed_decision_sha256": state["fixed_decision_sha256"],
        "checkpoint_status": "pending" if checkpoint_pending else "observed",
        "evaluation_status": "completed" if complete else "stopped_or_incomplete",
        "failure_stage": next((name for name in SPECIALISTS if ai.get(name, {}).get(
            "execution") == "error"), None),
        "fixed_original": {name: {k: fixed[name][k] for k in (
            "execution", "finding", "prerequisite", "error")} for name in SPECIALISTS},
        "fixed_candidate": ({name: {k: candidate["specialist_results"][name][k]
            for k in ("execution", "finding", "prerequisite", "error")}
            for name in SPECIALISTS} if candidate else None),
        "ai_original": contributions, "attempts": attempts,
        "request_count": sum(x["status"] == "reserved" for x in attempts),
        "returned_count": sum(x["status"] in ("returned", "completed") for x in attempts),
        "receipt_verification": "not_checked", "total_latency_ms": None,
        "total_tokens": None, "cost_usd": None,
        "review": {"status": state["review_status"], "action": HUMAN_ACTION,
                   "candidate_status": status, "customer_acceptance":
                   package["candidates"][0].get("customer_acceptance") if candidate else None},
        "accuracy": None}
