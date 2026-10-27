"""M2.0 offline AI evidence, failure and PostgreSQL restart boundaries."""

import os
from pathlib import Path
import unittest
from uuid import UUID

from dealdesk_phase2.m20_specialists import (_validate_claims, run_m20_offline, VERSION)
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import Phase1CAdapter, EvidenceMismatch
from m18_case_setup import CASES, install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None


class Scripted:
    provider = "offline_double"
    offline_only = True
    model = "m20-scripted-v1"

    def __init__(self, actions):
        self.actions = list(actions)
        self.calls = 0

    def next_action(self, input, observations):
        self.calls += 1
        return self.actions.pop(0)(input, observations)


def inspect(input, observations):
    return {"kind": "inspect", "tool": input["permitted_tool"],
            "line_id": input["line_ids"][0]}


def product_finding(input, observations):
    row = observations[0]["records"][0]
    return {"kind": "finding", "claims": [{"ref": row["ref"],
            "field": "is_sellable", "value": row["fields"]["is_sellable"]}],
            "uncertainty_reasons": []}


def pricing_finding(input, observations):
    row = observations[0]["records"][0]
    return {"kind": "finding", "claims": [{"ref": row["ref"],
            "field": "fixed_margin_pct", "value": row["fields"]["fixed_margin_pct"]}],
            "uncertainty_reasons": []}


