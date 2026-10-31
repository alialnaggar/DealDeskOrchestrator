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
    def test_b05_exact_review_hash_is_not_a_runtime_authorization(self):
        """The final owner-review digest includes the future status, not the proposal's."""
        base = json.loads((ROOT / "pricing-b05-typed-final-v2.json").read_text())
        proposal = json.loads((ROOT / "pricing-b05-scram-final-review-proposal.json").read_text())
        self.assertEqual(set(proposal), MANIFEST_KEYS)
        self.assertEqual(set(proposal["case"]), CASE_KEYS)
        self.assertEqual(set(proposal["execution_context"]), CONTEXT_KEYS)
        self.assertEqual(proposal["status"], "proposal_not_authorized_not_executable")
        self.assertEqual(proposal["account_id"], "org_01m5d82zneee6b2vzsz8d2014b")
        self.assertEqual(proposal["billing_state"],
                         "owner_asserts_free_tier_billing_disabled")
        self.assertEqual(proposal["case"]["assessment_id"],
                         "TYPED-B05-SCRAM-8ba93fddd647")
        self.assertEqual(proposal["case"]["bundle_sha256"],
                         "a80b5b99f5d09ca2568010f8c26867413f4049097173e72ff229661e7a830df9")
        self.assertEqual(proposal["execution_context"]["fixture_database_oid"], 16385)
        self.assertEqual(proposal["execution_context"]["checkpoint_database_oid"], 16386)
        for key in set(base) - {"account_id", "billing_state", "case", "execution_context"}:
            self.assertEqual(proposal[key], base[key])
        self.assertEqual(proposal["budgets"], budgets("pricing", 1))
        self.assertEqual(proposal["inspection_prompt_sha256"], sha256(
            inspection_instruction("pricing").encode()).hexdigest())
        self.assertEqual(proposal["configuration_prompt_sha256"], sha256(
            config_instruction("configuration").encode()).hexdigest())
        self.assertEqual(proposal["final_prompt_sha256"], sha256(
            FINAL_SYSTEM_INSTRUCTION.encode()).hexdigest())
        self.assertEqual(proposal["schema_sha256"], SCHEMA_SHA256)
        proposed_digest = sha256(_canonical(proposal).encode()).hexdigest()
        self.assertEqual(proposed_digest,
                         "16feccc8c0e499d8015399f1404bf101bd04ce08a2f0d133ed0710d877012b1a")
        with self.assertRaises(ValueError):
            _validate_manifest(proposal, proposed_digest, "pricing", None, None, {})
        future = {**proposal, "status": "authorized_one_case"}  # Only in memory.
        self.assertEqual(sha256(_canonical(future).encode()).hexdigest(),
                         "530cfc1d87cde830b3376284e9f0a05dd6a0e167b9e5c7bc27def85c2a42b0e3")
        self.assertIs(HOSTED_ACTIVATION, False)

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
                if specialist == "credit":
                    # Frozen, non-authorizing v1 proposal; the active Credit-only
                    # inspection is now explicitly versioned v2. Never rewrite
                    # historical proposal hashes to fit a newer prompt.
                    self.assertEqual(proposal["inspection_prompt_sha256"],
                        "e9a230c09fc8a046f883490a9108b589a53c761041d0db52f103cdb4c48c6e57")
                    self.assertNotEqual(proposal["inspection_prompt_sha256"], sha256(
                        inspection_instruction(specialist).encode()).hexdigest())
                else:
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
