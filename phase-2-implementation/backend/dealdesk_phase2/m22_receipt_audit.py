"""Bounded, read-only comparison of stored attempts to existing send receipts.

This does not resume a graph or prove that a provider received a request.
Only caller-approved owner directories can be inspected.
"""

import os
from hashlib import sha256
from pathlib import Path

from .hybrid_contracts import HybridContractError
from .hybrid_pack import _canonical
from .hybrid_send_reservation import attempt_path, verify_receipt
from .m22_capture import capture_m22
from .phase1c_adapter import EvidenceMismatch


VERSION = "m22-receipt-reconciliation-v1"
M21 = ("credit", "policy", "approval_routing")


def _owner(record, path_key, device_key, inode_key, allowed_root):
    if (type(record) is not dict or type(record.get(path_key)) is not str or
            not record[path_key].startswith("/") or not isinstance(allowed_root, Path) or
            not allowed_root.is_absolute() or allowed_root.is_symlink() or
            not allowed_root.is_dir() or allowed_root.stat().st_mode & 0o077):
        raise EvidenceMismatch("M2.2 receipt owner boundary unavailable")
    path = Path(record[path_key])
    # Reject untrusted paths before touching their metadata; a checkpoint must
    # not steer this read-only audit into unrelated host directories.
    if (".." in path.parts or not path.is_relative_to(allowed_root) or
            allowed_root.resolve() != allowed_root):
        raise EvidenceMismatch("M2.2 receipt owner outside approved root")
    if (path.is_symlink() or not path.is_dir() or
            path.resolve() != path or not path.is_relative_to(allowed_root.resolve()) or
            path.stat().st_uid != os.geteuid() or
            path.stat().st_mode & 0o077 or
            path.stat().st_dev != record.get(device_key) or
            path.stat().st_ino != record.get(inode_key)):
        raise EvidenceMismatch("M2.2 receipt owner identity changed")
    return path


def _check(path, assessment, start_digest, stage, ordinal, request_digest):
    if (type(request_digest) is not str or len(request_digest) != 64 or
            any(x not in "0123456789abcdef" for x in request_digest)):
        raise EvidenceMismatch("M2.2 receipt request digest unavailable")
    try:
        file = attempt_path(path, assessment_id=assessment, start_digest=start_digest,
                            stage=stage, ordinal=ordinal)
        return verify_receipt(file, start_digest=start_digest, stage=stage,
                              ordinal=ordinal, request_digest=request_digest)
    except (OSError, HybridContractError, ValueError):
        raise EvidenceMismatch("M2.2 receipt missing, invalid or mismatched") from None


