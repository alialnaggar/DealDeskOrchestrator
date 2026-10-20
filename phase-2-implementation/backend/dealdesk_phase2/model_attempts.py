"""Single-caller checkpoint ledger for live model requests; never stores keys or raw HTTP."""

from datetime import datetime, timezone

from .phase1c_adapter import EvidenceMismatch


def _state(graph, config, input):
    snapshot = graph.get_state(config)
    state = snapshot.values
    if (snapshot.next or state.get("assessment_id") != input.assessment_id
            or state.get("phase1c_run_id") != input.phase1c_run_id
            or state.get("context", {}).get("bundle_sha256") != input.bundle_sha256
            or state.get("context", {}).get("source_input_digest") != input.source_input_digest):
        raise EvidenceMismatch("Model attempt context differs from completed original")
    return state


def reserve(graph, config, input, attempt_id: str, provider: str, model: str,
            prompt_digest: str) -> dict | None:
    state = _state(graph, config, input)
    ledger = list(state.get("model_attempt_ledger", []))
    if any((x["provider"], x["model"]) != (provider, model) for x in ledger):
        raise EvidenceMismatch("Investigation provider/model cannot change on restart")
    prior = next((x for x in reversed(ledger) if x["attempt_id"] == attempt_id), None)
    if prior:
        if (prior["provider"], prior["model"], prior["prompt_digest"]) != (provider, model, prompt_digest):
            raise EvidenceMismatch("Model replay request changed")
        if prior["status"] != "completed":
            raise RuntimeError("Interrupted model request is not retried automatically")
        return prior
    ledger.append({"attempt_id": attempt_id, "provider": provider, "model": model,
                   "prompt_digest": prompt_digest, "assessment_id": input.assessment_id,
                   "subject_id": input.subject_id, "bundle_sha256": input.bundle_sha256,
                   "started_at": datetime.now(timezone.utc).isoformat(),
                   "status": "reserved"})
    graph.update_state(config, {"model_attempt_ledger": ledger}, as_node="finish")
    return None


def complete(graph, config, input, attempt_id: str, *, status: str,
             action: dict | None, usage: dict, latency_ms: int,
             response_model: str | None, error_code: str | None = None):
    ledger = list(_state(graph, config, input).get("model_attempt_ledger", []))
    prior = next((x for x in ledger if x["attempt_id"] == attempt_id), None)
    if prior is None or prior["status"] != "reserved":
        raise EvidenceMismatch("Model attempt reservation missing")
    ledger.append({**prior, "status": status, "action": action,
                   "usage": usage, "latency_ms": latency_ms,
                   "response_model": response_model, "error_code": error_code,
                   "finished_at": datetime.now(timezone.utc).isoformat()})
    graph.update_state(config, {"model_attempt_ledger": ledger}, as_node="finish")
