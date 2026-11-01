"""Pre-execution campaign freeze and model-blind WP2 denominator reconciliation.

The registry is an offline, owner-local artifact, not a transport or answer key.
The caller MUST freeze it before invoking any model. Preflight outcomes are
separate write-once records; reconciliation never writes or resumes a send.
"""

from hashlib import sha256
import json
import os
from pathlib import Path

from .graph_state import SPECIALISTS
from .m22_capture import capture_m22
from .m22_receipt_audit import reconcile_receipts
from .phase1c_adapter import EvidenceMismatch, PHASE1C_COMMIT

VERSION = "m22-scheduled-registry-v1"
COHORTS = {"pinned_development", "phase1c_100_diagnostic", "phase1c_36_held_out",
           "supplemental_control", "fault_injection"}
FIELDS = {"case_id", "assessment_id", "original_deal_id", "phase1c_run_id",
          "cohort", "case_family", "source_input_digest", "bundle_sha256",
          "as_of_at", "data_snapshot_ref", "contract_versions"}


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return sha256(_canonical(value).encode()).hexdigest()


def _directory(root):
    if (not isinstance(root, Path) or not root.is_absolute() or root.is_symlink()
            or not root.is_dir() or root.resolve() != root or
            root.stat().st_uid != os.geteuid() or root.stat().st_mode & 0o077):
        raise EvidenceMismatch("M2.2 registry owner boundary unavailable")


