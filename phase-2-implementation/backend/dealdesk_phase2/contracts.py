"""Minimum typed identity contract for the M1 reader boundary."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


CONTRACT_VERSION = "1"
PHASE1C_COMMIT = "90c0bc8e285ee69262c7db826b786096a77ad004"


@dataclass(frozen=True)
class RunContextV1:
    assessment_id: str
    phase1c_run_id: UUID
    original_deal_id: str
    submission_ref: str
    as_of_at: datetime
    data_snapshot_ref: str
    catalog_version: str
    policy_set_code: str
    config_hash: str
    source_input_digest: str
    bundle_sha256: str
    phase1c_commit: str = PHASE1C_COMMIT
    contract_version: str = CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.assessment_id or not self.original_deal_id or not self.submission_ref:
            raise ValueError("Assessment and original submission identity are required")
        if self.as_of_at.tzinfo is None or self.as_of_at.utcoffset() is None:
            raise ValueError("Business as-of timestamp must be timezone aware")
        if any(not value for value in (self.data_snapshot_ref, self.catalog_version,
                                       self.policy_set_code, self.config_hash)):
            raise ValueError("Pinned reader versions and configuration hash are required")
        if any(len(value) != 64 or any(char not in "0123456789abcdef" for char in value)
               for value in (self.source_input_digest, self.bundle_sha256)):
            raise ValueError("Source and bundle digests must be lowercase SHA-256")
        if self.phase1c_commit != PHASE1C_COMMIT or self.contract_version != CONTRACT_VERSION:
            raise ValueError("Unsupported Phase 1C pin or contract version")