def reconcile_receipts(state, adapter, *, allowed_root: Path):
    """Compare receipt-bearing hosted attempts; never reads credentials or sends.

    `False` proves only a valid reserved/failed marker, not provider non-delivery.
    Unreceipted Fulfillment/M2.0 transports remain explicitly unavailable.
    """
    observation = capture_m22(state, adapter)
    assessment = observation["assessment_id"]
    checked = []
    m21 = state.get("m21_model_attempts", [])
    owner = state.get("m21_hosted_owner")
    if owner is not None:
        directory = _owner(owner, "path", "device", "inode", allowed_root)
        digest = owner.get("manifest_sha256")
        if type(digest) is not str or len(digest) != 64:
            raise EvidenceMismatch("M2.2 M2.1 manifest digest unavailable")
        if any(x.get("provider") != "groq" for x in m21):
            raise EvidenceMismatch("M2.2 mixed M2.1 receipt provenance")
        for row in m21:
            if row["status"] != "reserved":
                continue
            specialist, ordinal = row.get("specialist"), row.get("ordinal")
            if specialist not in M21 or type(ordinal) is not int or ordinal not in (0, 1):
                raise EvidenceMismatch("M2.2 M2.1 receipt stage unavailable")
            wire_ordinal = M21.index(specialist) * 2 + ordinal
            returned = _check(directory, assessment, digest, "decision", wire_ordinal,
                              row.get("request_sha256"))
            matching = [x for x in m21 if x.get("specialist") == specialist and
                x.get("ordinal") == ordinal and x.get("status") == "returned"]
            if bool(matching) != returned:
                raise EvidenceMismatch("M2.2 M2.1 checkpoint/receipt disagree")
            checked.append({"family": "m21", "specialist": specialist,
                            "stage": "decision", "ordinal": wire_ordinal,
                            "receipt": "returned" if returned else "unreturned_or_uncertain"})
    elif any(x.get("provider") == "groq" for x in m21):
        raise EvidenceMismatch("M2.2 hosted M2.1 owner missing")

    typed = state.get("typed_final_attempts", [])
    protocol = state.get("typed_final_protocol")
    hosted = state.get("typed_final_hosted_start")
    if hosted is not None:
        directory = _owner(hosted, "owner_path", "owner_device", "owner_inode",
                           allowed_root)
        manifest_digest = hosted.get("manifest_sha256")
        if type(manifest_digest) is not str or len(manifest_digest) != 64:
            raise EvidenceMismatch("M2.2 typed manifest digest unavailable")
        configuration = state.get("m20_model_attempts", [])
        if any(x.get("specialist") != "configuration" or x.get("provider") != "groq"
               for x in configuration):
            raise EvidenceMismatch("M2.2 typed configuration attempts changed")
        for row in configuration:
            if row["status"] != "reserved":
                continue
            ordinal = row.get("ordinal")
            if type(ordinal) is not int or ordinal not in (0, 1):
                raise EvidenceMismatch("M2.2 typed configuration ordinal unavailable")
            returned = _check(directory, assessment, manifest_digest,
                              "typed_configuration", ordinal, row.get("request_sha256"))
            matching = [x for x in configuration if x.get("ordinal") == ordinal and
                        x.get("status") == "returned"]
            if bool(matching) != returned:
                raise EvidenceMismatch("M2.2 typed configuration checkpoint/receipt disagree")
            checked.append({"family": "m20", "specialist": "configuration",
                            "stage": "typed_configuration", "ordinal": ordinal,
                            "receipt": "returned" if returned else "unreturned_or_uncertain"})
        if protocol is None:
            if typed:
                raise EvidenceMismatch("M2.2 typed attempts lack a protocol")
        else:
            if type(protocol) is not dict or protocol.get("owner_directory") != str(
                    directory) or protocol.get("owner_device") != hosted["owner_device"] or (
                    protocol.get("owner_inode") != hosted["owner_inode"]):
                raise EvidenceMismatch("M2.2 typed protocol owner changed")
            digest = sha256(_canonical(protocol).encode()).hexdigest()
            for row in typed:
                if row["status"] != "reserved":
                    continue
                stage, ordinal = row.get("stage"), row.get("ordinal")
                if stage not in ("typed_inspection", "typed_final") or type(ordinal) is not int or ordinal not in (0, 1):
                    raise EvidenceMismatch("M2.2 typed receipt stage unavailable")
                returned = _check(directory, assessment, digest, stage, ordinal,
                                  row.get("request_sha256"))
                matching = [x for x in typed if x.get("stage") == stage and
                    x.get("ordinal") == ordinal and x.get("status") == "returned"]
                if bool(matching) != returned:
                    raise EvidenceMismatch("M2.2 typed checkpoint/receipt disagree")
                checked.append({"family": "typed", "specialist": protocol.get("specialist"),
                                "stage": stage, "ordinal": ordinal,
                                "receipt": "returned" if returned else "unreturned_or_uncertain"})
    elif typed and protocol and protocol.get("version", "").endswith("hosted-v1"):
        raise EvidenceMismatch("M2.2 hosted typed owner missing")

    return {"version": VERSION, "assessment_id": assessment,
            "bundle_sha256": observation["bundle_sha256"],
            "receipt_bearing_attempts": checked,
            "receipt_verification": "verified_bounded_receipts" if checked else
                "no_receipt_bearing_attempts",
            "other_transports": "not_verified_by_this_projection",
            "provider_delivery_of_unreturned": None}