def _write_once(path, value):
    data = (_canonical(value) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        while data:
            data = data[os.write(fd, data):]
        os.fsync(fd)
    finally:
        os.close(fd)
    parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(parent)
    finally:
        os.close(parent)


def _read(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        stat = os.fstat(fd)
        if (stat.st_nlink != 1 or stat.st_uid != os.geteuid() or
                stat.st_mode & 0o077 or stat.st_size > 262144):
            raise EvidenceMismatch("M2.2 registry file changed")
        with os.fdopen(os.dup(fd), "r", encoding="utf-8") as stream:
            return json.load(stream)
    finally:
        os.close(fd)


def _case(row):
    if (type(row) is not dict or set(row) != FIELDS or
            any(type(row[k]) is not str or not row[k] or len(row[k]) > 256
                for k in FIELDS - {"contract_versions"}) or
            row["cohort"] not in COHORTS or
            type(row["contract_versions"]) is not dict or
            not row["contract_versions"] or
            any(type(k) is not str or not k or type(v) is not str or not v
                for k, v in row["contract_versions"].items())):
        raise EvidenceMismatch("M2.2 scheduled case identity invalid")


def register_campaign(root, *, campaign_id, phase2_sha, cases):
    """Create a single immutable manifest before any preflight/model execution."""
    _directory(root)
    if (type(campaign_id) is not str or not campaign_id or len(campaign_id) > 128
            or type(phase2_sha) is not str or len(phase2_sha) != 40
            or type(cases) is not list or not cases):
        raise EvidenceMismatch("M2.2 campaign identity invalid")
    for row in cases:
        _case(row)
    if (len({row["case_id"] for row in cases}) != len(cases) or
            len({row["assessment_id"] for row in cases}) != len(cases)):
        raise EvidenceMismatch("M2.2 duplicate scheduled case or assessment")
    manifest = {"version": VERSION, "campaign_id": campaign_id,
                "phase1c_pin": PHASE1C_COMMIT, "phase2_sha": phase2_sha,
                "cases": cases}
    _write_once(root / "campaign.json", {**manifest, "sha256": _digest(manifest)})
    return _digest(manifest)


def _manifest(root):
    _directory(root)
    stored = _read(root / "campaign.json")
    if type(stored) is not dict:
        raise EvidenceMismatch("M2.2 campaign manifest invalid")
    manifest = {k: v for k, v in stored.items() if k != "sha256"}
    if (set(stored) != {"version", "campaign_id", "phase1c_pin", "phase2_sha",
                           "cases", "sha256"} or stored["version"] != VERSION or
            stored["phase1c_pin"] != PHASE1C_COMMIT or
            stored["sha256"] != _digest(manifest) or
            type(stored["cases"]) is not list or not stored["cases"] or
            len({r["case_id"] for r in stored["cases"]}) != len(stored["cases"]) or
            len({r["assessment_id"] for r in stored["cases"]}) != len(stored["cases"])):
        raise EvidenceMismatch("M2.2 campaign membership changed")
    for row in stored["cases"]:
        _case(row)
    return stored


def _preflight_path(root, case_id):
    return root / (sha256(case_id.encode()).hexdigest() + ".preflight.json")


def record_preflight(root, *, case_id, status, reason=None):
    """One outcome per frozen case; do not overwrite an adverse outcome."""
    manifest = _manifest(root)
    if (case_id not in {r["case_id"] for r in manifest["cases"]} or
            status not in ("eligible", "ineligible", "source_preflight_failed") or
            (status == "eligible" and reason is not None) or
            (status != "eligible" and (type(reason) is not str or not reason))):
        raise EvidenceMismatch("M2.2 preflight outcome invalid")
    event = {"manifest_sha256": manifest["sha256"], "case_id": case_id,
             "status": status, "reason": reason}
    _write_once(_preflight_path(root, case_id), {**event, "sha256": _digest(event)})


def reconcile_campaign(root, adapter, *, expected_manifest_sha256,
                       checkpoints, receipt_root=None):
    """Read-only accounting. checkpoints maps case IDs to stored state or (state,pending).

    Missing checkpoint is not an eligible completion; missing preflight is not
    an eligible case. Receipt verification is optional and never implies delivery.
    """
    manifest = _manifest(root)
    if manifest["sha256"] != expected_manifest_sha256:
        raise EvidenceMismatch("M2.2 campaign changed since pre-execution freeze")
    if type(checkpoints) is not dict or set(checkpoints) - {
            row["case_id"] for row in manifest["cases"]}:
        raise EvidenceMismatch("M2.2 unregistered checkpoint")
    rows = []
    for case in manifest["cases"]:
        case_id = case["case_id"]
        path = _preflight_path(root, case_id)
        record = _read(path) if os.path.lexists(path) else None
        if record is not None and (type(record) is not dict or record != {
                "manifest_sha256": manifest["sha256"], "case_id": case_id,
                "status": record.get("status"), "reason": record.get("reason"),
                "sha256": _digest({"manifest_sha256": manifest["sha256"],
                    "case_id": case_id, "status": record.get("status"),
                    "reason": record.get("reason")})}
                or record["status"] not in ("eligible", "ineligible", "source_preflight_failed")
                or record["status"] == "eligible" and record["reason"] is not None
                or record["status"] != "eligible" and not record["reason"]):
            raise EvidenceMismatch("M2.2 preflight record differs")
        snapshot = checkpoints.get(case_id)
        if snapshot is not None and (record is None or record["status"] != "eligible"):
            raise EvidenceMismatch("M2.2 checkpoint without eligible preflight")
        observation = None
        receipts = None
        if snapshot is not None:
            if isinstance(snapshot, tuple) and len(snapshot) == 2:
                state, pending = snapshot
            else:
                state, pending = snapshot, False
            observation = capture_m22(state, adapter, checkpoint_pending=pending)
            if (observation["version"] != case["contract_versions"]["capture"] or
                    observation["assessment_id"] != case["assessment_id"] or
                    observation["original_deal_id"] != case["original_deal_id"] or
                    observation["phase1c_run_id"] != case["phase1c_run_id"] or
                    observation["bundle_sha256"] != case["bundle_sha256"] or
                    observation["source_input_digest"] != case["source_input_digest"] or
                    observation["as_of_at"] != case["as_of_at"] or
                    observation["data_snapshot_ref"] != case["data_snapshot_ref"] or
                    observation["phase1c_pin"] != manifest["phase1c_pin"]):
                raise EvidenceMismatch("M2.2 checkpoint differs from scheduled original")
            if receipt_root is not None:
                receipts = reconcile_receipts(state, adapter, allowed_root=receipt_root)
                if (receipts["assessment_id"] != observation["assessment_id"] or
                        receipts["bundle_sha256"] != observation["bundle_sha256"]):
                    raise EvidenceMismatch("M2.2 receipt observation identity differs")
        attempts = observation["attempts"] if observation else []
        reserved = [a for a in attempts if a["status"] == "reserved"]
        returned = [a for a in attempts if a["status"] in ("returned", "completed")]
        results = observation["ai_original"] if observation else {}
        validated = [name for name in SPECIALISTS if results.get(name) and
                     results[name]["execution"] in ("completed", "abstained")]
        unresolved = len(reserved) > len(returned) + sum(a["status"] == "failed" for a in attempts)
        if observation and observation["evaluation_status"] == "completed":
            status = "completed"
        elif unresolved:
            status = "reserved_unreturned"
        elif observation and not reserved:
            status = ("no_send_stopped" if type(state) is dict and state.get("stop_reason")
                      or any(r.get("execution") == "error" for r in results.values() if r)
                      else "no_send_incomplete")
        elif observation:
            status = "attempted_incomplete"
        elif record is None:
            status = "scheduled_unobserved"
        elif record["status"] == "eligible":
            status = "eligible_not_executed"
        else:
            status = record["status"]
        errors = {name: results[name]["reason"] for name in SPECIALISTS
                  if results.get(name) and results[name]["execution"] == "error"}
        failure_stage = (observation["failure_stage"] if observation else None)
        if status in ("ineligible", "source_preflight_failed"):
            failure_stage = "preflight"
        elif status in ("reserved_unreturned", "attempted_incomplete") and not failure_stage:
            failure_stage = reserved[-1]["specialist"] if reserved else "assessment"
        elif status == "no_send_stopped" and not failure_stage:
            failure_stage = "before_send"
        failure_category = (record["reason"] if status in (
            "ineligible", "source_preflight_failed") else errors or
            ({"provider_error_codes": [a["error_code"] for a in attempts
                if a.get("error_code")]} if any(a.get("error_code") for a in attempts)
             else None) or
            ("uncertain_send" if status == "reserved_unreturned" else
             "no_send_stop" if status == "no_send_stopped" else
             "incomplete" if status == "attempted_incomplete" else None))
        rows.append({"case_id": case_id, "assessment_id": case["assessment_id"],
            "original_deal_id": case["original_deal_id"],
            "phase1c_run_id": case["phase1c_run_id"],
            "bundle_sha256": case["bundle_sha256"],
            "source_input_digest": case["source_input_digest"],
            "as_of_at": case["as_of_at"],
            "data_snapshot_ref": case["data_snapshot_ref"],
            "contract_versions": case["contract_versions"],
            "cohort": case["cohort"], "preflight": record["status"] if record else None,
            "status": status, "failure_stage": failure_stage,
            "failure_category": failure_category,
            "provider_send_reservations": len(reserved), "returned_responses": len(returned),
            "validated_specialists": validated,
            "receipt_verification": receipts["receipt_verification"] if receipts else "not_checked",
            "uncertain_delivery": unresolved})
    def counts(rows):
        return {
                "scheduled": len(rows),
                "eligible": sum(r["preflight"] == "eligible" for r in rows),
                "started_eligible": sum(r["preflight"] == "eligible" and
                                        r["status"] != "eligible_not_executed" for r in rows),
                "preflight_rejected": sum(r["status"] in (
                    "ineligible", "source_preflight_failed") for r in rows),
                "no_send_stopped": sum(r["status"] == "no_send_stopped" for r in rows),
                "reserved_unreturned_cases": sum(r["status"] == "reserved_unreturned"
                                                 for r in rows),
                "returned_rejected_cases": sum(r["status"] == "attempted_incomplete" and
                    r["returned_responses"] > 0 and not r["validated_specialists"] for r in rows),
                "attempted_cases": sum(r["provider_send_reservations"] > 0 for r in rows),
                "provider_send_reservations": sum(r["provider_send_reservations"] for r in rows),
                "returned_responses": sum(r["returned_responses"] for r in rows),
                "validated_specialist_outputs": sum(len(r["validated_specialists"]) for r in rows),
                "completed": sum(r["status"] == "completed" for r in rows),
                "failed_or_incomplete": sum(r["status"] != "completed" for r in rows),
                "failures_by_stage_category": sorted((r["case_id"], r["failure_stage"],
                    r["failure_category"]) for r in rows if r["failure_stage"] is not None)}
    return {"version": VERSION, "campaign_id": manifest["campaign_id"],
            "manifest_sha256": manifest["sha256"], "phase1c_pin": manifest["phase1c_pin"],
            "cases": rows, "counts": counts(rows),
            "by_cohort": {cohort: counts([r for r in rows if r["cohort"] == cohort])
                          for cohort in sorted({r["cohort"] for r in rows})}}
