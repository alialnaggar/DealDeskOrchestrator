"""Default-deny, original-only tool scopes assigned by the trusted caller."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

from .contracts import RunContextV1


PERMISSION_VERSION = "m1.2-v1"
MAX_RECORDS = 25
MAX_CALLS = 12
FORWARD_DAYS = 30
SPECIALIST_TOOLS = {
    "configuration": frozenset(),
    "pricing": frozenset(),
    "fulfillment": frozenset(("inspect_line_supply", "inspect_fulfillment_paths",
                              "inspect_evidence_record")),
    "credit": frozenset(),
    "policy": frozenset(),
    "approval_routing": frozenset(),
}
SOURCE_FIELDS = {
    "inventory": ("inventory", "inventory_id"),
    "inbound_supply": ("inbound_supply", "supply_id"),
    "supplier_offer": ("supplier_offers", "supplier_item_id"),
    "shipping_lane": ("shipping_lanes", "lane_id"),
}


class AuthorizationDenied(PermissionError):
    pass


@dataclass(frozen=True)
class TrustedToolScope:
    """Constructed by the Orchestrator, never deserialized from model arguments."""

    context: RunContextV1
    specialist: Literal["configuration", "pricing", "fulfillment", "credit", "policy", "approval_routing"]
    subject_id: str
    customer_id: str
    line_ids: frozenset[str]
    source_categories: frozenset[str]
    permission_version: str = PERMISSION_VERSION

    def check(self, *, tool: str, context: RunContextV1, subject_id: str,
              customer_id: str, line_id: str | None = None,
              source_category: str | None = None, horizon: date | None = None,
              requested_date: date | None = None) -> None:
        if (self.permission_version != PERMISSION_VERSION or self.context != context
                or self.subject_id != subject_id or self.customer_id != customer_id
                or self.subject_id != context.original_deal_id
                or tool not in SPECIALIST_TOOLS.get(self.specialist, ())):
            raise AuthorizationDenied("Tool, identity or pinned context not authorized")
        if line_id is not None and line_id not in self.line_ids:
            raise AuthorizationDenied("Line outside authorized scope")
        if source_category is not None and source_category not in self.source_categories:
            raise AuthorizationDenied("Source category outside authorized scope")
        if horizon is not None and (requested_date is None or horizon < requested_date
                                    or horizon > requested_date + timedelta(days=FORWARD_DAYS)):
            raise AuthorizationDenied("Forward investigation horizon exceeded")
