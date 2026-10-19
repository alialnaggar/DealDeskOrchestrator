"""Read-only adapter to an exact, separate Phase 1C Git checkout.

The caller provides fresh PostgreSQL connections. Every read uses its own
REPEATABLE READ READ ONLY transaction; candidate and original are compared
within the same transaction. This module never writes business rows.
"""

from dataclasses import dataclass
import importlib
from pathlib import Path
import subprocess
import sys
from typing import Callable
from uuid import UUID

from .contracts import PHASE1C_COMMIT, RunContextV1
from .evidence_bundle import seal, unseal


class EvidenceMismatch(ValueError):
    """A reread does not match the previously sealed assessment context."""


@dataclass(frozen=True)
class PinnedBundleV1:
    context: RunContextV1
    serialized: str
    size_bytes: int

    def decode(self) -> dict:
        return unseal(self.serialized, self.context.bundle_sha256)


def _git(checkout: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(checkout), *args],
                            check=True, capture_output=True, text=True)
    return result.stdout.strip()


class Phase1CAdapter:
    def __init__(self, checkout: Path):
        self.checkout = checkout.resolve(strict=True)
        if _git(self.checkout, "rev-parse", "HEAD") != PHASE1C_COMMIT:
            raise ValueError("Phase 1C checkout is not at the pinned commit")
        # Fixture imports create untracked __pycache__ files. Refuse changes
        # to tracked implementation files while allowing those generated caches.
        if _git(self.checkout, "status", "--porcelain", "--untracked-files=no", "--",
                "phase-1c-data/implementation"):
            raise ValueError("Pinned Phase 1C tracked implementation has local changes")
        implementation = (self.checkout / "phase-1c-data" / "implementation").resolve(strict=True)
        if str(implementation) not in sys.path:
            sys.path.insert(0, str(implementation))
        modules = {}
        for name in ("phase1c_reader", "phase1c_candidate", "phase1c_deal_decision"):
            module = importlib.import_module(name)
            if not Path(module.__file__).resolve().is_relative_to(implementation):
                raise ValueError(f"Module {name} came from another Phase 1C checkout")
            modules[name] = module
        self.reader = modules["phase1c_reader"]
        self.candidate = modules["phase1c_candidate"]
        self.decision = modules["phase1c_deal_decision"]

    def _context(self, bundle: dict, assessment_id: str) -> PinnedBundleV1:
        run, deal = bundle["run"], bundle["deal"]
        if str(run["deal_id"]) != str(deal["deal_id"]):
            raise EvidenceMismatch("Reader run and original deal differ")
        raw, bundle_hash, size = seal(bundle)
        context = RunContextV1(
            assessment_id=assessment_id, phase1c_run_id=UUID(str(run["run_id"])),
            original_deal_id=str(deal["deal_id"]), submission_ref=str(deal["deal_id"]),
            as_of_at=run["as_of_at"], data_snapshot_ref=str(run["data_snapshot_ref"]),
            catalog_version=str(run["catalog_version_used"]),
            policy_set_code=str(run["applied_policy_set_code"]),
            config_hash=str(run["config_hash"]),
            source_input_digest=self.candidate.reader_input_digest(bundle),
            bundle_sha256=bundle_hash)
        return PinnedBundleV1(context, raw, size)

    def _read(self, connect: Callable, run_id: UUID, candidate=None) -> dict:
        # Used only inside the transaction established by read_original or
        # verify_candidate. Kept separate to make the write boundary obvious.
        return self.reader.read_run(connect, run_id, commercial_rule_mode="compiled",
                                    candidate=candidate)

    def read_original(self, connection_factory: Callable, run_id: UUID,
                      assessment_id: str) -> PinnedBundleV1:
        with connection_factory() as conn:
            if conn.autocommit:
                raise ValueError("Read-only transaction requires autocommit disabled")
            with conn.transaction():
                conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                bundle = self._read(conn, run_id)
                pinned = self._context(bundle, assessment_id)
                if pinned.context.phase1c_run_id != run_id:
                    raise EvidenceMismatch("Reader returned a different run")
                return pinned

    def fixed_original_decision(self, pinned: PinnedBundleV1) -> dict:
        bundle = self.validate_pinned_context(pinned)
        return self.decision.assemble_deal_decision(bundle)

    def validate_pinned_context(self, pinned: PinnedBundleV1) -> dict:
        """Check the pinned reader identity without querying mutable business rows."""
        bundle = pinned.decode()
        context = self._context(bundle, pinned.context.assessment_id).context
        if context != pinned.context:
            raise EvidenceMismatch("Sealed reader source or run identity differs")
        return bundle

    def verify_candidate(self, connection_factory: Callable, pinned: PinnedBundleV1,
                         proposed_candidate) -> tuple[dict, dict]:
        context = pinned.context
        if (str(proposed_candidate.parent_run_id) != str(context.phase1c_run_id) or
                proposed_candidate.parent_deal_id != context.original_deal_id):
            raise EvidenceMismatch("Candidate parent identity differs")
        # Check the serialized source before touching the database again.
        sealed = pinned.decode()
        if self.candidate.reader_input_digest(sealed) != context.source_input_digest:
            raise EvidenceMismatch("Sealed source digest differs")
        with connection_factory() as conn:
            if conn.autocommit:
                raise ValueError("Read-only transaction requires autocommit disabled")
            with conn.transaction():
                conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                original = self._read(conn, context.phase1c_run_id)
                reread = self._context(original, context.assessment_id)
                if (reread.context != context or reread.serialized != pinned.serialized):
                    raise EvidenceMismatch("Original reader context or selected evidence changed")
                checked = self._read(conn, context.phase1c_run_id, proposed_candidate)
                self.candidate.verify_run_correlation(proposed_candidate, original, checked)
                if (checked["candidate_trace"]["source_input_digest"] !=
                        context.source_input_digest):
                    raise EvidenceMismatch("Candidate source digest differs")
                return checked, self.decision.assemble_deal_decision(checked)
