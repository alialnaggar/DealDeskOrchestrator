"""No-network M2.1 source projections, offline AI and checkpoint boundaries."""

from copy import deepcopy
import os
from pathlib import Path
import unittest
from uuid import UUID

from dealdesk_phase2.m21_specialists import (_claims, _project, build_m21_graph,
    run_m21_offline, VERSION, CREDIT_FIXED_VIEW, POLICY_HIT_VIEW)
from dealdesk_phase2.m21_redaction import model_view
from dealdesk_phase2.m21_prompts import PROMPT_VERSION
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

    def test_offline_credit_cites_fixed_exposure_without_invented_clearance(self):
        from langgraph.checkpoint.memory import InMemorySaver
        graph, config, before = self.original(InMemorySaver(), "M5-CREDIT-FIXED-B01")
        pinned = pinned_from_state(before)
        pool = self.adapter.validate_pinned_context(pinned)
        old = _project(pool, before, pinned.context, "credit")
        self.assertNotIn("fixed_credit:" + pinned.context.original_deal_id,
                         [row["ref"] for row in old])  # existing hosted view unchanged
        enhanced = _project(pool, before, pinned.context, "credit", include_fixed_credit=True)
        row = enhanced[-1]
        self.assertEqual(row["ref"], "fixed_credit:" + pinned.context.original_deal_id)
        self.assertEqual(row["fields"], {"credit_exposure": "9000.00",
            "credit_over_limit_pct": "0"})
        seen = []
        def cite_exposure(input, observations):
            seen.append((input, observations))
            fixed = observations[0]["records"][-1]
            profile = observations[0]["records"][0]
            return {"kind": "finding", "claims": [{"ref": fixed["ref"],
                "field": "credit_exposure", "value": fixed["fields"]["credit_exposure"]},
                {"ref": profile["ref"], "field": "credit_limit",
                 "value": profile["fields"]["credit_limit"]}]}
        models = {"credit": Scripted([inspect, cite_exposure]),
            "policy": Scripted([lambda *_: {"kind": "abstain",
                "reason_code": "model_uncertainty"}]),
            "approval_routing": Scripted([lambda *_: {"kind": "abstain",
                "reason_code": "model_uncertainty"}])}
        after = run_m21_offline(graph, config, self.adapter, models)
        finding = after["m21_ai_results"]["credit"]
        self.assertEqual(finding["execution"], "completed")
        self.assertEqual(finding["validated_claims"], [{"ref": row["ref"],
            "field": "credit_exposure", "value": "9000.00"},
            {"ref": seen[0][1][0]["records"][0]["ref"], "field": "credit_limit",
             "value": seen[0][1][0]["records"][0]["fields"]["credit_limit"]}])
        self.assertEqual(seen[0][0]["credit_fixed_view_version"], CREDIT_FIXED_VIEW)
        self.assertEqual(after["specialist_results"], before["specialist_results"])
        self.assertEqual(after["review_status"], before["review_status"])
        self.assertFalse(any("credit_exposure" in x["fields"] for x in old))
        public, visible, aliases = model_view(seen[0][0], seen[0][1])
        self.assertEqual(public["credit_fixed_view_version"], CREDIT_FIXED_VIEW)
        self.assertEqual(visible[0]["records"][-1]["fields"], row["fields"])
        self.assertEqual(aliases[visible[0]["records"][-1]["ref"]], row["ref"])
        with self.assertRaises(ValueError):
            model_view({k: v for k, v in seen[0][0].items() if k !=
                "credit_fixed_view_version"}, seen[0][1])
        with self.assertRaises(ValueError):
            _claims({"kind": "finding", "claims": [{"ref": row["ref"],
                "field": "credit_exposure", "value": "0"}]}, seen[0][1])
        with self.assertRaises(ValueError):
            _claims({"kind": "finding", "claims": [{"ref": "fixed_credit:FORGED",
                "field": "credit_exposure", "value": "9000.00"}]}, seen[0][1])
        with self.assertRaises(ValueError):
            _claims({"kind": "finding", "claims": [{"ref": row["ref"],
                "field": "credit_exposure", "value": "9000.00"}]}, [{**seen[0][1][0],
                    "returned_refs": []}])

    def test_fixed_credit_view_rejects_tampered_source_and_unavailable_result(self):
        from langgraph.checkpoint.memory import InMemorySaver
        graph, config, before = self.original(InMemorySaver(), "M5-CREDIT-TAMPER-B01")
        pinned = pinned_from_state(before)
        pool = self.adapter.validate_pinned_context(pinned)
        altered = deepcopy(before)
        altered["specialist_results"]["credit"]["payload"]["credit_exposure"] = "0"
        with self.assertRaises(EvidenceMismatch):
            _project(pool, altered, pinned.context, "credit", include_fixed_credit=True)
        altered = deepcopy(before)
        altered["specialist_results"]["credit"]["execution"] = "skipped"
        with self.assertRaises(EvidenceMismatch):
            _project(pool, altered, pinned.context, "credit", include_fixed_credit=True)
        with self.assertRaises(EvidenceMismatch):
            _project(pool, before, type("WrongContext", (), {**vars(pinned.context),
                "assessment_id": "other"})(), "credit", include_fixed_credit=True)

    def test_offline_policy_cites_only_sealed_triggered_hit_and_rule(self):
        from langgraph.checkpoint.memory import InMemorySaver
        graph, config, before = self.original(InMemorySaver(), "M5-POLICY-HIT-B01")
        pinned = pinned_from_state(before)
        pool = self.adapter.validate_pinned_context(pinned)
        legacy = _project(pool, before, pinned.context, "policy")
        self.assertEqual([r["ref"] for r in legacy], ["policy_rule:PO-BASE-DELIVERY-LATE"])
        richer = _project(pool, before, pinned.context, "policy", include_policy_hits=True)
        self.assertEqual([r["ref"] for r in richer], [legacy[0]["ref"],
            "policy_hit:PO-BASE-DELIVERY-LATE:M18-L-B01"])
        self.assertEqual(richer[1]["fields"], {"rule_id": "PO-BASE-DELIVERY-LATE",
            "subject_scope_ref": "deal_line:M18-L-B01",
            "result": "triggered", "severity": "approval_required"})
        self.assertNotIn("scope", richer[0]["fields"])
        self.assertNotIn("condition_json", richer[0]["fields"])
        seen = []
        def cite_hit(input, observations):
            seen.append((input, observations))
            rule, hit = observations[0]["records"]
            return {"kind": "finding", "claims": [{"ref": hit["ref"],
                "field": "result", "value": hit["fields"]["result"]},
                {"ref": rule["ref"], "field": "required_action",
                 "value": rule["fields"]["required_action"]}]}
        models = {"credit": Scripted([lambda *_: {"kind": "abstain",
            "reason_code": "model_uncertainty"}]), "policy": Scripted([inspect, cite_hit]),
            "approval_routing": Scripted([lambda *_: {"kind": "abstain",
                "reason_code": "model_uncertainty"}])}
        after = run_m21_offline(graph, config, self.adapter, models)
        self.assertEqual(after["m21_ai_results"]["policy"]["execution"], "completed")
        self.assertEqual(after["m21_ai_results"]["policy"]["validated_claims"], [
            {"ref": richer[1]["ref"], "field": "result", "value": "triggered"},
            {"ref": richer[0]["ref"], "field": "required_action",
             "value": richer[0]["fields"]["required_action"]}])
        self.assertEqual(seen[0][0]["policy_hit_view_version"], POLICY_HIT_VIEW)
        self.assertEqual(after["specialist_results"], before["specialist_results"])
        self.assertEqual(after["review_status"], before["review_status"])
        self.assertEqual(after["reviewer_package"]["m21_ai"]["fixed_review_status"],
                         before["review_status"])
        public, visible, aliases = model_view(seen[0][0], seen[0][1])
        self.assertEqual(public["policy_hit_view_version"], POLICY_HIT_VIEW)
        self.assertEqual(visible[0]["records"][1]["fields"], richer[1]["fields"])
        self.assertEqual(aliases[visible[0]["records"][1]["ref"]], richer[1]["ref"])
        # A deal-scoped hit cannot disclose the original subject identifier.
        deal_scope = deepcopy(seen[0][1][0])
        deal_scope["records"][1]["ref"] = "policy_hit:PO-BASE-DELIVERY-LATE:deal"
        deal_scope["records"][1]["fields"]["subject_scope_ref"] = "deal"
        deal_scope["returned_refs"][1] = deal_scope["records"][1]["ref"]
        self.assertEqual(model_view(seen[0][0], (deal_scope,))[1][0]["records"][1][
            "fields"]["subject_scope_ref"], "deal")
        with self.assertRaises(ValueError):
            model_view({k:v for k,v in seen[0][0].items() if k !=
                "policy_hit_view_version"}, seen[0][1])
        bad = deepcopy(seen[0][1][0])
        bad["records"][0]["fields"]["condition_json"] = {"invented": True}
        with self.assertRaises(ValueError):
            model_view(seen[0][0], (bad,))
        for field, value in (("result", "not_triggered"), ("result", "unknown"),
                             ("rule_id", "PO-FORGED"), ("subject_scope_ref", "deal_line:OTHER")):
            altered_view = deepcopy(seen[0][1][0])
            altered_view["records"][1]["fields"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                model_view(seen[0][0], (altered_view,))
        hit = richer[1]
        for ref, field, value in ((hit["ref"], "result", "not_triggered"),
                                  (hit["ref"], "result", "unknown"),
                                  ("policy_hit:FORGED", "result", "triggered"),
                                  (hit["ref"], "prerequisites_met", True),
                                  (hit["ref"], "underlying_evidence_ref", "invented")):
            with self.subTest(ref=ref, field=field, value=value), self.assertRaises(ValueError):
                _claims({"kind": "finding", "claims": [{"ref": ref,
                    "field": field, "value": value}]}, seen[0][1])
        with self.assertRaises(ValueError):
            _claims({"kind": "finding", "claims": [{"ref": hit["ref"],
                "field": "result", "value": "triggered"}]}, [{**seen[0][1][0],
                    "returned_refs": [richer[0]["ref"]]}])

    def test_policy_missing_hit_and_changed_source_fail_closed(self):
        from langgraph.checkpoint.memory import InMemorySaver
        graph, config, before = self.original(InMemorySaver(), "M5-POLICY-NO-HIT-N03", "N03")
        pinned = pinned_from_state(before)
        pool = self.adapter.validate_pinned_context(pinned)
        self.assertEqual(_project(pool, before, pinned.context, "policy",
                                  include_policy_hits=True), [])
        # Zero hits is neither proof of a pass nor a rule-level unknown.
        with self.assertRaises(ValueError):
            _claims({"kind": "finding", "claims": [{"ref": "policy_hit:invented",
                "field": "result", "value": "not_triggered"}]}, [{"execution":
                "completed", "records": [], "returned_refs": []}])
        graph, config, before = self.original(InMemorySaver(), "M5-POLICY-ADVERSE-B01")
        pinned = pinned_from_state(before)
        pool = self.adapter.validate_pinned_context(pinned)
        altered = deepcopy(before)
        altered["specialist_results"]["policy"]["payload"]["rule_hits"][0][
            "severity"] = "blocker"
        with self.assertRaises(EvidenceMismatch):
            _project(pool, altered, pinned.context, "policy", include_policy_hits=True)
        bad_pool = deepcopy(pool)
        bad_pool["rules"]["policy_rules"] = []
        with self.assertRaises(EvidenceMismatch):
            _project(bad_pool, before, pinned.context, "policy", include_policy_hits=True)
        with self.assertRaises(EvidenceMismatch):
            _project(pool, before, type("WrongContext", (), {**vars(pinned.context),
                "original_deal_id": "OTHER"})(), "policy", include_policy_hits=True)
        altered = deepcopy(before)
        altered["specialist_results"]["policy"]["payload"]["rule_hits"][0][
            "scope"] = "M18-L-B02"
        with self.assertRaises(EvidenceMismatch):
            _project(pool, altered, pinned.context, "policy", include_policy_hits=True)

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
            self.assertEqual({value["prompt_version"] for value in state[
                "m21_ai_results"].values()}, {PROMPT_VERSION})
            self.assertEqual({attempt["prompt_version"] for attempt in state[
                "m21_model_attempts"]}, {PROMPT_VERSION})
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
            graph.update_state(config, {"m21_model_attempts": [
                {**attempts[0], "prompt_version": VERSION}]}, as_node="finish")
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
