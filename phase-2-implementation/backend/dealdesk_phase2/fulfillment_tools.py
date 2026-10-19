"""Bounded read-only projections of the sealed Phase 1C original reader pool.

No tool derives a new quantity, delivery date, binding classification or
candidate result. The graph/checkpointer is the trusted call-budget ledger.
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from .graph_state import pinned_from_state
from .phase1c_adapter import EvidenceMismatch, Phase1CAdapter
from .tool_ledger import complete, entries, reserve, was_returned
from .tool_permissions import (AuthorizationDenied, FORWARD_DAYS, MAX_RECORDS,
                               SOURCE_FIELDS, TrustedToolScope)


def _json(value):
    if isinstance(value, dict):
        return {str(key): _json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json(item) for item in value]
    if isinstance(value, (date, datetime, time, UUID, Decimal)):
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError("Unsupported evidence projection value")


def _record(category, row, fields):
    _, id_field = SOURCE_FIELDS[category]
    return {"category": category, "id": str(row[id_field]),
            "fields": _json({key: row[key] for key in fields if key in row})}


PROJECTIONS = {
    "inventory": ("inventory_id", "product_id", "location_id", "quantity_on_hand",
                  "quantity_allocated", "snapshot_at"),
    "inbound_supply": ("supply_id", "product_id", "location_id", "quantity",
                       "quantity_allocated", "expected_date", "status", "confirmed_at",
                       "valid_until", "purchase_order_id", "po_status", "po_confirmed_at",
                       "destination_location_id", "evidence_ref"),
    "supplier_offer": ("supplier_item_id", "supplier_id", "product_id", "lead_days_min",
                       "lead_days_mode", "lead_days_max", "valid_from", "valid_to",
                       "order_calendar_json"),
    "shipping_lane": ("lane_id", "origin_location_id", "destination_country_code",
                      "destination_region", "shipping_service_code", "cutoff_local_time",
                      "origin_time_zone", "dispatch_weekdays_json", "transit_workdays"),
}


class FulfillmentTools:
    """One trusted, sequential tool session attached to a completed M1.1 graph."""

    def __init__(self, graph, config: dict, adapter: Phase1CAdapter,
                 scope: TrustedToolScope):
        self.graph, self.config, self.adapter, self.scope = graph, config, adapter, scope

    def _pool(self):
        state = self.graph.get_state(self.config).values
        pinned = pinned_from_state(state)
        pool = self.adapter.validate_pinned_context(pinned)
        entries(self.graph, self.config, pinned.context.assessment_id,
                pinned.context.bundle_sha256)
        return pool, pinned.context

    def _line(self, pool, line_id):
        line = next((x for x in pool["lines"] if x["deal_line_id"] == line_id), None)
        if line is None:
            raise AuthorizationDenied("Line does not belong to pinned deal")
        fact = next((x for x in pool["facts"]["lines"] if x["line_id"] == line_id), None)
        if fact is None:
            raise EvidenceMismatch("Pinned line has no fixed finding")
        return line, fact

    def _check_sources(self, records):
        if any(record["category"] not in self.scope.source_categories for record in records):
            raise AuthorizationDenied("Returned source category outside specialist scope")

    def _invoke(self, tool, call_id, args, work):
        if not isinstance(call_id, str) or not call_id or len(call_id) > 100:
            raise ValueError("Trusted call ID required")
        # Never take identity or specialist name from the tool arguments.
        pool, actual_context = self._pool()
        context = actual_context
        claim = {"tool": tool, "context": actual_context,
                 "subject_id": context.original_deal_id,
                 "customer_id": pool["deal"]["customer_id"]}
        try:
            self.scope.check(**claim, line_id=args.get("line_id"),
                             source_category=args.get("source_category"),
                             horizon=args.get("horizon"),
                             requested_date=pool["deal"].get("requested_delivery_date"))
            authorized = True
        except AuthorizationDenied:
            authorized = False
        # Args in the ledger are canonical primitives, excluding raw records.
        recorded_args = _json(args)
        digest = context.bundle_sha256
        identity = {"assessment_id": context.assessment_id,
                    "phase1c_run_id": str(context.phase1c_run_id),
                    "subject_id": context.original_deal_id,
                    "customer_id": pool["deal"]["customer_id"],
                    "bundle_sha256": digest, "source_input_digest": context.source_input_digest,
                    "specialist": self.scope.specialist,
                    "permission_version": self.scope.permission_version,
                    "allowed_lines": sorted(self.scope.line_ids),
                    "allowed_sources": sorted(self.scope.source_categories)}
        event, prior = reserve(self.graph, self.config, context.assessment_id,
                               digest, call_id, tool, recorded_args, identity)
        if event == "budget_exhausted":
            return {"version": "1", "tool": tool, "execution": "budget_exhausted",
                    "evidence": None, "records": [], "returned_refs": [],
                    "gaps": ["Twelve-call investigation ceiling reached"]}
        if prior is not None:
            if prior["status"] == "completed":
                return prior["result"]
            # The reservation was checkpointed but not completed; never
            # reexecute an interrupted invocation or create citations for it.
            return {"version": "1", "tool": tool, "execution": "technical_failure",
                    "evidence": None, "records": [], "returned_refs": [],
                    "gaps": ["Previously reserved call interrupted; budget remains consumed"]}
        if not authorized:
            result = self._result(tool, "authorization_denied", None,
                                  gaps=["Tool or record scope denied"])
        else:
            try:
                result = work(pool)
            except AuthorizationDenied:
                result = self._result(tool, "authorization_denied", None,
                                      gaps=["Source was not previously exposed within this line scope"])
            except EvidenceMismatch:
                # Corrupted source identity stops; reserved budget stays spent.
                raise
            except Exception as exc:
                result = self._result(tool, "technical_failure", None,
                                      gaps=[type(exc).__name__])
        complete(self.graph, self.config, context.assessment_id, digest, call_id, result)
        return result

    @staticmethod
    def _result(tool, execution="completed", evidence="eligible_binding", *,
                records=None, findings=None, gaps=None, more=False):
        records = records or []
        return {"version": "1", "tool": tool, "execution": execution,
                "evidence": evidence, "records": records, "findings": findings or {},
                "returned_refs": [f"{r['category']}:{r['id']}" for r in records],
                "gaps": gaps or [], "more_in_sealed_pool": more}

    def inspect_line_supply(self, *, call_id: str, line_id: str,
                            horizon: date | None = None) -> dict:
        args = {"line_id": line_id, "horizon": horizon}

        def work(pool):
            line, fact = self._line(pool, line_id)
            mode = line["fulfillment_mode"]
            if mode not in ("stocked_finished", "supplier_finished"):
                return self._result("inspect_line_supply", evidence="unsupported_capability",
                                    gaps=["M1.2 physical finished-line projection only"])
            product = line["product_id"]
            requested = pool["deal"]["requested_delivery_date"]
            end = horizon or requested + timedelta(days=FORWARD_DAYS)
            selected = []
            for category in ("inventory", "inbound_supply", "supplier_offer"):
                rows = pool[SOURCE_FIELDS[category][0]]
                for row in rows:
                    if row["product_id"] != product:
                        continue
                    if category == "inbound_supply" and row["expected_date"] > end:
                        continue
                    selected.append(_record(category, row, PROJECTIONS[category]))
            locations = {r["fields"]["location_id"] for r in selected
                         if r["category"] in ("inventory", "inbound_supply")}
            for lane in pool["shipping_lanes"]:
                if lane["origin_location_id"] in locations:
                    selected.append(_record("shipping_lane", lane, PROJECTIONS["shipping_lane"]))
            self._check_sources(selected)
            selected.sort(key=lambda r: (r["category"], r["id"]))
            exposed, more = selected[:MAX_RECORDS], len(selected) > MAX_RECORDS
            supply = pool["facts"]["supply"]
            stock = supply["stock"].get(product, [])
            binding = supply["binding_receipts"].get(product, [])
            offer_ids = {r["id"] for r in exposed if r["category"] == "supplier_offer"}
            if more:
                status = "discovery_limit"
            elif (any(str(s["id"]) in {r["id"] for r in exposed if r["category"] == "inbound_supply"}
                      for s in binding)
                  or any(s["fresh"] and s["free"] > 0 and
                         str(s["id"]) in {r["id"] for r in exposed if r["category"] == "inventory"}
                         for s in stock)):
                status = "eligible_binding"
            elif offer_ids or stock or any(r["category"] == "inbound_supply" for r in exposed):
                status = "insufficient_or_conditional"
            else:
                status = "no_eligible_evidence"
            exposed_stock_ids = {r["id"] for r in exposed if r["category"] == "inventory"}
            exposed_supply_ids = {r["id"] for r in exposed if r["category"] == "inbound_supply"}
            return self._result("inspect_line_supply", evidence=status, records=exposed,
                                findings={"line_id": line_id, "product_id": product,
                                          "requested_date": _json(requested),
                                          "fixed_fulfillment_status": fact.get("fulfillment_status"),
                                          "fixed_stock": _json([x for x in stock if str(x["id"]) in exposed_stock_ids]),
                                          "fixed_binding_receipts": _json([x for x in binding if str(x["id"]) in exposed_supply_ids]),
                                          "offer_is_commitment": False},
                                gaps=["Results only cover Phase 1C's selected reader pool"]
                                + (["Some selected records were withheld by response limit"] if more else []),
                                more=more)

        return self._invoke("inspect_line_supply", call_id, args, work)

    def inspect_fulfillment_paths(self, *, call_id: str, line_id: str,
                                  horizon: date | None = None) -> dict:
        args = {"line_id": line_id, "horizon": horizon}

        def work(pool):
            line, fact = self._line(pool, line_id)
            if line["fulfillment_mode"] not in ("stocked_finished", "supplier_finished"):
                return self._result("inspect_fulfillment_paths", evidence="unsupported_capability",
                                    gaps=["No M1.2 physical finished-line path mapping for mode"])
            requested = pool["deal"]["requested_delivery_date"]
            end = horizon or requested + timedelta(days=FORWARD_DAYS)
            options = [x for x in fact.get("shipping_options", [])
                       if x.get("arrival") is not None and x["arrival"] <= end]
            offers = [x for x in pool["supplier_offers"] if x["product_id"] == line["product_id"]]
            # Do not synthesize any shipping or supplier dates. Phase 1C
            # derives offer estimates only when there are no binding options.
            estimates = fact.get("supplier_offer_estimates", [])
            records = []
            sources = {(category, str(identifier)) for option in options
                       for category, identifier in (
                           [("inventory", option["stock_id"])] if option.get("stock_id") else [])
                       + [("inbound_supply", x) for x in option.get("supply_ids", [])]}
            sources.update(("supplier_offer", str(x["supplier_item_id"])) for x in offers)
            for category, source_id in sorted(sources):
                table, key = SOURCE_FIELDS[category]
                row = next((r for r in pool[table] if str(r[key]) == source_id
                            and r["product_id"] == line["product_id"]), None)
                if row is None:
                    raise EvidenceMismatch("Fixed path references unavailable selected source")
                records.append(_record(category, row, PROJECTIONS[category]))
            self._check_sources(records)
            more = (len(records) > MAX_RECORDS or len(options) > MAX_RECORDS
                    or len(estimates) > MAX_RECORDS)
            exposed = records[:MAX_RECORDS]
            permitted_refs = {f"{r['category']}:{r['id']}" for r in exposed}
            visible_options = [x for x in options if
                               (not x.get("stock_id") or f"inventory:{x['stock_id']}" in permitted_refs)
                               and all(f"inbound_supply:{i}" in permitted_refs for i in x.get("supply_ids", []))]
            visible_options = visible_options[:MAX_RECORDS]
            mixed = bool(options and offers)
            if more:
                status = "discovery_limit"
            elif mixed:
                status = "unsupported_capability"
            elif options:
                status = "eligible_binding"
            elif offers:
                status = "insufficient_or_conditional"
            else:
                status = "no_eligible_evidence"
            gaps = ["Selected reader pool only"]
            if mixed:
                gaps.append("Phase 1C has no fixed combined binding-plus-offer path")
            if offers and not estimates:
                gaps.append("No Phase 1C conditional estimate is available for these offers")
            if more:
                gaps.append("Path/source response truncated; no completeness claim")
            return self._result("inspect_fulfillment_paths", evidence=status, records=exposed,
                                findings={"line_id": line_id, "fixed_status": fact.get("fulfillment_status"),
                                          "requested_date": _json(requested),
                                          "quantity_by_requested_date": None if more else
                                          _json(fact.get("quantity_by_requested_date")),
                                          "binding_options": _json(visible_options),
                                          "conditional_estimates": _json(estimates[:MAX_RECORDS])
                                          if not more else [],
                                          "confirmed_mixed_path": False}, gaps=gaps, more=more)

        return self._invoke("inspect_fulfillment_paths", call_id, args, work)

    def inspect_evidence_record(self, *, call_id: str, line_id: str,
                                source_category: str, source_id: str) -> dict:
        args = {"line_id": line_id, "source_category": source_category, "source_id": source_id}

        def work(pool):
            line, _ = self._line(pool, line_id)
            context = self.scope.context
            if source_category not in SOURCE_FIELDS or not was_returned(
                    self.graph, self.config, context.assessment_id,
                    context.bundle_sha256, source_category, source_id, line_id):
                raise AuthorizationDenied("Evidence was not exposed by an authorized tool")
            table, key = SOURCE_FIELDS[source_category]
            selected = [r for r in pool[table] if str(r[key]) == source_id]
            if source_category != "shipping_lane":
                selected = [r for r in selected if r["product_id"] == line["product_id"]]
            else:
                locations = {r["location_id"] for name in ("inventory", "inbound_supply")
                             for r in pool[name] if r["product_id"] == line["product_id"]}
                selected = [r for r in selected if r["origin_location_id"] in locations]
            if len(selected) != 1:
                raise AuthorizationDenied("Source is not unique and line-scoped in the sealed pool")
            record = _record(source_category, selected[0], PROJECTIONS[source_category])
            fixed = pool["facts"]["supply"]
            if source_category == "inventory":
                proof = next((x for x in fixed["stock"].get(line["product_id"], [])
                              if str(x["id"]) == source_id), None)
                status = "eligible_binding" if proof and proof["fresh"] and proof["free"] > 0 \
                    else "insufficient_or_conditional"
            elif source_category == "inbound_supply":
                status = "eligible_binding" if any(
                    str(x["id"]) == source_id for x in fixed["binding_receipts"].get(
                        line["product_id"], [])) else "insufficient_or_conditional"
            else:
                status = "insufficient_or_conditional"
            return self._result("inspect_evidence_record", records=[record],
                                evidence=status,
                                findings={"source_identity_only": True,
                                          "business_classification_requires_fixed_findings": True})

        return self._invoke("inspect_evidence_record", call_id, args, work)
