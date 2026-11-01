"""Synthetic structure checks only; NO signing, issuer or hosted authority."""

from copy import deepcopy
from datetime import datetime, timezone
import unittest

from dealdesk_phase2.graph_state import SPECIALISTS
from dealdesk_phase2.m22_authorization_contract import (VERSION,
    audit_proposal)
from dealdesk_phase2.m22_hosted_readiness import CONTRACTS, PROMPT_PLAN
from dealdesk_phase2.m22_registry import _digest
from dealdesk_phase2.phase1c_adapter import PHASE1C_COMMIT
from test_m22_registry import case

NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


def fixture():
    cases = [{**case(i), "contract_versions": CONTRACTS} for i in (0, 1)]
    manifest = {"version": "m22-scheduled-registry-v1", "campaign_id": "synthetic-only",
        "phase1c_pin": PHASE1C_COMMIT, "phase2_sha": "f"*40, "cases": cases}
    manifest["sha256"] = _digest(manifest)
    proposal = {"version": VERSION, "approval_id": "mock-not-a-real-approval",
        "campaign_id": manifest["campaign_id"],
        "campaign_manifest_sha256": manifest["sha256"],
        "case_set_sha256": _digest(cases), "phase1c_commit": PHASE1C_COMMIT,
        "phase2_commit": "f"*40, "cohorts": ["fault_injection"],
        "stages": [{"specialist": name, "model_id": CONTRACTS["model"],
            "prompt_version": PROMPT_PLAN[name], "prompt_sha256": "a"*64,
            "wire_version": "mock-wire-v1", "schema_sha256": (
                "c"*64 if name == "pricing" else None),
            "stage_manifest_sha256": "b"*64,
            "max_requests_per_case": 2, "max_requests_total": 4,
            "max_completion_tokens_per_request": 512} for name in SPECIALISTS],
        "max_requests_per_case": 12, "max_requests_total": 24,
        "max_completion_tokens_total": 12288,
        "max_provider_spend_usd": "0.00", "billing_disabled_required": True,
        "window_start": "2026-11-01T11:00:00+00:00",
        "window_end": "2026-11-01T13:00:00+00:00",
        "issued_at": "2026-11-01T10:00:00+00:00",
        "expires_at": "2026-11-01T13:00:00+00:00",
        "operator_subject_id": "mock-operator", "approver_subject_id": "mock-other",
        "issuer_key_id": "mock-not-a-trust-anchor", "checkpoint_namespace": "mock-namespace",
        "revocation_feed_id": "mock-feed", "signature_b64": "not-a-signature"}
    return manifest, proposal


def audit(manifest, proposal, **overrides):
    return audit_proposal(proposal, manifest,
        expected_manifest_sha256=overrides.get("digest", manifest["sha256"]),
        expected_issuer_key_id="mock-not-a-trust-anchor", now=overrides.get("now", NOW),
        revoked_ids=overrides.get("revoked", frozenset()))


class ProposalOnly(unittest.TestCase):
    def test_even_perfect_synthetic_structure_never_authorizes(self):
        manifest, proposal = fixture()
        result = audit(manifest, proposal)
        self.assertEqual(result, {"version": VERSION, "authorization_status": "blocked",
            "errors": ["independent_verification_unavailable"]})
        self.assertNotIn("authorized", str(result))

    def test_missing_issuer_operator_or_signature(self):
        manifest, proposal = fixture()
        self.assertIn("invalid_contract", audit(manifest, {})["errors"])
        for key, value in (("issuer_key_id", "wrong-issuer"),
                           ("approver_subject_id", "mock-operator"),
                           ("signature_b64", "")):
            with self.subTest(key=key):
                changed = {**proposal, key: value}
                self.assertIn("issuer_or_separation_invalid",
                              audit(manifest, changed)["errors"])

    def test_manifest_membership_or_scope_change(self):
        manifest, proposal = fixture()
        for key, value, error in (("campaign_id", "other", "campaign_binding_changed"),
                                  ("phase1c_commit", "wrong", "campaign_binding_changed"),
                                  ("phase2_commit", "wrong", "campaign_binding_changed"),
                                  ("cohorts", ["phase1c_36_held_out"], "case_membership_changed"),
                                  ("case_set_sha256", "c"*64, "case_membership_changed")):
            with self.subTest(key=key):
                self.assertIn(error, audit(manifest, {**proposal,key:value})["errors"])
        changed = deepcopy(manifest)
        changed["cases"][0]["case_id"] = "modified"
        self.assertIn("manifest_unverified", audit(changed, proposal)["errors"])
        other = deepcopy(manifest)
        other["campaign_id"] = "other"
        other["sha256"] = _digest({k:v for k,v in other.items() if k!="sha256"})
        self.assertIn("campaign_binding_changed", audit(other, proposal)["errors"])

    def test_model_prompt_and_stage_budget_changed(self):
        manifest, proposal = fixture()
        for key,value,error in (("prompt_sha256", "bad", "stage_identity_invalid"),
                                ("prompt_version", "different", "stage_identity_invalid"),
                                ("model_id", "other", "case_model_or_contract_changed"),
                                ("max_requests_per_case", 0, "request_budget_invalid")):
            with self.subTest(key=key):
                changed = deepcopy(proposal)
                changed["stages"][0][key] = value
                self.assertIn(error, audit(manifest, changed)["errors"])
        changed = deepcopy(proposal)
        changed["stages"].pop()
        self.assertIn("six_stage_scope_incomplete", audit(manifest, changed)["errors"])
        changed = deepcopy(proposal)
        changed["stages"][0], changed["stages"][1] = (
            changed["stages"][1], changed["stages"][0])
        self.assertIn("six_stage_scope_incomplete", audit(manifest, changed)["errors"])
        changed = {**proposal, "max_requests_total": 1000}
        self.assertIn("campaign_budget_invalid", audit(manifest, changed)["errors"])
        changed = {**proposal, "max_provider_spend_usd": "100.00"}
        self.assertIn("spending_not_disabled", audit(manifest, changed)["errors"])

    def test_expiry_revocation_reuse_and_malformed_input(self):
        manifest, proposal = fixture()
        self.assertIn("expired_or_out_of_window", audit(manifest, proposal,
            now=datetime(2026, 11, 1, 14, tzinfo=timezone.utc))["errors"])
        self.assertIn("revoked", audit(manifest, proposal, revoked=frozenset({
            proposal["approval_id"]}))["errors"])
        changed = {**proposal, "checkpoint_namespace":"", "approval_id":""}
        self.assertIn("issuer_or_separation_invalid", audit(manifest, changed)["errors"])
        self.assertIn("issuer_or_separation_invalid", audit(manifest,
            {**proposal, "approval_id": []})["errors"])
        self.assertIn("window_invalid", audit(manifest,
            {**proposal, "issued_at":"not-a-date"})["errors"])


if __name__ == "__main__":
    unittest.main()
