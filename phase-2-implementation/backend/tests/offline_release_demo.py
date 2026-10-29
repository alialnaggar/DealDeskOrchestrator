"""Read-only operator projection of one executed Week 4 offline cohort.

Only already captured, source-checked graph outputs are projected. There is
no model, SQL, rule recomputation, answer sheet or approval API here.
"""

from hashlib import sha256
import json

from dealdesk_phase2.graph_state import SPECIALISTS
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from run_week4_development import VERSION as EVALUATION_VERSION, summarize


VERSION = "offline-release-demo-v1"
SHOW = ("M18-D-B01", "M18-D-B05", "M18-D-N03")
REVIEW_ACTION = "Human review required; no approval, reservation or delivery promise"


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def project(data):
    """Fail closed on a stale/tampered evaluation or cross-subject candidate."""
    stable = {k: v for k, v in data.items() if k not in (
        "stable_result_sha256", "timing_diagnostics", "disposable_setup")}
    if (data.get("version") != EVALUATION_VERSION
            or sha256(_canonical(stable)).hexdigest() != data.get("stable_result_sha256")
            or data.get("provider_requests") != 0
            or data.get("independent_answers_accepted") != 0
            or len(data.get("scenarios", ())) != 9
            or summarize(data["scenarios"], data["isolated_candidate"]) != data["summary"]):
        raise EvidenceMismatch("Release demo requires intact offline development results")
    by_id = {s["case_id"]: s for s in data["scenarios"]}
    if set(SHOW) - set(by_id):
        raise EvidenceMismatch("Release demo missing original or adverse control")
    candidate = data["isolated_candidate"]
    original = by_id["M18-D-B01"]
    if (candidate["case_id"] != original["case_id"]
            or candidate["assessment_id"] == original["assessment_id"]
            or candidate["bundle_sha256"] != original["bundle_sha256"]
            or candidate["source_input_digest"] != original["source_input_digest"]
            or candidate["fixed_supply_status"] != "supply_supported_unreserved"
            or candidate["fixed_business_status"] != "needs_revision"
            or candidate["customer_acceptance"] != "pending"
            or candidate["human_approval"] != "not_granted_by_system"
            or set(candidate["fixed_rechecks"]) != set(SPECIALISTS)
            or not candidate["citations_returned"]
            or not candidate["same_schedule_as_fixed_discovery"]):
        raise EvidenceMismatch("Release demo cannot claim an unchecked candidate")
    shown = []
    for case_id in SHOW:
        row = by_id[case_id]
        if (row.get("reviewer_action") != REVIEW_ACTION
                or row.get("human_approval") != "not_granted_by_system"
                or row["candidate_status"] != "not_started"
                or set(row["offline_ai"]) != set(SPECIALISTS)
                or set(row["deterministic_baseline"]["specialists"]) != set(SPECIALISTS)):
            raise EvidenceMismatch("Release demo original handoff changed")
        shown.append({"deal_id": case_id, "assessment_id": row["assessment_id"],
            "phase1c_run_id": row["phase1c_run_id"],
            "bundle_sha256": row["bundle_sha256"],
            "source_input_digest": row["source_input_digest"],
            "fixed_decision_sha256": row["fixed_decision_sha256"],
            "fixed_review_status": row["deterministic_baseline"]["review_status"],
            "fixed_specialists": row["deterministic_baseline"]["specialists"],
            "offline_ai": {name: {"execution": result["execution"],
                "contribution_kind": result.get("contribution_kind"),
                "validated_claims": result["validated_claims"],
                "provider": result.get("provider", "offline_scripted_double")}
                for name, result in row["offline_ai"].items()},
            "trace": row["trace"], "reviewer_action": row["reviewer_action"],
            "candidate_status": row["candidate_status"]})
    if (set(shown[0]["offline_ai"][name]["execution"] for name in SPECIALISTS)
            != {"completed"}
            or shown[0]["offline_ai"]["fulfillment"]["contribution_kind"] != "abstention"
            or shown[1]["offline_ai"]["credit"]["execution"] != "error"
            or shown[1]["offline_ai"]["policy"]["execution"] != "abstained"
            or shown[2]["offline_ai"]["fulfillment"]["execution"] != "skipped"):
        raise EvidenceMismatch("Release demo specialist prerequisite or fault scenario changed")
    return {"version": VERSION, "phase1c_pin": data["phase1c_pin"],
        "contracts": data["contracts"], "source_hashes": data["source_hashes"],
        "evaluation_stable_sha256": data["stable_result_sha256"],
        "model_class": "scripted_offline_doubles_only", "scenarios": shown,
        "separate_fulfillment_candidate": {key: candidate[key] for key in (
            "assessment_id", "candidate_id", "case_id", "bundle_sha256",
            "source_input_digest", "proposal_source", "candidate_status",
            "fixed_supply_status", "fixed_business_status", "fixed_rechecks",
            "citations_returned", "same_schedule_as_fixed_discovery",
            "customer_acceptance", "human_approval")},
        "approval_authority": "human_only", "hosted_model_reliability": "unmeasured",
        "independent_answers_accepted": 0}


