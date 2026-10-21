"""Restricted M1.3 Fulfillment input and unverified AI contribution contract."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Literal, Protocol, TypedDict

from .candidate_contract import validate_from_graph
from .claim_validation import FulfillmentClaimV2, assess_claims
from .phase1c_adapter import EvidenceMismatch
from .tool_ledger import was_returned


@dataclass(frozen=True)
class FulfillmentInputV1:
    assessment_id: str
    phase1c_run_id: str
    subject_id: str
    bundle_sha256: str
    source_input_digest: str
    line_id: str
    product_id: str
    requested_quantity: str
    quantity_by_requested_date: str
    requested_delivery_date: str
    destination_country_code: str
    destination_region: str
    allow_partial_delivery: bool
    fixed_fulfillment_status: str
    permitted_tools: tuple[str, ...]
    remaining_calls: int


class DeliverySliceClaimV1(TypedDict):
    quantity: str
    delivery_date: str
    commitment_claim: Literal["conditional", "unknown"]


class ProposalPayloadV1(TypedDict):
    line_id: str
    delivery_slices: list[DeliverySliceClaimV1]
    citations: list[str]
    tradeoffs: list[str]
    assumptions: list[str]
    unmet_requirements: list[str]
    uncertainty_reasons: list[str]


class FindingPayloadV1(TypedDict):
    line_id: str
    finding: str
    citations: list[str]
    uncertainty_reasons: list[str]


class AbstentionPayloadV1(TypedDict):
    reason: str
    uncertainty_reasons: list[str]


class TypedFulfillmentPayloadV2(TypedDict):
    line_id: str
    claims: list[FulfillmentClaimV2]
    notes: dict


class FulfillmentAIResultV1(TypedDict):
    version: Literal["1"]
    producer_type: Literal["AI"]
    specialist: Literal["fulfillment"]
    assessment_id: str
    phase1c_run_id: str
    subject_id: str
    bundle_sha256: str
    source_input_digest: str
    line_id: str
    execution: Literal["completed", "error", "skipped"]
    contribution: dict | None
    error: str | None


class InvestigationModel(Protocol):
    """Returns untrusted tool requests or domain content, never runtime identity."""

    def next_action(self, input: FulfillmentInputV1,
                    observations: tuple[dict, ...]) -> dict: ...


class OfflineModelDouble:
    """Deterministic script for offline tests; no provider connection."""

    def __init__(self, actions: tuple[dict, ...]):
        self.actions = actions

    def next_action(self, input: FulfillmentInputV1,
                    observations: tuple[dict, ...]) -> dict:
        return self.actions[len(observations)]


def _decimal(value) -> Decimal | None:
    try:
        number = Decimal(str(value))
        return number if number.is_finite() else None
    except (InvalidOperation, TypeError, ValueError):
        return None


def eligible_line(state: dict, pool: dict) -> tuple[dict | None, str]:
    """Gate on fixed prerequisites; independent Credit/Policy blocks are visible."""
    if state.get("stop_reason") or state.get("review_status") in (None, "pending"):
        return None, "original_fixed_assessment_incomplete"
    fixed = state.get("specialist_results", {})
    config, fulfillment = fixed.get("configuration"), fixed.get("fulfillment")
    if not config or config["execution"] != "completed" or config["finding"] != "confirmed":
        return None, "configuration_not_valid"
    if not fulfillment or fulfillment["execution"] != "completed":
        return None, "fixed_fulfillment_unavailable"
    if not pool["deal"].get("requested_delivery_date"):
        return None, "requested_delivery_date_missing"
    eligible = []
    for finding in fulfillment["payload"]:
        line = next((x for x in pool["lines"] if x["deal_line_id"] == finding["line_id"]), None)
        if not line or line["fulfillment_mode"] not in ("stocked_finished", "supplier_finished"):
            continue
        if finding["status"] not in ("late_alternative", "conditional"):
            continue
        requested = _decimal(finding.get("requested_quantity"))
        supported = _decimal(finding.get("quantity_by_requested_date"))
        if requested is None or supported is None or requested <= 0 or supported >= requested:
            continue
        eligible.append((line, finding))
    if len(eligible) != 1:
        return None, "no_single_supported_recoverable_shortage"
    return {"line": eligible[0][0], "finding": eligible[0][1]}, "eligible"


def restricted_input(context, pool: dict, selected: dict, remaining: int) -> FulfillmentInputV1:
    line, finding, deal = selected["line"], selected["finding"], pool["deal"]
    return FulfillmentInputV1(
        assessment_id=context.assessment_id, phase1c_run_id=str(context.phase1c_run_id),
        subject_id=context.original_deal_id, bundle_sha256=context.bundle_sha256,
        source_input_digest=context.source_input_digest,
        line_id=line["deal_line_id"], product_id=line["product_id"],
        requested_quantity=str(finding["requested_quantity"]),
        quantity_by_requested_date=str(finding["quantity_by_requested_date"]),
        requested_delivery_date=deal["requested_delivery_date"].isoformat(),
        destination_country_code=deal["destination_country_code"],
        destination_region=deal["destination_region"],
        allow_partial_delivery=deal["terms_json"].get("allow_partial_delivery") is True,
        fixed_fulfillment_status=finding["status"],
        permitted_tools=("inspect_line_supply", "inspect_fulfillment_paths", "inspect_evidence_record"),
        remaining_calls=remaining)


def validate_contribution(raw: dict, input: FulfillmentInputV1,
                          graph, config) -> dict:
    """Validate shape and seen citations, not business feasibility."""
    if isinstance(raw, dict) and raw.get("schema_version") == "3":
        if set(raw) != {"schema_version", "kind", "payload"} or raw["kind"] != "binding_proposal":
            raise ValueError("Malformed v3 binding contribution envelope")
        proposal = validate_from_graph(raw["payload"], input, graph, config)
        return {"schema_version": "3", "kind": "binding_proposal",
                "payload": proposal, "verification": "unverified",
                "review_summary_status": "fixed_verification_pending"}
    if isinstance(raw, dict) and raw.get("schema_version") == "2":
        if set(raw) != {"schema_version", "kind", "payload"}:
            raise ValueError("Malformed v2 contribution envelope")
        if raw["kind"] not in ("proposal", "finding_without_proposal", "abstention"):
            raise ValueError("Unknown v2 contribution")
        assessed = assess_claims(raw["payload"], input, graph, config)
        # Even a useful idea is not a verified candidate. Reviewer-facing text
        # comes solely from validated typed claims and Phase 1C fixed findings.
        kind = ("abstention" if raw["kind"] == "abstention" or
                assessed["disposition"] == "no_validated_claims"
                else "finding_without_proposal")
        return {"kind": kind, "payload": {
                    "line_id": input.line_id,
                    "validated_claims": assessed["accepted_claims"],
                    "review_summary": assessed["review_summary"]},
                "schema_version": "2", "model_contribution_kind": raw["kind"],
                "verification": None, "validation_disposition": assessed["disposition"],
                "claim_audit": {"rejected_claims": assessed["rejected_claims"],
                                "raw_model_notes": assessed["raw_model_notes"]}}
    if not isinstance(raw, dict) or set(raw) != {"kind", "payload"}:
        raise ValueError("Malformed contribution envelope")
    kind, payload = raw["kind"], raw["payload"]
    if kind not in ("proposal", "finding_without_proposal", "abstention") or not isinstance(payload, dict):
        raise ValueError("Unknown Fulfillment contribution")
    if kind == "proposal":
        keys = {"line_id", "delivery_slices", "citations", "tradeoffs", "assumptions",
                "unmet_requirements", "uncertainty_reasons"}
        slices = payload.get("delivery_slices")
        if (set(payload) != keys or payload["line_id"] != input.line_id
                or not isinstance(slices, list) or not slices
                or any(not isinstance(x, dict) or set(x) != {"quantity", "delivery_date",
                                                            "commitment_claim"}
                       or not isinstance(x["quantity"], str)
                       or not isinstance(x["delivery_date"], str)
                       or x["commitment_claim"] not in ("conditional", "unknown")
                       for x in slices)):
            raise ValueError("Malformed proposal shape")
        for item in slices:
            if _decimal(item["quantity"]) is None or _decimal(item["quantity"]) <= 0:
                raise ValueError("Proposal quantity must be a positive finite decimal string")
            try:
                date.fromisoformat(item["delivery_date"])
            except ValueError as exc:
                raise ValueError("Proposal date must be an ISO calendar date") from exc
        if not input.allow_partial_delivery and len(slices) > 1:
            raise ValueError("Submitted customer permission does not allow a split suggestion")
    elif kind == "finding_without_proposal":
        if set(payload) != {"line_id", "finding", "citations", "uncertainty_reasons"} \
                or payload["line_id"] != input.line_id or not isinstance(payload["finding"], str):
            raise ValueError("Malformed finding")
    else:
        if set(payload) != {"reason", "uncertainty_reasons"} or not isinstance(payload["reason"], str):
            raise ValueError("Malformed abstention")
    citations = payload.get("citations", [])
    uncertainty = payload.get("uncertainty_reasons")
    if (not isinstance(citations, list) or any(not isinstance(ref, str) or ":" not in ref
                                               for ref in citations)
            or not isinstance(uncertainty, list)
            or any(not isinstance(x, str) for x in uncertainty)):
        raise ValueError("Malformed citation or uncertainty list")
    if kind == "proposal" and (not citations or any(not isinstance(payload[k], list)
                                                       for k in ("tradeoffs", "assumptions", "unmet_requirements"))):
        raise ValueError("Proposal requires cited source and structured tradeoffs")
    # A source-based finding without an exposed citation cannot be audited.
    # No selected evidence belongs in an abstention with uncertainty reasons.
    if kind == "finding_without_proposal" and (
            not citations or not payload["finding"].strip()):
        raise ValueError("Finding requires a returned source citation and nonblank text")
    for ref in citations:
        category, source_id = ref.split(":", 1)
        if not was_returned(graph, config, input.assessment_id, input.bundle_sha256,
                            category, source_id, input.line_id):
            raise EvidenceMismatch("AI cited a source not returned by an authorized tool")
    return {"kind": kind, "payload": payload, "verification": "unverified" if kind == "proposal" else None,
            "review_summary_status": "withheld_legacy_unvalidated_prose"}


def runtime_envelope(input: FulfillmentInputV1, *, execution: Literal["completed", "error", "skipped"],
                     contribution: dict | None = None, error: str | None = None) -> FulfillmentAIResultV1:
    if execution == "completed" and (contribution is None or error):
        raise ValueError("Completed AI call requires a valid contribution")
    if execution == "error" and (not error or contribution is not None):
        raise ValueError("AI execution error cannot carry a contribution")
    return {"version": "1", "producer_type": "AI", "specialist": "fulfillment",
            "assessment_id": input.assessment_id, "phase1c_run_id": input.phase1c_run_id,
            "subject_id": input.subject_id, "bundle_sha256": input.bundle_sha256,
            "source_input_digest": input.source_input_digest,
            "line_id": input.line_id, "execution": execution,
            "contribution": contribution, "error": error}
