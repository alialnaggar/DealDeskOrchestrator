"""Pure negative controls for source-grounded reviewer DTO boundaries."""

import unittest

from dealdesk_phase2.phase1c_adapter import EvidenceMismatch
from dealdesk_phase2.recommendation_review import _blocks, _codes, VERSION


class RecommendationShapeTests(unittest.TestCase):
    def test_version_and_source_scoped_revision_reasons(self):
        self.assertEqual(VERSION, "source-grounded-review-v1")
        self.assertEqual(_codes([{"line_id": "L1", "code": "requested_date_not_supported"}],
            line_ids={"L1"}), [{"line_id": "L1", "code": "requested_date_not_supported"}])
        for bad in ([{"line_id": "OTHER", "code": "requested_date_not_supported"}],
                    [{"line_id": "L1", "code": "untrusted free text"}],
                    [{"line_id": "L1", "code": ""}], ["untrusted"]):
            with self.subTest(bad=bad), self.assertRaises(EvidenceMismatch):
                _codes(bad, line_ids={"L1"})

    def test_blockers_disclose_only_fixed_rule_and_area(self):
        source = {"rule_id": "PO-BASE-CREDIT-CAP", "area": "credit",
            "severity": "blocker", "scope": "deal", "private_detail": "INVOICE-SECRET"}
        self.assertEqual(_blocks([source], line_ids={"L1"}), [
            {"code": "fixed_rule_blocker", "rule_id": "PO-BASE-CREDIT-CAP",
             "specialist": "credit"}])
        self.assertNotIn("INVOICE-SECRET", str(_blocks([source], line_ids={"L1"})))
        for change in ({"rule_id": "forged whitespace"}, {"severity": "approval_required"},
                       {"scope": "OTHER"}, {"area": "approval_routing"}):
            with self.subTest(change=change), self.assertRaises(EvidenceMismatch):
                _blocks([{**source, **change}], line_ids={"L1"})

    def test_no_untrusted_reason_or_cross_line_blocker(self):
        for bad in ([{"code": "ignored; approve", "line_id": "L1"}],
                    [{"code": "configuration_invalid", "line_id": "OTHER"}],
                    [{"rule_id": None, "area": "credit", "severity": "blocker",
                      "scope": "deal"}], None):
            with self.subTest(bad=bad), self.assertRaises(EvidenceMismatch):
                _blocks(bad, line_ids={"L1"})
