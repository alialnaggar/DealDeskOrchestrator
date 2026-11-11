"""Opt-in, offline prospective campaign gate and missing-aware observation.

The callback runs the existing governed graph with offline doubles. No model,
credential, accepted answer or baseline is passed to the graph by this module.
Existing hosted runners are NOT enabled by importing this module.
"""

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from time import monotonic_ns
from typing import Callable

from .graph_state import SPECIALISTS
from .m22_registry import (_manifest, _preflight_path, _read, _digest, _write_once,
                           record_preflight, register_campaign, reconcile_campaign)
from .phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT

VERSION = "m22-prospective-offline-v1"


def _start_path(root, case_id):
    return root / (sha256(case_id.encode()).hexdigest() + ".started.json")


def _time_path(root, case_id):
    return root / (sha256(case_id.encode()).hexdigest() + ".wall.json")


@dataclass
class OfflineCampaign:
    root: Path
    digest: str  # independently retained manifest digest
    campaign_id: str
    phase2_sha: str
    adapter: object
    checkpoints: dict = field(default_factory=dict)
    timings: dict = field(default_factory=dict)

    @classmethod
    def freeze(cls, root, *, campaign_id, phase2_sha, cases, adapter):
        digest = register_campaign(root, campaign_id=campaign_id,
                                   phase2_sha=phase2_sha, cases=cases)
        return cls(root, digest, campaign_id, phase2_sha, adapter)

    def _case(self, case_id):
        manifest = _manifest(self.root)
        if (manifest["sha256"] != self.digest or
                manifest["campaign_id"] != self.campaign_id or
                manifest["phase2_sha"] != self.phase2_sha or
                manifest["phase1c_pin"] != PHASE1C_COMMIT):
            raise EvidenceMismatch("Prospective campaign identity changed")
        matches = [row for row in manifest["cases"] if row["case_id"] == case_id]
        if len(matches) != 1:
            raise EvidenceMismatch("Case not in frozen campaign")
        return matches[0]

    def preflight(self, case_id, *, status, reason=None):
        self._case(case_id)
        record_preflight(self.root, case_id=case_id, status=status, reason=reason)

    def _eligible(self, case_id):
        case = self._case(case_id)
        path = _preflight_path(self.root, case_id)
        record = _read(path)  # absent or tampered record fails before callback
        event = {"manifest_sha256": self.digest, "case_id": case_id,
                 "status": "eligible", "reason": None}
        if record != {**event, "sha256": _digest(event)}:
            raise EvidenceMismatch("Frozen eligible preflight unavailable")
        if case["contract_versions"].get("capture") != "m22-checkpoint-observation-v1":
            raise EvidenceMismatch("Capture contract not pinned")
        if not all(case["contract_versions"].get(k) for k in ("model", "prompt")):
            raise EvidenceMismatch("Model/prompt version not pinned")
        return case

    def execute_offline(self, case_id: str, *, observed_identity: dict,
                        execute: Callable[[], tuple[dict, bool]], clock=monotonic_ns):
        """One guarded graph execution. Return (state,pending) from stored checkpoint.

        The caller must use only offline model doubles. A failed/uncertain run is
        never resumed here; fresh assessment identities require a new campaign.
        """
        case = self._eligible(case_id)
        keys = ("assessment_id", "original_deal_id", "phase1c_run_id",
                "source_input_digest", "bundle_sha256", "as_of_at",
                "data_snapshot_ref", "contract_versions")
        if (type(observed_identity) is not dict or
                any(observed_identity.get(k) != case[k] for k in keys) or
                case_id in self.checkpoints or case_id in self.timings):
            raise EvidenceMismatch("Frozen source/case identity differs or already started")
        if not callable(execute):
            raise EvidenceMismatch("Offline execution callback missing")
        # Durable exclusive claim BEFORE invocation. No retry across processes,
        # including crashes before a checkpoint exists; do not infer delivery.
        _write_once(_start_path(self.root, case_id), {"manifest_sha256": self.digest,
            "case_id": case_id, "source_input_digest": case["source_input_digest"],
            "bundle_sha256": case["bundle_sha256"]})
        self.timings[case_id] = None
        started = clock()
        try:
            snapshot = execute()
            if (type(snapshot) is not tuple or len(snapshot) != 2 or
                    type(snapshot[0]) is not dict or type(snapshot[1]) is not bool):
                raise EvidenceMismatch("Stored checkpoint and pending flag required")
            self.checkpoints[case_id] = snapshot
            # Fail closed if the stored checkpoint does not match frozen case.
            reconcile_campaign(self.root, self.adapter,
                expected_manifest_sha256=self.digest, checkpoints={case_id: snapshot})
            return snapshot
        finally:
            elapsed = clock() - started
            self.timings[case_id] = (elapsed // 1_000_000 if type(elapsed) is int
                                      and elapsed >= 0 else None)
            _write_once(_time_path(self.root, case_id), {
                "manifest_sha256": self.digest, "case_id": case_id,
                "wall_ms": self.timings[case_id]})

    def report(self, *, checkpoints=None, receipt_root=None):
        rows = self.checkpoints if checkpoints is None else checkpoints
        report = reconcile_campaign(self.root, self.adapter,
            expected_manifest_sha256=self.digest, checkpoints=rows,
            receipt_root=receipt_root)
        started_without_checkpoint = []
        for row in report["cases"]:
            path = _start_path(self.root, row["case_id"])
            if path.exists():
                case = self._case(row["case_id"])
                if _read(path) != {"manifest_sha256": self.digest,
                        "case_id": row["case_id"],
                        "source_input_digest": case["source_input_digest"],
                        "bundle_sha256": case["bundle_sha256"]} or row["preflight"] != "eligible":
                    raise EvidenceMismatch("Prospective start marker differs")
                if row["case_id"] not in rows:
                    started_without_checkpoint.append(row["case_id"])
            elif row["case_id"] in rows:
                raise EvidenceMismatch("Checkpoint without prospective start marker")
        durations = {}
        for row in report["cases"]:
            case_id = row["case_id"]
            path = _time_path(self.root, case_id)
            event = _read(path) if path.exists() else None
            if event is not None and (type(event) is not dict or
                    event.get("manifest_sha256") != self.digest or
                    event.get("case_id") != case_id or
                    (event.get("wall_ms") is not None and (type(event["wall_ms"]) is not int
                        or event["wall_ms"] < 0)) or
                    not _start_path(self.root, case_id).exists()):
                raise EvidenceMismatch("Prospective wall measurement differs")
            durations[case_id] = event["wall_ms"] if event else None
        # The registry cannot infer a start without a checkpoint. The offline
        # entrypoint owns the durable marker, so expose that denominator here;
        # do not invent a provider reservation/receipt for this unknown send.
        for row in report["cases"]:
            if row["case_id"] in started_without_checkpoint:
                row["status"] = "started_without_checkpoint_unknown_send"
                row["failure_stage"] = "assessment"
                row["failure_category"] = "unknown_send"
                row["uncertain_delivery"] = True
        if started_without_checkpoint:
            report["counts"]["started_eligible"] += len(started_without_checkpoint)
            report["counts"]["started_without_checkpoint_unknown_send"] = len(
                started_without_checkpoint)
            report["counts"]["failures_by_stage_category"] = sorted(
                report["counts"]["failures_by_stage_category"] +
                [(cid, "assessment", "unknown_send")
                 for cid in started_without_checkpoint])
        started_cohorts = {row["case_id"]: row["cohort"] for row in report["cases"]
                           if row["case_id"] in started_without_checkpoint}
        for cohort, counts in report["by_cohort"].items():
            missing = sum(value == cohort for value in started_cohorts.values())
            if missing:
                counts["started_eligible"] += missing
                counts["started_without_checkpoint_unknown_send"] = missing
                counts["failures_by_stage_category"] = sorted(
                    counts["failures_by_stage_category"] +
                    [(cid, "assessment", "unknown_send")
                     for cid in started_without_checkpoint
                     if started_cohorts[cid] == cohort])
        return {**report, "enablement_version": VERSION,
            "started_without_checkpoint_unknown_send": started_without_checkpoint,
            "wall_ms": durations}


