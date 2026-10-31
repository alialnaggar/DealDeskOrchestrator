"""Produce reviewer-only technical recommendations from pinned exported packets.

Pass the 73-file PostgreSQL evaluation export directory with --packets.
This generator never imports author outcomes, draft answers or acceptance.
"""
import argparse
import json
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--packets", type=Path, required=True)
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
ROOT = Path(__file__).resolve().parent
PACKETS = args.packets
INDEX = json.loads((PACKETS / "packet_index.json").read_bytes())
SCOPE = json.loads((ROOT / "credit-evidence-v3/credit_scope_v3.json").read_bytes())
V3_INDEX = json.loads((ROOT / "credit-evidence-v3/index.json").read_bytes())

def digest(o):
    return sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def finding(label, text, *refs):
    return {"technical_recommendation": label, "source_basis": text,
            "source_pointers": list(refs)}

def cohort(n):
    return next(i for i, (lo, hi) in enumerate(((1,2),(3,4),(5,6),(7,8),(9,10),
        (11,12),(13,14),(15,16),(17,18),(19,20),(21,22),(23,24),(25,26),
        (27,28),(29,30),(31,32),(33,34),(35,36))) if lo <= n <= hi)

AVAIL = [
    ("no_issue_identified", "Fresh free stock supports the submitted quantity subject to dispatch confirmation."),
    ("issue_identified", "All observed stock is allocated; the submitted delivery needs a changed proposal or new evidence."),
    ("evidence_needed", "The stock observation is stale; refresh before claiming availability or shortage."),
    ("no_issue_identified", "Confirmed receipt supports a dated route; the separate offer is uncommitted."),
    ("human_review_required", "Only an uncommitted offer supports a possible route; obtain supplier and dispatch commitments."),
    ("human_review_required", "Cancelled receipt is unusable; a separate offer needs a new commitment."),
    ("human_review_required", "Materials and capacity are observed, but no workshop or dispatch slot is booked."),
    ("human_review_required", "Alternate component receipt needs exact BOM choice and workshop/dispatch commitments."),
    ("evidence_needed", "Workshop capacity is stale; current capacity cannot be inferred."),
    ("human_review_required", "Late confirmed PO is not the requested route; earlier offer and workshop route need commitments."),
    ("no_issue_identified", "Binding digital pool and separate full-term proof support only a proposed activation."),
    ("evidence_needed", "Pool reference without separate matching provider proof is insufficient."),
    ("evidence_needed", "Provider proof does not cover the full anniversary term."),
    ("human_review_required", "Regional coverage is eligible but no service appointment is booked."),
    ("issue_identified", "Regional service rule is ineligible for the submitted destination."),
    ("no_issue_identified", "Stock appears fresh; the separate credit cap controls the overall gate."),
    ("no_issue_identified", "Stock appears fresh; the separate price floor controls the overall gate."),
    ("no_issue_identified", "Stock appears fresh; the legal clause controls review routing."),
]
GATES = ["approval_required","needs_revision","needs_evidence","approval_required",
         "needs_commitment","needs_commitment","needs_commitment","needs_commitment",
         "needs_evidence","needs_commitment","approval_required","needs_evidence",
         "needs_evidence","needs_commitment","needs_revision","blocked","blocked",
         "approval_required"]

if digest(INDEX) != "7deac5b7a9337a49e3a64b60ca99cd1c0118bb9cfa61ea9abe73b3cacfa444dc":
    raise ValueError("v2 index differs")
if sha256((ROOT / "credit-evidence-v3/credit_scope_v3.json").read_bytes()).hexdigest() != V3_INDEX["credit_scope_sha256"]:
    raise ValueError("v3 scope differs")
if len(INDEX["cases"]) != len(SCOPE["cases"]) != 36:
    raise ValueError("36 cases required")