class M20Contracts(unittest.TestCase):
    def test_only_returned_domain_fields_support_claims(self):
        records = [{"ref": "product:P", "fields": {"is_sellable": True}}]
        observation = {"execution": "completed", "records": records,
                       "returned_refs": ["product:P"]}
        base = {"kind": "finding", "claims": [{"ref": "product:P", "field": "is_sellable",
                                                  "value": True}], "uncertainty_reasons": []}
        self.assertEqual(_validate_claims(base, [observation], "configuration"), base["claims"])
        for claim in ({"ref": "product:P", "field": "is_sellable", "value": False},
                      {"ref": "product:forged", "field": "is_sellable", "value": True},
                      {"ref": "pricing_line:P", "field": "is_sellable", "value": True}):
            with self.subTest(claim=claim), self.assertRaises(ValueError):
                _validate_claims({**base, "claims": [claim]}, [observation], "configuration")
        with self.assertRaises(ValueError):
            _validate_claims(base, [{**observation, "returned_refs": []}], "configuration")
        with self.assertRaises(ValueError):
            _validate_claims({**base, "claims": [{**base["claims"][0], "value": 1}]},
                             [observation], "configuration")  # bool is not numeric 1
        pricing = {"execution": "completed", "returned_refs": ["pricing_line:L"],
                   "records": [{"ref": "pricing_line:L", "fields": {
                       "fixed_margin_pct": "21.000"}}]}
        with self.assertRaises(ValueError):
            _validate_claims({"kind": "finding", "claims": [{"ref": "pricing_line:L",
                "field": "fixed_margin_pct", "value": "31.000"}],
                "uncertainty_reasons": []}, [pricing], "pricing")


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Separate disposable M2.0 business/checkpoint databases required")
class M20PinnedPostgres(unittest.TestCase):
    def test_sequential_specialists_positive_abstain_adverse_restart_and_fixed_isolation(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer

        database = os.environ["M20_DATABASE_URL"]
        checkpoint = os.environ["M20_CHECKPOINT_DATABASE_URL"]
        adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        connect = lambda: psycopg.connect(database)
        with connect() as conn:
            count = conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0]
        if not count:
            with connect() as conn:
                install_disposable_cases(conn)

        def original(saver, name, case_id):
            graph = build_original_graph(adapter, connect, saver)
            case = next(item for item in CASES if item.case_id == case_id)
            config = {"configurable": {"thread_id": name}}
            state = graph.invoke(initial_state(name, case.run_id), config)
            self.assertEqual(len(state["specialist_results"]), 6)
            return graph, config, state

        with thesis_checkpointer(checkpoint) as saver:
            graph, config, before = original(saver, "M20-POSITIVE-B05", "B05")
            configuration = Scripted([inspect, product_finding])
            pricing = Scripted([inspect, pricing_finding])
            after = run_m20_offline(graph, config, adapter, {
                "configuration": configuration, "pricing": pricing})
            self.assertEqual([after["m20_ai_results"][k]["execution"] for k in (
                "configuration", "pricing")], ["completed", "completed"])
            self.assertEqual(after["specialist_results"], before["specialist_results"])
            self.assertEqual(after["review_status"], before["review_status"])
            self.assertEqual(after["candidate_status"], "not_started")
            self.assertEqual(after["m20_review"]["fixed_review_status"], before["review_status"])
            self.assertEqual(after["m20_review"]["specialists"]["configuration"][
                "validated_claims"], after["m20_ai_results"]["configuration"]["validated_claims"])
            self.assertEqual((configuration.calls, pricing.calls), (2, 2))
            self.assertEqual(len([e for e in after["tool_access_ledger"] if e["status"] == "completed"]), 2)
            self.assertEqual([v["specialist"] for v in after["m20_ai_results"].values()],
                             ["configuration", "pricing"])
            self.assertEqual(after["m20_ai_results"]["pricing"]["version"], VERSION)
            self.assertEqual({x["status"] for x in after["m20_model_attempts"]},
                             {"returned", "reserved"})
        # PostgreSQL checkpoint reopening must not call either model or charge another tool.
        with thesis_checkpointer(checkpoint) as saver:
            reopened = build_original_graph(adapter, connect, saver)
            resumed = run_m20_offline(reopened, config, adapter, {
                "configuration": configuration, "pricing": pricing})
            self.assertEqual(resumed["m20_ai_results"], after["m20_ai_results"])
            self.assertEqual(resumed["tool_access_ledger"], after["tool_access_ledger"])
            self.assertEqual((configuration.calls, pricing.calls), (2, 2))

            graph, config, original_n = original(saver, "M20-ABSTAIN-N01", "N01")
            abstain = Scripted([lambda *_: {"kind": "abstain", "reason_code": "model_uncertainty"}])
            price = Scripted([inspect, pricing_finding])
            state = run_m20_offline(graph, config, adapter, {
                "configuration": abstain, "pricing": price})
            self.assertEqual(state["m20_ai_results"]["configuration"]["execution"], "abstained")
            self.assertEqual(state["m20_ai_results"]["pricing"]["execution"], "completed")
            self.assertEqual(state["specialist_results"], original_n["specialist_results"])

            # Pinned offer-only reference: conditional supply never becomes a
            # confirmed or verified candidate due to an unrelated AI finding.
            graph = build_original_graph(adapter, connect, saver)
            config = {"configurable": {"thread_id": "M20-CONDITIONAL-OFFER"}}
            offer_run = UUID("00000000-0000-4000-8000-000000030001")
            original_offer = graph.invoke(initial_state("M20-CONDITIONAL-OFFER", offer_run), config)
            self.assertEqual(original_offer["specialist_results"]["fulfillment"]["finding"],
                             "conditional")
            state = run_m20_offline(graph, config, adapter, {
                "configuration": Scripted([inspect, product_finding]),
                "pricing": Scripted([inspect, pricing_finding])})
            self.assertEqual(state["specialist_results"], original_offer["specialist_results"])
            self.assertEqual(state["candidate_status"], "not_started")
            self.assertEqual(state["m20_review"]["fixed_review_status"],
                             original_offer["review_status"])

            graph, config, original_b = original(saver, "M20-FORGED-B02", "B02")
            forged = Scripted([inspect, lambda input, obs: {"kind": "finding",
                "claims": [{"ref": "product:FORGED", "field": "is_sellable", "value": True}],
                "uncertainty_reasons": []}])
            price = Scripted([lambda *_: {"kind": "abstain", "reason_code": "insufficient_evidence"}])
            state = run_m20_offline(graph, config, adapter, {
                "configuration": forged, "pricing": price})
            self.assertEqual(state["m20_ai_results"]["configuration"]["execution"], "error")
            self.assertEqual(state["m20_ai_results"]["configuration"]["validated_claims"], [])
            self.assertEqual(state["m20_review"]["specialists"]["configuration"][
                "validated_claims"], [])
            self.assertEqual(state["m20_ai_results"]["pricing"]["execution"], "abstained")
            self.assertEqual(state["specialist_results"], original_b["specialist_results"])

            graph, config, original_bad = original(saver, "M20-INVALID-B04", "B04")
            # A model cannot inspect an unrelated/historical line or acquire another domain tool.
            bad = Scripted([lambda input, obs: {"kind": "inspect",
                "tool": "inspect_pricing_line", "line_id": "M18-L-B01"}])
            price = Scripted([inspect, pricing_finding])
            state = run_m20_offline(graph, config, adapter, {
                "configuration": bad, "pricing": price})
            self.assertEqual(state["m20_ai_results"]["configuration"]["execution"], "error")
            self.assertEqual(state["m20_ai_results"]["pricing"]["execution"], "completed")
            self.assertEqual(state["specialist_results"], original_bad["specialist_results"])

            # Change only the disposable B03 product before its *new* pinned read.
            # Phase 1C, not AI or the test, determines invalid configuration.
            with connect() as conn:
                conn.execute("UPDATE deal_desk.products SET is_sellable=false "
                             "WHERE product_id='M18-P-B03'")
            graph, config, original_skip = original(saver, "M20-CONFIG-INVALID-B03", "B03")
            self.assertEqual(original_skip["specialist_results"]["configuration"]["finding"],
                             "infeasible")
            cfg = Scripted([lambda *_: {"kind": "abstain", "reason_code": "model_uncertainty"}])
            price = Scripted([inspect])
            state = run_m20_offline(graph, config, adapter, {"configuration": cfg,
                                                            "pricing": price})
            self.assertEqual(state["m20_ai_results"]["pricing"]["execution"], "skipped")
            self.assertEqual(price.calls, 0)
            self.assertEqual(state["specialist_results"]["configuration"]["finding"], "infeasible")

            graph, interrupted_config, original_interrupted = original(
                saver, "M20-INTERRUPTED-N02", "N02")
            def interrupt(*_):
                raise KeyboardInterrupt("simulated offline process stop")
            interrupted = Scripted([interrupt])
            with self.assertRaises(KeyboardInterrupt):
                run_m20_offline(graph, interrupted_config, adapter, {
                    "configuration": interrupted,
                    "pricing": Scripted([lambda *_: {"kind": "abstain",
                        "reason_code": "model_uncertainty"}])})
            self.assertEqual(interrupted.calls, 1)
            self.assertEqual(graph.get_state(interrupted_config).values[
                "m20_model_attempts"][0]["status"], "reserved")
        with thesis_checkpointer(checkpoint) as restarted_saver:
            restarted = build_original_graph(adapter, connect, restarted_saver)
            resumed = run_m20_offline(restarted, interrupted_config, adapter, {
                "configuration": interrupted,
                "pricing": Scripted([lambda *_: {"kind": "abstain",
                    "reason_code": "model_uncertainty"}])})
            self.assertEqual(interrupted.calls, 1)  # never replay an uncertain model turn
            self.assertEqual(resumed["m20_ai_results"]["configuration"]["execution"], "error")
            self.assertEqual(resumed["m20_ai_results"]["configuration"]["reason"],
                             "evidence_identity")
            self.assertEqual(resumed["specialist_results"], original_interrupted[
                "specialist_results"])
