"""Checkpointed reservations make bounded calls and exposed citations restart-safe.

M1.2 admits one sequential caller per assessment. A future parallel caller must
introduce an atomic reservation/compare-and-swap mechanism before enablement.
"""

from .phase1c_adapter import EvidenceMismatch
from .tool_permissions import MAX_CALLS


def entries(graph, config, assessment_id: str, bundle_sha256: str) -> list[dict]:
    snapshot = graph.get_state(config)
    state = snapshot.values
    if (snapshot.next or state.get("assessment_id") != assessment_id
            or state.get("context", {}).get("bundle_sha256") != bundle_sha256):
        raise EvidenceMismatch("Tool session needs a completed, matching original assessment")
    return list(state.get("tool_access_ledger", []))


def reserve(graph, config, assessment_id: str, digest: str, call_id: str,
            tool: str, args: dict, identity: dict) -> tuple[str, dict | None]:
    ledger = entries(graph, config, assessment_id, digest)
    prior = next((item for item in reversed(ledger) if item["call_id"] == call_id), None)
    if prior is not None:
        if (prior["tool"] != tool or prior["args"] != args
                or prior.get("identity") != identity):
            raise EvidenceMismatch("Reused tool call ID changed arguments")
        return "replayed", prior
    if len([item for item in ledger if item.get("counted")]) >= MAX_CALLS:
        # One terminal record; repeated attempts cannot grow checkpoint storage.
        if not any(item.get("status") == "budget_exhausted" for item in ledger):
            graph.update_state(config, {"tool_access_ledger": [*ledger, {
                "call_id": call_id, "tool": tool, "args": args, "identity": identity,
                "counted": False,
                "status": "budget_exhausted", "returned_refs": []}]}, as_node="finish")
        return "budget_exhausted", None
    graph.update_state(config, {"tool_access_ledger": [*ledger, {
        "call_id": call_id, "tool": tool, "args": args, "identity": identity,
        "counted": True,
        "status": "reserved", "returned_refs": []}]}, as_node="finish")
    return "reserved", None


def complete(graph, config, assessment_id: str, digest: str,
             call_id: str, result: dict) -> None:
    ledger = entries(graph, config, assessment_id, digest)
    matches = [item for item in ledger if item["call_id"] == call_id]
    if len(matches) != 1 or matches[0]["status"] != "reserved":
        raise EvidenceMismatch("Tool reservation is missing or was already completed")
    # Append a completion event instead of rewriting the reservation event.
    graph.update_state(config, {"tool_access_ledger": [*ledger, {
        "call_id": call_id, "tool": matches[0]["tool"], "args": matches[0]["args"],
        "identity": matches[0]["identity"],
        "counted": False, "status": "completed", "result": result,
        "returned_refs": result["returned_refs"]}]}, as_node="finish")


def was_returned(graph, config, assessment_id: str, digest: str,
                 source_category: str, source_id: str, line_id: str) -> bool:
    ref = f"{source_category}:{source_id}"
    return any(item["status"] == "completed" and item["args"].get("line_id") == line_id
               and ref in item["returned_refs"]
               for item in entries(graph, config, assessment_id, digest))