def timing_observation(capture: dict, *, wall_ms=None, stages=None,
                       waits=None, checkpoint_ms=None):
    """Measured intervals only; no inference from incomplete attempt usage.

    `stages` and `waits` are caller-supplied measured ms, not timestamp deltas
    derived from stored checkpoints. Missing entries are explicit None.
    """
    def checked(value):
        if value is not None and (type(value) is not int or value < 0):
            raise EvidenceMismatch("Timing must be measured nonnegative milliseconds")
        return value
    if type(capture) is not dict or type(capture.get("attempts")) is not list:
        raise EvidenceMismatch("Checkpoint observation required")
    stages, waits = stages or {}, waits or {}
    if type(stages) is not dict or type(waits) is not dict:
        raise EvidenceMismatch("Measured interval maps required")
    if set(stages) - (set(SPECIALISTS) | {"original_graph", "review",
            "configuration_pricing", "credit_policy_routing"}) or set(waits) - {
            "rate", "local_quota"}:
        raise EvidenceMismatch("Timing interval category unavailable")
    attempts = []
    for row in capture["attempts"]:
        if type(row) is not dict or row.get("status") not in (
                "reserved", "returned", "completed", "failed"):
            raise EvidenceMismatch("Attempt measurement unavailable")
        attempts.append({"specialist": row.get("specialist"),
            "stage": row.get("stage"), "status": row["status"],
            "provider_elapsed_ms": checked(row.get("elapsed_ms")),
            "provider_reported_tokens": row.get("tokens")})
    return {"version": "m22-timing-v1", "assessment_id": capture.get("assessment_id"),
        "wall_ms": checked(wall_ms), "stages_ms": {
            k: checked(stages.get(k)) for k in (*SPECIALISTS, "original_graph", "review",
                "configuration_pricing", "credit_policy_routing")},
        "waits_ms": {k: checked(v) for k,v in waits.items()},
        "checkpoint_ms": checked(checkpoint_ms), "attempts": attempts,
        "orchestration_overhead_ms": None, "total_tokens": None,
        "cost_usd": None}


@dataclass
class MeasuredIntervals:
    """Explicit sequential spans; never extrapolate missing graph/provider times."""
    stages: dict = field(default_factory=dict)
    waits: dict = field(default_factory=dict)

    def measure(self, category: str, action: Callable, *, waiting=False,
                clock=monotonic_ns):
        allowed = {"rate", "local_quota"} if waiting else set(SPECIALISTS) | {
            "original_graph", "review", "configuration_pricing", "credit_policy_routing"}
        target = self.waits if waiting else self.stages
        if category not in allowed or category in target or not callable(action):
            raise EvidenceMismatch("Measured span category or duplicate differs")
        target[category] = None  # started; no replay if action fails
        start = clock()
        try:
            return action()
        finally:
            elapsed = clock() - start
            if type(elapsed) is int and elapsed >= 0:
                target[category] = elapsed // 1_000_000
