"""M4 correction eligibility, not a transport or permission to send.

Only Fulfillment has an existing checkpointed revision wire and narrow fixed
failure classifier. Other stages need separately verified classification,
receipt and budget contracts before a model correction can be enabled.
"""

from .graph_state import SPECIALISTS

VERSION = "m4-correction-eligibility-v1"
ALLOWED = {"fulfillment": frozenset({"quantity_format", "quantity_sum_mismatch"})}


def disposition(specialist: str, code: str | None, *, fully_returned: bool,
                remaining_turns: int) -> dict:
    """Fail closed for every absent/unknown validation or unsafe send state."""
    if specialist not in SPECIALISTS:
        raise ValueError("Unknown specialist correction scope")
    if fully_returned is not True:
        reason = "response_not_fully_returned"
    elif type(remaining_turns) is not int or remaining_turns < 1:
        reason = "correction_budget_unavailable"
    elif type(code) is not str or code not in ALLOWED.get(specialist, ()):
        reason = "failure_not_allowlisted"
    else:
        reason = "bounded_correction_eligible"
    return {"version": VERSION, "specialist": specialist,
            "eligible": reason == "bounded_correction_eligible", "reason": reason}
