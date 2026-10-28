"""Provider-independent Pricing/Credit terminal result; no hosted capability.

The model supplies a proposed finding or abstention, never a business decision.
Returned evidence and identities must be obtained from the trusted ledger.
"""

import json

from .m20_specialists import _validate_claims
from .m21_redaction import model_view
from .m21_specialists import _claims


VERSION = "terminal-final-v1"
REASONS = ("insufficient_evidence", "model_uncertainty", "unsupported_capability")
MAX_CONTENT_BYTES = 8192


class InvalidTerminal(ValueError):
    """Fixed, non-provider diagnostic; never include arbitrary output text."""


def schema():
    """Groq strict-mode-compatible subset; branch invariants stay local."""
    return {"type": "object", "properties": {
        "version": {"type": "string", "enum": [VERSION]},
        "kind": {"type": "string", "enum": ["finding", "abstain"]},
        "claims": {"type": "array", "items": {"type": "object", "properties": {
            "ref": {"type": "string"}, "field": {"type": "string"},
            "value_json": {"type": "string"}},
            "required": ["ref", "field", "value_json"], "additionalProperties": False}},
        "uncertainty_reasons": {"type": "array", "items": {"type": "string"}},
        "reason_code": {"type": "string", "enum": ["none", *REASONS]}},
        "required": ["version", "kind", "claims", "uncertainty_reasons", "reason_code"],
        "additionalProperties": False}


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidTerminal("duplicate_json_key")
        result[key] = value
    return result


def decode(content, *, specialist, input, observations):
    """Map an exact scoped final to an existing checked specialist action.

    `observations` MUST be the already-verified completed tool-ledger results;
    the caller owns checkpoint/owner/permission binding and no-replay.
    """
    if (specialist not in ("pricing", "credit") or input.get("specialist") != specialist
            or type(observations) is not tuple or not 1 <= len(observations) <= (
                2 if specialist == "pricing" else 1) or any(type(x) is not dict
                or x.get("execution") != "completed" for x in observations)):
        raise InvalidTerminal("invalid_scoped_observations")
    try:
        if type(content) is not str or len(content.encode()) > MAX_CONTENT_BYTES:
            raise ValueError()
        raw = json.loads(content, object_pairs_hook=_unique)
        if (type(raw) is not dict or set(raw) != set(schema()["required"])
                or raw["version"] != VERSION or raw["kind"] not in ("finding", "abstain")
                or type(raw["claims"]) is not list or
                type(raw["uncertainty_reasons"]) is not list or
                raw["reason_code"] not in ("none", *REASONS)):
            raise ValueError()
        if raw["kind"] == "abstain":
            if raw["reason_code"] == "none" or raw["claims"] or raw["uncertainty_reasons"]:
                raise ValueError()
            return {"kind": "abstain", "reason_code": raw["reason_code"]}
        if raw["reason_code"] != "none" or not 1 <= len(raw["claims"]) <= 6:
            raise ValueError()
        parsed = []
        for claim in raw["claims"]:
            if (type(claim) is not dict or set(claim) != {"ref", "field", "value_json"}
                    or any(type(v) is not str for v in claim.values()) or
                    len(claim["value_json"].encode()) > 1024):
                raise ValueError()
            value = json.loads(claim["value_json"], object_pairs_hook=_unique)
            if type(value) not in (str, int, bool, type(None)):
                raise ValueError()
            parsed.append({"ref": claim["ref"], "field": claim["field"], "value": value})
        if len({(c["ref"], c["field"]) for c in parsed}) != len(parsed):
            raise ValueError()
        if specialist == "pricing":
            action = {"kind": "finding", "claims": parsed,
                      "uncertainty_reasons": raw["uncertainty_reasons"]}
            _validate_claims(action, observations, specialist)
            return action
        if raw["uncertainty_reasons"]:
            raise ValueError()
        _, visible, aliases = model_view(input, observations)
        exposed = {row["ref"]: row["fields"] for obs in visible
                   for row in obs["records"] if row["ref"] in obs["returned_refs"]}
        for claim in parsed:
            if (claim["ref"] not in aliases or claim["field"] not in exposed.get(
                    claim["ref"], {}) or type(claim["value"]) is not type(
                    exposed[claim["ref"]][claim["field"]]) or claim["value"] !=
                    exposed[claim["ref"]][claim["field"]]):
                raise ValueError()
            claim["ref"] = aliases[claim["ref"]]
        _claims({"kind": "finding", "claims": parsed}, observations)
        return {"kind": "finding", "claims": parsed}
    except (ValueError, TypeError, UnicodeError, KeyError, IndexError):
        raise InvalidTerminal("invalid_terminal_output") from None
