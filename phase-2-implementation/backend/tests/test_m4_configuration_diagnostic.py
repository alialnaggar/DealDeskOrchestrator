"""Configuration output-format analysis only; no model send or trust simulation."""

from copy import deepcopy
import json
import unittest

from dealdesk_phase2.m4_configuration_diagnostic import diagnose_boolean_text
from dealdesk_phase2.m4_correction_policy import disposition
from dealdesk_phase2.groq_typed_final import _rejection_category
from dealdesk_phase2.typed_final_contract import InvalidTerminal, decode


def fixture():
    identity = {"assessment_id":"A", "phase1c_run_id":"R", "subject_id":"D",
        "bundle_sha256":"b"*64, "source_input_digest":"a"*64,
        "specialist":"configuration"}
    input = {**identity, "version":"m20-ai-investigation-v1"}
    observations = ({"execution":"completed", "records":[{"ref":"product:P",
        "fields":{"is_sellable":True,"is_active":False,"catalog_version":"v1"}}],
        "returned_refs":["product:P"]},)
    raw = {"version":"terminal-final-v1", "kind":"finding", "claims":[
        {"ref":"product:P", "field":"is_sellable", "value_json":'"true"'}],
        "uncertainty_reasons":[], "reason_code":"none"}
    return identity, input, observations, raw


def diagnose(identity, input, observations, raw, **kwargs):
    return diagnose_boolean_text(json.dumps(raw), input=input,
        observations=observations, expected_identity=identity,
        fully_returned=kwargs.get("fully_returned", True),
        remaining_turns=kwargs.get("remaining_turns", 1))


class ConfigurationDiagnostic(unittest.TestCase):
    def test_precise_boolean_text_diagnostic_never_enables_send(self):
        identity, input, observations, raw = fixture()
        with self.assertRaises(InvalidTerminal):
            decode(json.dumps(raw), specialist="configuration", input=input,
                   observations=observations)
        before = deepcopy(raw)
        result = diagnose(identity, input, observations, raw)
        self.assertEqual(result["classification"], "boolean_text_format_candidate")
        self.assertEqual(result["field_paths"], ["claims[0].value_json"])
        self.assertFalse(result["eligible"])
        self.assertEqual(result["reason"], "offline_only_no_bound_correction_receipt_or_budget")
        self.assertEqual(raw, before)  # diagnostic projection cannot fix the model output
        def envelope(value):
            return {"choices":[{"finish_reason":"stop", "message":{
                "content":json.dumps(value)}}], "usage":{
                "prompt_tokens":1,"completion_tokens":1}}
        forged = deepcopy(raw)
        forged["claims"][0]["ref"] = "product:FORGED"
        self.assertEqual(_rejection_category(envelope(raw), input=input,
            observations=observations), "claim_binding")
        self.assertEqual(_rejection_category(envelope(forged), input=input,
            observations=observations), "claim_binding")
        # A hosted rejection category alone cannot distinguish these cases.
        self.assertEqual(diagnose(identity, input, observations, forged)[
            "classification"], "not_proven")
        self.assertFalse(disposition("configuration", "boolean_text_format",
            fully_returned=True, remaining_turns=1)["eligible"])
        corrected = deepcopy(raw)
        corrected["claims"][0]["value_json"] = "true"  # model-authored hypothetical
        self.assertEqual(decode(json.dumps(corrected), specialist="configuration",
            input=input, observations=observations)["kind"], "finding")
        self.assertEqual(diagnose(identity, input, observations, corrected)[
            "classification"], "not_proven")

    def test_source_identity_forgery_and_other_bad_claims_are_not_format_proof(self):
        identity, input, observations, raw = fixture()
        candidates = []
        for key in ("subject_id", "source_input_digest", "bundle_sha256", "phase1c_run_id"):
            candidates.append((identity, {**input, key:"wrong"}, observations, raw))
        for ref, field, value in (("product:FORGED", "is_sellable", '"true"'),
                                  ("product:P", "unknown", '"true"'),
                                  ("product:P", "is_sellable", '"false"'),
                                  ("product:P", "is_sellable", "true")):
            changed = deepcopy(raw)
            changed["claims"][0].update(ref=ref, field=field, value_json=value)
            candidates.append((identity, input, observations, changed))
        changed = deepcopy(raw)
        changed["claims"].append({"ref":"product:P", "field":"catalog_version",
            "value_json":'"invented"'})
        candidates.append((identity, input, observations, changed))
        for item in candidates:
            with self.subTest(item=item):
                self.assertEqual(diagnose(*item)["classification"], "not_proven")
        self.assertEqual(diagnose(identity,input,observations,raw,fully_returned=False)[
            "classification"], "not_proven")
        self.assertEqual(diagnose(identity,input,observations,raw,remaining_turns=0)[
            "classification"], "not_proven")
        self.assertEqual(diagnose(identity,input,({**observations[0],
            "returned_refs":[]},),raw)["classification"], "not_proven")

    def test_malformed_and_duplicate_json_never_prove_correction(self):
        identity, input, observations, raw = fixture()
        base = dict(input=input, observations=observations,
                    expected_identity=identity, fully_returned=True, remaining_turns=1)
        for content in ('{"version":1,"version":2}', "not-json", "x"*8193,
                        "\ud800", json.dumps({**raw, "claims":[]})):
            with self.subTest(content=content[:40]):
                self.assertFalse(diagnose_boolean_text(content, **base)["eligible"])
                self.assertEqual(diagnose_boolean_text(content, **base)[
                    "classification"], "not_proven")


if __name__ == "__main__":
    unittest.main()
