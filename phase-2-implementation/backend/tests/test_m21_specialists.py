"""No-network M2.1 source projections, offline AI and checkpoint boundaries."""

from copy import deepcopy
import os
from pathlib import Path
import unittest
from uuid import UUID

from dealdesk_phase2.m21_specialists import (_claims, _project, build_m21_graph,
    run_m21_offline, VERSION)
from dealdesk_phase2.graph_state import pinned_from_state
from dealdesk_phase2.orchestrator import build_original_graph, initial_state
from dealdesk_phase2.phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from dealdesk_phase2.tool_permissions import AuthorizationDenied, TrustedToolScope
from m18_case_setup import CASES, install_disposable_cases

try:
    import psycopg
except ImportError:
    psycopg = None


class Scripted:
    provider = "offline_double"
    offline_only = True
    model = "m21-scripted-v1"

    def __init__(self, actions):
        self.actions = list(actions)
        self.calls = 0

    def next_action(self, input, observations):
        self.calls += 1
        return self.actions.pop(0)(input, observations)


def inspect(input, _):
    return {"kind": "inspect", "tool": input["permitted_tool"],
            "subject_id": input["subject_id"]}


def cite(input, observations):
    row = observations[0]["records"][0]
    field = next(k for k, v in row["fields"].items() if type(v) in (
        str, int, bool, type(None)))
    return {"kind": "finding", "claims": [{"ref": row["ref"],
        "field": field, "value": row["fields"][field]}]}


class M21Contracts(unittest.TestCase):
    def test_exact_returned_fields_and_no_approval_or_bool_numeric_coercion(self):
        obs = {"execution": "completed", "returned_refs": ["fixed_route:D"],
            "records": [{"ref": "fixed_route:D", "fields": {"route_withheld": True}}]}
        claim = {"ref": "fixed_route:D", "field": "route_withheld", "value": True}
        self.assertEqual(_claims({"kind": "finding", "claims": [claim]}, [obs]), [claim])
        for adverse in ({**claim, "value": 1}, {**claim, "value": False},
                        {**claim, "ref": "fixed_route:OTHER"},
                        {**claim, "field": "approved", "value": True}):
            with self.subTest(adverse=adverse), self.assertRaises(ValueError):
                _claims({"kind": "finding", "claims": [adverse]}, [obs])
        with self.assertRaises(ValueError):
            _claims({"kind": "approve", "claims": [claim]}, [obs])
        with self.assertRaises(ValueError):
            _claims({"kind": "finding", "claims": [claim]}, [{**obs, "returned_refs": []}])

    def test_reject_hosted_or_missing_specialists(self):
        with self.assertRaises(ValueError):
            build_m21_graph(None, {}, None, {"credit": Scripted([inspect])})
        bad = Scripted([inspect])
        bad.provider = "groq"
        with self.assertRaises(ValueError):
            build_m21_graph(None, {}, None, {"credit": bad, "policy": Scripted([inspect]),
                "approval_routing": Scripted([inspect])})


@unittest.skipUnless(psycopg and all(os.getenv(k) for k in (
    "M20_DATABASE_URL", "M20_CHECKPOINT_DATABASE_URL", "DEALDESK_PHASE1C_CHECKOUT")),
    "Fresh isolated PostgreSQL business and checkpoint databases required")
