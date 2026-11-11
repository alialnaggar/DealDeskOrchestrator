"""Read-only Configuration format diagnostic. NEVER a correction capability.

The hosted Configuration parser discards rejected content after a broad error
category; this function is ONLY for bounded, caller-held offline test records.
It neither modifies a model result nor reserves/sends a new request.
"""

from copy import deepcopy
from hashlib import sha256
import json

from .m4_correction_policy import disposition
from .typed_final_contract import InvalidTerminal, _unique, decode

VERSION = "m4-configuration-format-diagnostic-v1"
IDENTITY = ("assessment_id", "phase1c_run_id", "subject_id",
            "bundle_sha256", "source_input_digest", "specialist")
MAX_BYTES = 8192


def diagnose_boolean_text(content, *, input, observations, expected_identity,
                          fully_returned=False, remaining_turns=0):
    """Recognize a single quoted boolean for an EXACT returned boolean field.

    A temporary normalized copy is checked using the same trusted decoder to
    rule out *other* bad citations/branches. It is discarded, never shown as
    model-authored output or used to approve a deal. Even a match stays blocked.
    """
    outcome = {"version": VERSION, "specialist": "configuration",
        "classification": "not_proven", "eligible": False,
        "reason": "no_offline_format_proof", "content_sha256": None}
    if type(content) is not str:
        return outcome
    try:
        size = len(content.encode("utf-8"))
    except UnicodeError:
        return outcome
    if (fully_returned is not True or type(remaining_turns) is not int or
            remaining_turns < 1 or size > MAX_BYTES or type(input) is not dict or
            type(expected_identity) is not dict or set(expected_identity) != set(IDENTITY) or
            any(type(expected_identity[k]) is not str or not expected_identity[k]
                or input.get(k) != expected_identity[k] for k in IDENTITY) or
            input["specialist"] != "configuration" or
            type(observations) is not tuple or len(observations) != 1 or
            type(observations[0]) is not dict or observations[0].get("execution") !=
            "completed" or type(observations[0].get("records")) is not list or
            type(observations[0].get("returned_refs")) is not list):
        return outcome
    outcome["content_sha256"] = sha256(content.encode("utf-8")).hexdigest()
    try:
        raw = json.loads(content, object_pairs_hook=_unique)
        if (type(raw) is not dict or type(raw.get("claims")) is not list or
                not 1 <= len(raw["claims"]) <= 6 or raw.get("kind") != "finding"):
            return outcome
        # Do not classify a valid terminal or rely only on a coarse error code.
        try:
            decode(content, specialist="configuration", input=input,
                   observations=observations)
        except InvalidTerminal:
            pass
        else:
            return outcome
        exposed = {record["ref"]: record["fields"] for record in observations[0]["records"]
            if type(record) is dict and type(record.get("ref")) is str and
            record["ref"] in observations[0]["returned_refs"] and
            type(record.get("fields")) is dict}
        candidates = []
        for index, claim in enumerate(raw["claims"]):
            if type(claim) is not dict or set(claim) != {"ref", "field", "value_json"} or any(
                    type(value) is not str for value in claim.values()):
                return outcome
            value = json.loads(claim["value_json"], object_pairs_hook=_unique)
            expected = exposed.get(claim["ref"], {}).get(claim["field"], object())
            if (type(expected) is bool and type(value) is str and value in ("true", "false")
                    and value == str(expected).lower()):
                candidates.append(index)
        if len(candidates) != 1:
            return outcome
        shadow = deepcopy(raw)
        index = candidates[0]
        shadow["claims"][index]["value_json"] = json.dumps(
            exposed[shadow["claims"][index]["ref"]][shadow["claims"][index]["field"]])
        decode(json.dumps(shadow, sort_keys=True), specialist="configuration",
               input=input, observations=observations)
    except (ValueError, TypeError, KeyError, UnicodeError, InvalidTerminal):
        return outcome
    # Policy is deliberately NOT expanded: a readable old response is not a
    # separately authorized, receipt-bound, budgeted new Configuration send.
    decision = disposition("configuration", "boolean_text_format", fully_returned=True,
                           remaining_turns=remaining_turns)
    return {**outcome, "classification": "boolean_text_format_candidate",
            "field_paths": [f"claims[{index}].value_json"], "eligible": decision["eligible"],
            "reason": "offline_only_no_bound_correction_receipt_or_budget"}
