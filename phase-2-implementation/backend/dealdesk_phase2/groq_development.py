"""Fresh synthetic Groq development manifest and private audit record.

No sender here. The gated hosted entry checks every field again before sends.
"""

import os
from hashlib import sha256
from pathlib import Path

from .graph_state import pinned_from_state
from .groq_typed_final import (WIRE_VERSION, PROMPT_VERSION, SCHEMA_NAME,
    DEVELOPMENT_FINAL_INSTRUCTION, CONFIG_FINAL_INSTRUCTION)
from .hybrid_pack import _canonical
from .live_models import GROQ_MODEL
from .m20_groq import WIRE_VERSION as CONFIG_WIRE, PROMPT_VERSION as CONFIG_PROMPT
from .m20_groq import system_instruction as config_instruction
from .m21_groq_contract import WIRE_VERSION as CREDIT_WIRE
from .phase1c_adapter import PHASE1C_COMMIT
from .tool_permissions import PERMISSION_VERSION
from .typed_final_hosted import (APPROVAL_NAME, MANIFEST_VERSION, SCHEMA_SHA256,
    INSPECTION_WIRE_VERSION, INSPECTION_PROMPT_VERSION, budgets,
    inspection_instruction, _validate_manifest)


def build_manifest(original, config, adapter, *, case_id, specialist, plan,
                   account_id, owner_dir):
    snapshot = original.get_state(config)
    pinned = pinned_from_state(snapshot.values)
    adapter.validate_pinned_context(pinned)
    ctx = pinned.context
    with original.phase2_connection_factory() as db:
        fixture_name, fixture_oid = db.execute("SELECT current_database(), oid FROM "
            "pg_database WHERE datname=current_database()").fetchone()
    checkpoint_row = original.checkpointer.conn.execute(
        "SELECT current_database(), oid FROM pg_database WHERE datname=current_database()"
        ).fetchone()
    checkpoint_name, checkpoint_oid = (checkpoint_row["current_database"],
                                        checkpoint_row["oid"])
    manifest = {"version": MANIFEST_VERSION, "status": "standing_development",
        "phase1c_pin": PHASE1C_COMMIT, "specialist": specialist,
        "inspection_plan": plan, "account_id": account_id,
        "billing_state": "owner_asserts_free_tier_billing_disabled",
        "provider": "groq", "model": GROQ_MODEL,
        "credential_env_selection": "GROQ_SECONDARY_API_KEY",
        "permission_version": PERMISSION_VERSION,
        "inspection_wire_version": INSPECTION_WIRE_VERSION,
        "inspection_prompt_version": INSPECTION_PROMPT_VERSION,
        "inspection_prompt_sha256": sha256(inspection_instruction(specialist).encode()).hexdigest(),
        "configuration_wire_version": CONFIG_WIRE,
        "configuration_prompt_version": CONFIG_PROMPT,
        "configuration_prompt_sha256": sha256(config_instruction("configuration").encode()).hexdigest(),
        "configuration_final_prompt_sha256": sha256(CONFIG_FINAL_INSTRUCTION.encode()).hexdigest(),
        "wire_version": WIRE_VERSION, "prompt_version": PROMPT_VERSION,
        "final_prompt_sha256": sha256(DEVELOPMENT_FINAL_INSTRUCTION.encode()).hexdigest(),
        "schema_name": SCHEMA_NAME, "schema_sha256": SCHEMA_SHA256,
         "budgets": budgets(specialist, plan, development=True),
        "case": {"case_id": case_id, "assessment_id": ctx.assessment_id,
            "run_id": str(ctx.phase1c_run_id), "subject_id": ctx.original_deal_id,
            "bundle_sha256": ctx.bundle_sha256, "source_input_digest": ctx.source_input_digest,
            "as_of_at": ctx.as_of_at.isoformat(), "data_snapshot_ref": ctx.data_snapshot_ref},
        "execution_context": {"fixture_database": fixture_name,
            "checkpoint_database": checkpoint_name, "fixture_database_oid": fixture_oid,
            "checkpoint_database_oid": checkpoint_oid, "owner_directory": str(owner_dir),
            "fresh_databases_required": True}}
    digest = sha256(_canonical(manifest).encode()).hexdigest()
    _validate_manifest(manifest, digest, specialist, owner_dir, pinned, config,
                       development=True)
    return manifest, digest


def record_manifest(owner_dir, manifest, digest):
    """Persist only an identity-bound standing-authorization audit, once."""
    if (not owner_dir.is_absolute() or owner_dir.is_symlink() or
            owner_dir.stat().st_uid != os.geteuid() or
            owner_dir.stat().st_mode & 0o077 or list(owner_dir.iterdir())):
        raise ValueError("groq_development_owner_not_private_and_empty")
    data = {"version": MANIFEST_VERSION, "assessment_id": manifest["case"]["assessment_id"],
        "approved_manifest_sha256": digest,
        "credential_env_selection": "GROQ_SECONDARY_API_KEY",
        "account_id": manifest["account_id"], "owner_billing_attested": True,
        "typed_final_opt_in_confirmed": True}
    path = owner_dir / APPROVAL_NAME
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        output.write(_canonical(data) + "\n")
        output.flush()
        os.fsync(output.fileno())
    directory_fd = os.open(owner_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return path
