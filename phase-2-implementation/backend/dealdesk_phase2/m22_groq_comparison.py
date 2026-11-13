"""Read-only paired Groq development audit; never authorizes or sends inference.

The existing campaign registry/report owns membership, receipts and denominators.
The second model ID must be supplied AND verified outside this module before any
separately authorized provider use. Hosted transport gates remain unchanged.
"""

import re

from .m22_hosted_readiness import CONTRACTS
from .m22_registry import _manifest
from .phase1c_adapter import EvidenceMismatch

VERSION = "m22-groq-pair-readonly-v1"
BASELINE_MODEL = "openai/gpt-oss-120b"  # preserved historical arm, not a sender setting
DEVELOPMENT_COHORTS = frozenset(("pinned_development", "supplemental_control",
                                 "fault_injection"))
SOURCE_FIELDS = ("case_id", "original_deal_id", "phase1c_run_id", "cohort",
                 "case_family", "source_input_digest", "bundle_sha256", "as_of_at",
                 "data_snapshot_ref")


def inspect_groq_pair(existing, alternative, *, second_model_id):
    """Compare frozen identities and existing reports, without another runner.

    This is a diagnostic of *declared* model arms. An owner-local manifest and
    its report are not independently authenticated proof of a provider send.
    Missing wall, usage, cost and semantic judgments remain missing.
    """
    if (type(second_model_id) is not str or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._/-]{2,127}", second_model_id)
            or second_model_id == BASELINE_MODEL or existing.root == alternative.root):
        raise EvidenceMismatch("Groq paired development model or owner scope invalid")
    left, right = _manifest(existing.root), _manifest(alternative.root)
    if (left["sha256"] != existing.digest or right["sha256"] != alternative.digest
            or left["phase1c_pin"] != right["phase1c_pin"] or
            len(left["cases"]) != len(right["cases"])):
        raise EvidenceMismatch("Groq paired campaign identity differs")
    pairs = []
    for first, second in zip(left["cases"], right["cases"]):
        if (any(first[k] != second[k] for k in SOURCE_FIELDS) or
                first["assessment_id"] == second["assessment_id"] or
                first["cohort"] not in DEVELOPMENT_COHORTS or
                first["contract_versions"] != {**CONTRACTS, "model": BASELINE_MODEL} or
                second["contract_versions"] != {**CONTRACTS, "model": second_model_id}):
            raise EvidenceMismatch("Groq pair source, cohort or prompt/model plan differs")
        pairs.append(first["case_id"])
    # report() checks existing starts, checkpoints, source/receipts (if attached)
    # and measured wall sidecars; it never creates a start or invokes a model.
    reports = (existing.report(), alternative.report())
    arms = []
    for campaign, manifest, report in zip((existing, alternative), (left, right), reports):
        if (report.get("manifest_sha256") != campaign.digest or
                report.get("phase1c_pin") != manifest["phase1c_pin"] or
                [r["case_id"] for r in report.get("cases", ())] != pairs):
            raise EvidenceMismatch("Groq paired report differs from frozen cases")
        cases = []
        for row, frozen in zip(report["cases"], manifest["cases"]):
            if any(row.get(k) != frozen[k] for k in SOURCE_FIELDS if k != "case_family") or (
                    row.get("contract_versions") != frozen["contract_versions"]):
                raise EvidenceMismatch("Groq paired report source differs")
            cases.append({"case_id": row["case_id"], "cohort": row["cohort"],
                "status": row["status"], "failure_stage": row["failure_stage"],
                "failure_category": row["failure_category"],
                "uncertain_delivery": row["uncertain_delivery"],
                "receipt_verification": row["receipt_verification"],
                "validated_specialists": row["validated_specialists"],
                "wall_ms": report["wall_ms"].get(row["case_id"]),
                "reported_tokens": None, "cost_usd": None})
        arms.append({"declared_model": manifest["cases"][0]["contract_versions"]["model"],
            "campaign_id": manifest["campaign_id"],
            "phase2_sha": manifest["phase2_sha"],
            "manifest_sha256": campaign.digest, "counts": report["counts"],
            "cases": cases})
    return {"version": VERSION, "execution": "no_send_read_only",
        "provider_model_verified": False, "independent_campaign_authorized": False,
        "formal_accuracy": None, "phase1c_pin": left["phase1c_pin"],
        "case_ids": pairs, "arms": arms}
