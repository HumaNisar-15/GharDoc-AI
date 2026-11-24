"""Safety rules applied after the AI answer. They can only make the result more cautious, never less.
These rules are a first draft and should be verified by a civil engineer.
Reasons are returned as i18n keys; the app shows them in the user's language (see i18n.py)."""
import config

LEVELS = ["green", "yellow", "red"]


def _idx(level):
    return LEVELS.index(level) if level in LEVELS else 1


def apply_rules(d):
    """d: a normalized diagnosis. Returns (final_level, reason_keys, need_more_photos)."""
    level = _idx(d.get("risk_level"))
    reasons = []
    need_more = bool(d.get("need_more_photos"))
    flags = d.get("flags", {})
    issue = d.get("issue_type")

    if issue == "structural_crack":
        level = max(level, 2)
        reasons.append("r_struct")
    if flags.get("stair_step_or_diagonal"):
        level = max(level, 2)
        reasons.append("r_diag")
    if flags.get("wide_or_widening"):
        level = max(level, 2)
        reasons.append("r_wide")
    if flags.get("near_structural_element"):
        level = max(level, 1)
        reasons.append("r_near")
    if flags.get("recurring_or_spreading"):
        level = max(level, 1)
        reasons.append("r_spread")
    if issue == "pipe_leak":
        level = max(level, 1)
        reasons.append("r_pipe")

    if d.get("confidence", 0) < config.CONF_MIN or issue == "unclear":
        level = min(level + 1, 2)
        need_more = True
        reasons.append("r_lowconf")

    return LEVELS[level], reasons, need_more
