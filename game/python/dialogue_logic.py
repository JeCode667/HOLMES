# Simple dialogue processing for prototype input
from renpy.store import (
    _dialogue_feedback,
    get_dialogue_feedback_text,
    get_dialogue_keywords,
)


def _normalize_keywords(keywords):
    cleaned = []
    for kw in keywords or []:
        if not isinstance(kw, str):
            continue
        kw = kw.strip().lower()
        if kw:
            cleaned.append(kw)
    return cleaned


def process_input(text, target_id):
    """Evaluate player input against configured keywords."""

    text_value = (text or "").strip()
    if not text_value:
        feedback = "No input provided."
        _dialogue_feedback[0] = feedback
        return False, feedback

    lowered = text_value.lower()
    keywords = _normalize_keywords(get_dialogue_keywords(target_id))
    matched = sorted({kw for kw in keywords if kw in lowered})

    if matched:
        base_feedback = get_dialogue_feedback_text(target_id, success=True)
        if base_feedback:
            feedback = base_feedback
        else:
            feedback = "Strong response. You referenced key details."
        feedback = f"{feedback} (matched: {', '.join(matched)})"
        _dialogue_feedback[0] = feedback
        return True, feedback

    base_failure = get_dialogue_feedback_text(target_id, success=False)
    feedback = base_failure or "Response received. Try citing the relevant clues."
    _dialogue_feedback[0] = feedback
    return False, feedback