out = []
for n, (pin, scoped) in enumerate(zip(INDEX["cases"], SCOPE["cases"]), 1):
    cid = f"EVAL-PREP-{n:03d}"
    if pin["case_id"] != cid or scoped["case_id"] != cid:
        raise ValueError("case ID mismatch")
    pb = (PACKETS / f"{cid}.json").read_bytes()
    provider = (PACKETS / f"{cid}-provider.json").read_bytes()
    packet = json.loads(pb)
    p, s = packet["payload"], packet["payload"]["source_rows"]
    if (packet["sha256"] != pin["packet_sha256"] or digest(p) != pin["packet_sha256"]
            or sha256(provider).hexdigest() != pin["provider_file_sha256"]
            or pin["packet_sha256"] != scoped["base_packet_sha256"]
            or pin["provider_file_sha256"] != scoped["base_provider_file_sha256"]
            or digest(scoped) != V3_INDEX["cases"][n-1]["scope_sha256"]
            or p["case_id"] != cid or p["run_context"]["as_of_at"] != scoped["as_of_at"]
            or p["run_context"]["run_id"] != scoped["run_id"]
            or s["credit"]["customer_id"] != scoped["customer_id"]
            or s["receivables"] or s["payments"]
            or scoped["credit_evidence_scope"]["completeness"] != "declared_complete_zero"):
        raise ValueError(f"{cid}: packet, provider or v3 source differs")
    i = cohort(n)
    line, credit = s["lines"][0], s["credit"]
    q = Decimal(str(line["quantity"]))
    quote = q * Decimal(line["quoted_unit_price"])
    list_total = q * Decimal(line["list_price"])
    cost = q * Decimal(line["standard_cost"])
    margin = (quote-cost)/quote*100
    exposure = quote + Decimal(credit["unbilled_committed_amount"])
    availability = AVAIL[i]
    if n == 20:
        availability = ("human_review_required",
            "Ali's recorded conditional modal route is a review assumption; maximum lead and October PO do not establish requested-date capacity.")
    conf = finding("no_issue_identified" if i not in (14,) else "requires_adjudication",
                   "Check submitted product, selected options, version and dependencies; ineligible service attribution needs a reviewer choice." if i==14
                   else "Submitted line and version inspected; no generic dependency row in this original case.",
                   "packet:/source_rows/lines/0", "packet:/source_rows/compatibility")
    pricing = finding("issue_identified" if i==16 else "no_issue_identified",
                      f"Quantity {q:g}; quote EUR {quote:.2f}, list EUR {list_total:.2f}, standard cost EUR {cost:.2f}, quoted gross margin {margin:.2f}%. "
                      + ("Hard category margin floor requires deterministic rule confirmation." if i==16 else "Check active pricing thresholds before final disposition."),
                      "packet:/source_rows/lines/0", "packet:/source_rows/rules/pricing_rules")
    av_refs = ["packet:/source_rows/deal", "packet:/run_context/as_of_at"]
    av_refs += (["packet:/source_rows/digital_capacity", "provider:/records"] if 10<=i<=12
                else ["packet:/source_rows/compatibility"] if 13<=i<=14
                else ["packet:/source_rows/inventory", "packet:/source_rows/inbound_supply",
                      "packet:/source_rows/supplier_offers", "packet:/source_rows/production_capacity",
                      "packet:/source_rows/shipping_lanes"])
    avail = finding(*availability, *av_refs)
    cr = finding("issue_identified" if i==15 else "no_issue_identified",
                 f"v3 fictional complete-zero AR/payment scope for this customer/cutoff; quote EUR {quote:.2f} + commitments EUR {Decimal(credit['unbilled_committed_amount']):.2f} = exposure EUR {exposure:.2f}, limit EUR {Decimal(credit['credit_limit']):.2f}. "
                 + ("Exposure exceeds the credit cap; blocked route requires verification." if i==15 else "No real-world zero-balance or favorable-payment-history claim."),
                 "packet:/source_rows/credit", "packet:/source_rows/receivables",
                 "packet:/source_rows/payments", "scope:/credit_evidence_scope")
    policy = finding("issue_identified" if i in (15,16,17) else "requires_adjudication",
                     ("Check credit cap, hard price floor or legal-review clause against the compiled predicates."
                      if i in (15,16,17) else
                      "Check compiled policy predicates and avoid duplicating an Availability limitation as a separate policy finding."),
                     "packet:/source_rows/rules/policy_rules", "packet:/source_rows/deal/terms_json")
    approval = finding("human_review_required",
                       ("Blocked proposal has no executable approval route; retain conditional human actions only."
                        if i in (15,16) else
                        "A human route is conditional on resolving evidence, revision and commitments; no approval has been granted."),
                       "packet:/source_rows/rules/approval_rules",
                       "packet:/source_rows/deal/terms_json")
    roles = {"Configuration":conf,"Pricing":pricing,
             "Availability":avail,"Credit":cr,"Policy":policy,"Approval":approval}
    documents = {"packet":p, "provider":json.loads(provider), "scope":scoped}
    for role in roles.values():
        for ref in role["source_pointers"]:
            document, pointer = ref.split(":", 1)
            value = documents[document]
            for part in pointer.lstrip("/").split("/"):
                value = value[int(part)] if isinstance(value, list) else value[part]
    out.append({"case_id":cid,"v2_packet_sha256":pin["packet_sha256"],
        "v2_provider_file_sha256":pin["provider_file_sha256"],
        "v3_scope_sha256":V3_INDEX["cases"][n-1]["scope_sha256"],
        "archetype":scoped["archetype_id"],
        "six_responsibilities":roles,
        "overall_technical_gate_proposal":GATES[i],
        "unresolved_review":("Case 020 modal route is an author business interpretation, not acceptance."
                           if n==20 else
                           "Specialist findings, exact rule IDs, negative evidence and action wording require accountable review."),
        "acceptance_recommendation":"hold_for_accountable_case_level_review"})

result={"schema_version":1,"status":"model_assisted_source_first_technical_recommendations_not_accepted_answers",
    "review_provenance":{"method":"model_assisted","source":"pinned v2 PostgreSQL export and provisional v3 Credit scope",
      "reviewed_at":"2026-10-30","independent_human_adjudication":False},
    "base_v2_index_sha256":digest(INDEX),
    "v3_credit_scope_sha256":V3_INDEX["credit_scope_sha256"],
    "original_case_count":36,"accepted_answers":0,"cases":out}
target=ROOT/"reviews/v3_six_responsibility_technical_matrix.json"
rendered = json.dumps(result, indent=2, sort_keys=True)+"\n"
if args.check:
    if target.read_text() != rendered:
        raise ValueError("Tracked technical matrix differs from pinned sources")
else:
    target.write_text(rendered)
print(f"{len(out)} cases, {sum(len(x['six_responsibilities']) for x in out)} role recommendations, {target.stat().st_size} bytes")
