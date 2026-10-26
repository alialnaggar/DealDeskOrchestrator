"""Opt-in, provider-independent hybrid action and binding provenance contract.

No transport, state mutation, database read or business calculation lives here.
The existing iterative contract remains unchanged.
"""

from datetime import date
import re

from .candidate_contract import TRADEOFF, validate_binding_proposal
from .phase1c_adapter import EvidenceMismatch


ACTION_VERSION = "hybrid-action-v1"
PACK_VERSION = "hybrid-evidence-pack-v1"
PROPOSAL_VERSION = "hybrid-binding-v1"
_WHOLE = re.compile(r"[1-9][0-9]*\Z", re.ASCII)
_TOOLS = frozenset(("inspect_line_supply", "inspect_fulfillment_paths",
                    "inspect_evidence_record"))


def canonical_quantity(value: object) -> bool:
    return isinstance(value, str) and len(value) <= 12 and bool(_WHOLE.fullmatch(value))


class HybridContractError(ValueError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def decision(raw: object, *, line_id: str, permitted_tools: tuple[str, ...]) -> dict:
    """One explicit tool or submission intent; plain text/READY is never final."""
    if not isinstance(raw, dict) or raw.get("version") != ACTION_VERSION:
        raise HybridContractError("invalid_action")
    kind = raw.get("kind")
    if kind == "inspect":
        if set(raw) != {"version", "kind", "tool_name", "arguments", "purpose_code"}:
            raise HybridContractError("invalid_action")
        name, args = raw["tool_name"], raw["arguments"]
        if (name not in _TOOLS or name not in permitted_tools or not isinstance(args, dict)
                or args.get("line_id") != line_id):
            raise HybridContractError("unauthorized_inspection")
        fields = ({"line_id", "horizon"} if name != "inspect_evidence_record"
                  else {"line_id", "source_category", "source_id"})
        required = ({"line_id"} if name != "inspect_evidence_record" else fields)
        if (not required.issubset(args) or not set(args).issubset(fields)
                or not isinstance(raw["purpose_code"], str)
                or raw["purpose_code"] not in ("check_dated_path", "inspect_source",
                                                 "check_line_supply")):
            raise HybridContractError("invalid_inspection")
        if name == "inspect_evidence_record" and any(
                not isinstance(args[x], str) or not args[x] or len(args[x]) > 128
                for x in ("source_category", "source_id")):
            raise HybridContractError("invalid_inspection")
        if "horizon" in args:
            try:
                if date.fromisoformat(args["horizon"]).isoformat() != args["horizon"]:
                    raise ValueError()
            except (TypeError, ValueError):
                raise HybridContractError("invalid_inspection") from None
        return dict(raw)
    if kind == "submit_proposal":
        if set(raw) != {"version", "kind", "submission_kind"} or raw[
                "submission_kind"] != "binding_partial_delivery":
            raise HybridContractError("invalid_submission_intent")
        return dict(raw)
    if kind in ("submit_finding", "abstain") and set(raw) == {"version", "kind"}:
        return dict(raw)
    raise HybridContractError("invalid_action")


def final(raw: object, intent: dict) -> dict:
    """Require an explicitly saved matching intent before interpreting a final."""
    if (not isinstance(intent, dict) or intent.get("version") != ACTION_VERSION
            or intent.get("kind") not in ("submit_proposal", "submit_finding", "abstain")
            or not isinstance(raw, dict) or set(raw) != {"version", "kind", "payload"}
            or raw.get("version") != ACTION_VERSION or raw.get("kind") != intent["kind"]
            or not isinstance(raw["payload"], dict)):
        raise HybridContractError("final_intent_mismatch")
    return dict(raw)


def _option_refs(option: dict) -> set[str]:
    if not isinstance(option, dict) or not isinstance(option.get("supply_ids"), list):
        raise HybridContractError("binding_option_incomplete")
    refs = set()
    if option.get("stock_id"):
        refs.add("inventory:" + str(option["stock_id"]))
    refs.update("inbound_supply:" + str(x) for x in option["supply_ids"])
    return refs


def strict_binding(raw: object, input, ledger: list[dict]) -> dict:
    """Hybrid canonical/returned-source precheck; NOT dated-slice verification.

    The pinned Phase 1C assess_reader_slices, not an option-date heuristic in
    Phase 2, determines quantity, dated support and cited source for each slice.
    """
    if (not isinstance(raw, dict) or set(raw) != {"line_id", "delivery_slices", "tradeoff_code"}
            or raw.get("line_id") != input.line_id or raw.get("tradeoff_code") != TRADEOFF
            or not isinstance(raw["delivery_slices"], list)
            or len(raw["delivery_slices"]) != 2):
        raise HybridContractError("invalid_binding_shape")
    for index, item in enumerate(raw["delivery_slices"]):
        if not isinstance(item, dict) or set(item) != {"quantity", "delivery_date", "source_refs"}:
            raise HybridContractError("invalid_binding_shape")
        quantity = item["quantity"]
        if not canonical_quantity(quantity):
            raise HybridContractError(f"quantity_noncanonical:{index}")
    checked = validate_binding_proposal(raw, input, ledger)
    return checked


def prove_source_slices(raw: dict, input, ledger: list[dict]) -> None:
    """Conservative exact-option check for D4 revision classification ONLY.

    Not a gate for construction: pinned Phase 1C may support a later delivery
    from an earlier option. Never use a failed exact-match diagnostic to reject
    an otherwise verified candidate; it only prevents automatic correction.
    """
    if (not isinstance(raw, dict) or raw.get("line_id") != input.line_id
            or not isinstance(raw.get("delivery_slices"), list)
            or len(raw["delivery_slices"]) != 2):
        raise EvidenceMismatch("source_to_slice_unproven:identity")
    for index, item in enumerate(raw["delivery_slices"]):
        if (not isinstance(item, dict) or not isinstance(item.get("source_refs"), list)
                or not item["source_refs"] or any(not isinstance(ref, str) for ref in
                                                    item["source_refs"])):
            raise EvidenceMismatch(f"source_to_slice_unproven:{index}")
        if len(item["source_refs"]) != len(set(item["source_refs"])) or not isinstance(
                item.get("delivery_date"), str):
            raise EvidenceMismatch(f"source_to_slice_unproven:{index}")
        try:
            if date.fromisoformat(item["delivery_date"]).isoformat() != item["delivery_date"]:
                raise ValueError()
        except ValueError:
            raise EvidenceMismatch(f"source_to_slice_unproven:{index}") from None
        refs = set(item["source_refs"])
        supported = False
        for event in ledger:
            identity = event.get("identity", {})
            if (event.get("tool") != "inspect_fulfillment_paths" or event.get("status") != "completed"
                    or event.get("args", {}).get("line_id") != input.line_id
                    or identity.get("assessment_id") != input.assessment_id
                    or identity.get("phase1c_run_id") != input.phase1c_run_id
                    or identity.get("subject_id") != input.subject_id
                    or identity.get("bundle_sha256") != input.bundle_sha256
                    or identity.get("source_input_digest") != input.source_input_digest
                    or identity.get("specialist") != "fulfillment"):
                continue
            result = event.get("result", {})
            if (result.get("evidence") != "eligible_binding"
                    or result.get("more_in_sealed_pool") or not refs.issubset(
                        set(event.get("returned_refs", [])))):
                continue
            for option in result.get("findings", {}).get("binding_options", []):
                if not isinstance(option, dict):
                    continue
                arrival = option.get("arrival")
                if not isinstance(arrival, str) or arrival != item["delivery_date"]:
                    continue
                if refs.issubset(_option_refs(option)):
                    supported = True
                    break
            if supported:
                break
        if not supported:
            raise EvidenceMismatch(f"source_to_slice_unproven:{index}")


def verified_source_slices(raw: dict, fixed: dict) -> None:
    """Match untrusted per-slice citations to Phase 1C's checked slice trace.

    Phase 1C computed all cumulative supply/date/location and source support.
    This compares identities only, adding no Phase 2 availability calculation.
    """
    trace = fixed.get("candidate_trace", {}).get("assessment", {})
    supported = trace.get("slices")
    if (trace.get("status") != "supply_supported_unreserved"
            or not isinstance(supported, list) or len(supported) != len(raw["delivery_slices"])):
        raise EvidenceMismatch("fixed_source_to_slice_unproven")
    for item, checked in zip(raw["delivery_slices"], supported):
        if (str(checked.get("line_id")) != raw["line_id"]
                or str(checked.get("quantity")) != item["quantity"]
                or str(checked.get("arrival_date")) != item["delivery_date"]
                or {ref.split(":", 1)[1] for ref in item["source_refs"]} - set(
                    checked.get("source_ids", []))):
            raise EvidenceMismatch("fixed_source_to_slice_unproven")
