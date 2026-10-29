"""Repository proposal files are data, never owner approvals or send instructions."""

from hashlib import sha256
import json
from pathlib import Path
import unittest

from dealdesk_phase2.groq_typed_final import (FINAL_SYSTEM_INSTRUCTION,
    PROMPT_VERSION, SCHEMA_NAME, WIRE_VERSION)
from dealdesk_phase2.hybrid_pack import _canonical
from dealdesk_phase2.live_models import GROQ_MODEL
from dealdesk_phase2.m20_groq import (PROMPT_VERSION as CONFIG_PROMPT,
    WIRE_VERSION as CONFIG_WIRE, system_instruction as config_instruction)
from dealdesk_phase2.phase1c_adapter import PHASE1C_COMMIT
from dealdesk_phase2.tool_permissions import PERMISSION_VERSION
from dealdesk_phase2.typed_final_hosted import (BUDGET_KEYS, CASE_KEYS, CONTEXT_KEYS,
    HOSTED_ACTIVATION, INSPECTION_PROMPT_VERSION, INSPECTION_WIRE_VERSION,
    MANIFEST_KEYS, MANIFEST_VERSION, SCHEMA_SHA256, _validate_manifest, budgets,
    inspection_instruction, run_typed_final_hosted)


ROOT = Path(__file__).resolve().parents[2] / "architecture" / "trial-proposals"


class ProposalContracts(unittest.TestCase):
    def test_proposals_match_offline_contract_but_cannot_authorize_a_send(self):
        self.assertIs(HOSTED_ACTIVATION, False)
        for file, specialist, case_id, subject in (
            ("pricing-b05-typed-final-v2.json", "pricing", "B05", "M18-D-B05"),
            ("credit-limit-typed-final-v2.json", "credit", "CREDIT-LIMIT",
             "CONFLICT-DEAL-13"),
        ):
            with self.subTest(file=file):
                proposal = json.loads((ROOT / file).read_text())
                self.assertEqual(set(proposal), MANIFEST_KEYS)
                self.assertEqual(set(proposal["case"]), CASE_KEYS)
                self.assertEqual(set(proposal["execution_context"]), CONTEXT_KEYS)
                self.assertEqual(set(proposal["budgets"]), BUDGET_KEYS)
                self.assertEqual(proposal["version"], MANIFEST_VERSION)
                self.assertEqual(proposal["status"], "proposal_not_authorized_not_executable")
                self.assertEqual(proposal["case"]["case_id"], case_id)
                self.assertEqual(proposal["case"]["subject_id"], subject)
                self.assertEqual(proposal["specialist"], specialist)
                self.assertEqual(proposal["inspection_plan"], 1)
                self.assertEqual(proposal["budgets"], budgets(specialist, 1))
                self.assertEqual(proposal["phase1c_pin"], PHASE1C_COMMIT)
                self.assertEqual(proposal["model"], GROQ_MODEL)
                self.assertEqual(proposal["provider"], "groq")
                self.assertEqual(proposal["permission_version"], PERMISSION_VERSION)
                self.assertEqual(proposal["inspection_wire_version"],
                                 INSPECTION_WIRE_VERSION)
                self.assertEqual(proposal["inspection_prompt_version"],
                                 INSPECTION_PROMPT_VERSION)
                self.assertEqual(proposal["inspection_prompt_sha256"], sha256(
                    inspection_instruction(specialist).encode()).hexdigest())
                self.assertEqual(proposal["configuration_wire_version"], CONFIG_WIRE)
                self.assertEqual(proposal["configuration_prompt_version"], CONFIG_PROMPT)
                self.assertEqual(proposal["configuration_prompt_sha256"], sha256(
                    config_instruction("configuration").encode()).hexdigest())
                self.assertEqual(proposal["wire_version"], WIRE_VERSION)
                self.assertEqual(proposal["prompt_version"], PROMPT_VERSION)
                self.assertEqual(proposal["final_prompt_sha256"], sha256(
                    FINAL_SYSTEM_INSTRUCTION.encode()).hexdigest())
                self.assertEqual(proposal["schema_name"], SCHEMA_NAME)
                self.assertEqual(proposal["schema_sha256"], SCHEMA_SHA256)
                self.assertIsNone(proposal["account_id"])
                self.assertIsNone(proposal["billing_state"])
                for name in ("assessment_id", "run_id", "bundle_sha256",
                             "source_input_digest", "as_of_at", "data_snapshot_ref"):
                    self.assertIsNone(proposal["case"][name])
                for name in CONTEXT_KEYS - {"fresh_databases_required"}:
                    self.assertIsNone(proposal["execution_context"][name])
                digest = sha256(_canonical(proposal).encode()).hexdigest()
                with self.assertRaises(ValueError):
                    _validate_manifest(proposal, digest, specialist, None, None, {})
                with self.assertRaisesRegex(ValueError,
                                            "activation_or_authorization_required"):
                    run_typed_final_hosted(None, {}, None, manifest=proposal,
                        approved_manifest_sha256=digest, specialist=specialist,
                        owner_dir=None, authorized=True, owner_billing_attested=True)


if __name__ == "__main__":
    unittest.main()