def markdown(demo):
    lines = ["# Offline release-candidate demonstration", "",
        "**Engineering demonstration only:** pinned synthetic evidence and scripted "
        "offline model substitutes; no real LLM reasoning, approval or delivery promise. "
        "The six fixed mappings are not six AI findings.", "",
        "| Deal | Fixed original | Fulfillment AI | Configuration | Pricing | Credit | Policy | Routing |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in demo["scenarios"]:
        ai = row["offline_ai"]
        lines.append("| " + row["deal_id"] + " | " + row["fixed_review_status"]
            + " | " + " / ".join([ai["fulfillment"]["execution"],
                str(ai["fulfillment"]["contribution_kind"])])
            + " | " + " | ".join(ai[name]["execution"] for name in (
                "configuration", "pricing", "credit", "policy", "approval_routing")) + " |")
    b01 = demo["scenarios"][0]
    lines += ["", "## Follow B01 end to end", "",
        "- **Submitted deal and evidence:** `" + b01["deal_id"] + "`, pinned Phase 1C run `"
        + b01["phase1c_run_id"] + "`, frozen bundle `" + b01["bundle_sha256"]
        + "`. Read-only dated evidence and source digests are in the JSON.",
        "- **Fixed rules:** original `" + b01["fixed_review_status"]
        + "`; all six deterministic specialist mappings completed. The approval "
        "route is withheld; no salesperson promise is authorized.",
        "- **Scripted AI:** all six investigations completed; Fulfillment *abstained* "
        "rather than proposing a candidate in this original-only workflow. "
        "The five other specialists each recorded an evidence-checked citation. "
        "See `offline_ai` and `trace` in the JSON for exact references and order.",
        "- **Final handoff:** `" + b01["reviewer_action"] + "`.", "",
        "B05 injects an unsupported Credit citation (rejected) and a Policy "
        "abstention; N03 has insufficient/stale Fulfillment evidence and a Policy "
        "error. Neither is reported as a validated AI finding. Other fixed "
        "specialist results remain isolated.", "",
        "## Separate supported alternative", "",
        "A **different assessment thread** on the same frozen B01 deal uses a "
        "predeclared scripted two-slice Fulfillment hypothesis. It is not a "
        "six-AI candidate continuation. The pinned verifier rechecked all six "
        "fixed candidate responsibilities: `" + demo["separate_fulfillment_candidate"][
            "fixed_supply_status"] + "` supply, `" + demo["separate_fulfillment_candidate"][
            "fixed_business_status"] + "` business outcome, customer acceptance `"
        + demo["separate_fulfillment_candidate"]["customer_acceptance"]
        + "`. Source citations were returned by an authorized tool. The schedule "
        "matches deterministic-only discovery, so no AI advantage is shown.", "",
        "## Reproduce and operator checks", "",
        "1. Follow the [Week 4 one-command setup and evaluation](week4-offline-development.md#run) "
        "from this repository's root with the locked Python environment and "
        "already-running `/tmp/opencode` test PostgreSQL. It writes fresh "
        "evaluation JSON/Markdown and `dealdesk-offline-demo.json`/`.md` "
        "beside the JSON path; it never connects to Groq or a non-disposable DB.",
        "2. Check `phase1c_pin`, bundle and source hashes, and `evaluation_stable_sha256`; "
        "the B01 original and candidate must have different assessment IDs but "
        "the same bundle and source digest.",
        "3. Check B05 rejected/abstained and N03 skipped/error outcomes, "
        "candidate `fixed_rechecks` (six), pending customer acceptance and the "
        "human-only reviewer action. A rerun on one thread tests replay, not a new sample.",
        "4. If any source or fixed result differs, stop rather than treating this "
        "sample report as an answer key. No 36-case independent answers have "
        "been accepted. Hosted-model compatibility, semantic utility and "
        "private CI remain unverified.", ""]
    return "\n".join(lines)