class M21Postgres(unittest.TestCase):
    def setUp(self):
        self.db = os.environ["M20_DATABASE_URL"]
        self.checkpoint = os.environ["M20_CHECKPOINT_DATABASE_URL"]
        self.adapter = Phase1CAdapter(Path(os.environ["DEALDESK_PHASE1C_CHECKOUT"]))
        self.connect = lambda: psycopg.connect(self.db)
        with self.connect() as conn:
            count = conn.execute("SELECT count(*) FROM deal_desk.deals WHERE deal_id LIKE 'M18-D-%'").fetchone()[0]
        if not count:
            with self.connect() as conn:
                install_disposable_cases(conn)

    def original(self, saver, name, case="B01"):
        graph = build_original_graph(self.adapter, self.connect, saver)
        config = {"configurable": {"thread_id": name}}
        run = next(x for x in CASES if x.case_id == case).run_id
        before = graph.invoke(initial_state(name, run), config)
        return graph, config, before

    def test_source_first_scopes_and_adverse_pool_identity(self):
        from langgraph.checkpoint.memory import InMemorySaver
        graph, config, state = self.original(InMemorySaver(), "M21-SOURCE-FIRST-B01")
        pinned = pinned_from_state(state)
        pool = self.adapter.validate_pinned_context(pinned)
        context = pinned.context
        scope = TrustedToolScope(context, "credit", context.original_deal_id,
            pool["deal"]["customer_id"], frozenset(), frozenset())
        scope.check(tool="inspect_customer_credit_evidence", context=context,
            subject_id=context.original_deal_id, customer_id=pool["deal"]["customer_id"])
        for subject, customer, tool in (("wrong-subject", pool["deal"]["customer_id"],
                                          "inspect_customer_credit_evidence"),
                                        (context.original_deal_id, "wrong-customer",
                                          "inspect_customer_credit_evidence"),
                                        (context.original_deal_id, pool["deal"]["customer_id"],
                                          "inspect_fixed_policy_hits")):
            with self.subTest(subject=subject, customer=customer, tool=tool), self.assertRaises(
                    AuthorizationDenied):
                scope.check(tool=tool, context=context, subject_id=subject, customer_id=customer)
        credit = _project(pool, state, context, "credit")
        self.assertEqual(credit[0]["ref"], "credit_profile:M18-C-B01")
        self.assertIn("fixed_commitments_fresh", credit[0]["fields"])
        self.assertNotIn("credit_exposure", credit[0]["fields"])
        self.assertNotIn("customer_name", credit[0]["fields"])
        policy = _project(pool, state, context, "policy")
        self.assertEqual({r["ref"] for r in policy}, {"policy_rule:PO-BASE-DELIVERY-LATE"})
        self.assertNotIn("condition_json", policy[0]["fields"])
        route = _project(pool, state, context, "approval_routing")
        self.assertEqual(route, [{"ref": "fixed_route:M18-D-B01", "fields": {
            "route_withheld": True, "roles_available_from_fixed_interface": False}}])
        bad = deepcopy(pool)
        bad["credit"]["customer_id"] = "wrong-customer"
        with self.assertRaises(EvidenceMismatch):
            _project(bad, state, context, "credit")
        bad = deepcopy(pool)
        bad["credit"]["commitments_as_of_at"] = context.as_of_at.replace(year=2099)
        with self.assertRaises(EvidenceMismatch):
            _project(bad, state, context, "credit")
        bad = deepcopy(pool)
        bad["receivables"] = [{"customer_id": "wrong-customer", "receivable_id": "R",
            "as_of_date": context.as_of_at.date()}]
        with self.assertRaises(EvidenceMismatch):
            _project(bad, state, context, "credit")
        bad = deepcopy(pool)
        bad["payments"] = [{"customer_id": pool["deal"]["customer_id"],
            "payment_id": "P", "paid_date": context.as_of_at.date().replace(year=2099)}]
        with self.assertRaises(EvidenceMismatch):
            _project(bad, state, context, "credit")
        bad = deepcopy(pool)
        bad["receivables"] = [{"customer_id": pool["deal"]["customer_id"],
            "receivable_id": "R" + str(i), "as_of_date": context.as_of_at.date(),
            "invoice_number": "INV" + str(i), "due_date": context.as_of_at.date(),
            "outstanding_amount": 1, "status": "Open"} for i in range(25)]
        with self.assertRaises(EvidenceMismatch):
            _project(bad, state, context, "credit")
        bad = deepcopy(pool)
        bad["rules"]["policy_rules"] = []
        with self.assertRaises(EvidenceMismatch):
            _project(bad, state, context, "policy")
        bad_state = deepcopy(state)
        bad_state["specialist_results"]["policy"]["payload"][
            "per_rule_prerequisites_available"] = True
        with self.assertRaises(EvidenceMismatch):
            _project(pool, bad_state, context, "policy")
        bad_state = deepcopy(state)
        bad_state["specialist_results"]["approval_routing"]["payload"]["required_roles"] = [
            {"role": "invented"}]
        with self.assertRaises(EvidenceMismatch):
            _project(pool, bad_state, context, "approval_routing")
        selected = pool["rules"]["approval_rules"][0]
        opened = deepcopy(state)
        opened_route = opened["specialist_results"]["approval_routing"]["payload"]
        opened_route.update({"route_withheld": False, "roles_available_from_fixed_interface": True,
            "required_roles": [{"role": selected["required_role"],
                "sequence": selected["approval_sequence"],
                "rule_id": selected["approval_rule_id"]}]})
        records = _project(pool, opened, context, "approval_routing")
        self.assertEqual(records[1]["fields"]["role"], selected["required_role"])
        opened_route["required_roles"][0]["role"] = "invented"
        with self.assertRaises(EvidenceMismatch):
            _project(pool, opened, context, "approval_routing")

    def test_three_offline_models_fixed_isolation_abstention_errors_and_restart(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        models = {name: Scripted([inspect, cite]) for name in (
            "credit", "policy", "approval_routing")}
        with thesis_checkpointer(self.checkpoint) as saver:
            graph, config, before = self.original(saver, "M21-THREE-OFFLINE-B01")
            state = run_m21_offline(graph, config, self.adapter, models)
            self.assertEqual({name: value["execution"] for name, value in state[
                "m21_ai_results"].items()}, {name: "completed" for name in models})
            self.assertEqual([v["model_turns"] for v in state["m21_ai_results"].values()],
                             [2, 2, 2])
            self.assertEqual(len([e for e in state["tool_access_ledger"] if e[
                "status"] == "completed"]), 3)
            self.assertEqual(state["specialist_results"], before["specialist_results"])
            self.assertEqual(state["review_status"], before["review_status"])
            self.assertEqual(state["candidate_status"], "not_started")
            self.assertTrue(state["m21_review"]["fixed_route_withheld"])
            self.assertEqual(state["reviewer_package"]["m21_ai"], state["m21_review"])
            self.assertEqual(state["m21_ai_results"]["credit"]["version"], VERSION)
        with thesis_checkpointer(self.checkpoint) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver)
            replay = run_m21_offline(graph, config, self.adapter, models)
            self.assertEqual(replay["m21_ai_results"], state["m21_ai_results"])
            self.assertEqual(replay["tool_access_ledger"], state["tool_access_ledger"])
            self.assertEqual({name: model.calls for name, model in models.items()}, {
                name: 2 for name in models})
            graph, config, before = self.original(saver, "M21-ADVERSE-B05", "B05")
            bad_credit = Scripted([inspect, lambda input, obs: {"kind": "finding",
                "claims": [{"ref": "credit_profile:FORGED", "field": "credit_status",
                            "value": "Active"}]}])
            policy = Scripted([lambda *_: {"kind": "abstain",
                "reason_code": "insufficient_evidence"}])
            routing = Scripted([inspect, cite])
            adverse = run_m21_offline(graph, config, self.adapter, {"credit": bad_credit,
                "policy": policy, "approval_routing": routing})
            self.assertEqual([adverse["m21_ai_results"][name]["execution"] for name in (
                "credit", "policy", "approval_routing")], ["error", "abstained", "completed"])
            self.assertEqual(adverse["m21_ai_results"]["credit"]["validated_claims"], [])
            self.assertEqual(adverse["specialist_results"], before["specialist_results"])
            self.assertEqual(adverse["review_status"], before["review_status"])
            graph, config, before = self.original(saver, "M21-WRONG-TOOL-B02", "B02")
            wrong = Scripted([lambda input, obs: {"kind": "inspect",
                "tool": "inspect_fixed_route", "subject_id": input["subject_id"]}])
            state = run_m21_offline(graph, config, self.adapter, {"credit": wrong,
                "policy": Scripted([lambda *_: {"kind": "abstain",
                    "reason_code": "model_uncertainty"}]),
                "approval_routing": Scripted([lambda *_: {"kind": "abstain",
                    "reason_code": "model_uncertainty"}])})
            self.assertEqual(state["m21_ai_results"]["credit"]["execution"], "error")
            self.assertEqual(len(state.get("tool_access_ledger", [])), 0)
            self.assertEqual(state["specialist_results"], before["specialist_results"])

    def test_interrupted_reserved_model_never_replayed_after_postgres_restart(self):
        from dealdesk_phase2.checkpoint import thesis_checkpointer
        interrupted = Scripted([lambda *_: (_ for _ in ()).throw(KeyboardInterrupt())])
        with thesis_checkpointer(self.checkpoint) as saver:
            graph, config, original = self.original(saver, "M21-INTERRUPTED-B01")
            with self.assertRaises(KeyboardInterrupt):
                run_m21_offline(graph, config, self.adapter, {"credit": interrupted,
                    "policy": Scripted([inspect, cite]), "approval_routing": Scripted([inspect, cite])})
            attempts = graph.get_state(config).values["m21_model_attempts"]
            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts[0]["status"], "reserved")
        with thesis_checkpointer(self.checkpoint) as saver:
            graph = build_original_graph(self.adapter, self.connect, saver)
            credit = Scripted([lambda *_: (_ for _ in ()).throw(AssertionError("replayed"))])
            state = run_m21_offline(graph, config, self.adapter, {"credit": credit,
                "policy": Scripted([lambda *_: {"kind": "abstain",
                    "reason_code": "model_uncertainty"}]),
                "approval_routing": Scripted([lambda *_: {"kind": "abstain",
                    "reason_code": "model_uncertainty"}])})
            self.assertEqual(credit.calls, 0)
            self.assertEqual(state["m21_ai_results"]["credit"]["execution"], "error")
            self.assertEqual(state["specialist_results"], original["specialist_results"])
            self.assertEqual(state["candidate_status"], "not_started")
