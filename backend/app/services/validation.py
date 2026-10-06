"""Turn raw model text into a trusted Mission, or explain exactly what is wrong.

Spec section 9: "Validate the returned JSON before displaying it."
Spec section 7: encode the mission design rules in application logic where practical.
"""
import json
import re
from typing import Any, List, Tuple

from ..models.mission import Mission, Step
from .safety import find_safety_violations

MIN_STEPS, MAX_STEPS = 4, 7
MIN_PHONE_DOWN_STEPS = 2
MAX_INSTRUCTION_CHARS = 300
MAX_TITLE_CHARS = 80
MAX_INTRO_CHARS = 350


class MissionValidationError(Exception):
    """Raised when model output can't be used. `problems` is safe to show back to the model."""

    def __init__(self, problems: List[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


def extract_json(text: str) -> Any:
    """Parse JSON even if the model wrapped it in ```json fences or added chatter."""
    if not isinstance(text, str) or not text.strip():
        raise MissionValidationError(["The answer was empty."])
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            pass
    raise MissionValidationError(["The answer was not valid JSON."])


def _clean_text(value: Any) -> str:
    return " ".join(value.split()) if isinstance(value, str) else ""


def _as_int(value: Any) -> Tuple[bool, int]:
    # bool is a subclass of int in Python, so rule it out explicitly.
    if isinstance(value, bool):
        return False, 0
    if isinstance(value, int):
        return True, value
    if isinstance(value, float) and value.is_integer():
        return True, int(value)
    return False, 0


def validate_mission(data: Any, time_minutes: int) -> Mission:
    """Check the structure and the design/safety rules. Returns a clean Mission."""
    problems: List[str] = []

    if not isinstance(data, dict):
        raise MissionValidationError(["The answer must be a JSON object."])

    title = _clean_text(data.get("title"))
    intro = _clean_text(data.get("intro"))
    reflection = _clean_text(data.get("reflection_prompt"))
    closing = _clean_text(data.get("closing_message"))

    if not title:
        problems.append("title is missing.")
    elif len(title) > MAX_TITLE_CHARS:
        problems.append(f"title is longer than {MAX_TITLE_CHARS} characters.")
    if not intro:
        problems.append("intro is missing.")
    elif len(intro) > MAX_INTRO_CHARS:
        problems.append(f"intro is longer than {MAX_INTRO_CHARS} characters; keep it to 1-2 sentences.")
    if not reflection:
        problems.append("reflection_prompt is missing.")
    if not closing:
        problems.append("closing_message is missing.")
    elif "close" not in closing.lower():
        problems.append("closing_message must tell the user to close the app.")

    raw_steps = data.get("steps")
    steps: List[Step] = []
    if not isinstance(raw_steps, list):
        problems.append("steps must be a list.")
        raw_steps = []
    elif not (MIN_STEPS <= len(raw_steps) <= MAX_STEPS):
        problems.append(f"there must be {MIN_STEPS} to {MAX_STEPS} steps, but there were {len(raw_steps)}.")

    for index, raw in enumerate(raw_steps, start=1):
        if not isinstance(raw, dict):
            problems.append(f"step {index} must be an object.")
            continue
        instruction = _clean_text(raw.get("instruction"))
        phone_down = raw.get("phone_down")
        ok_minutes, minutes = _as_int(raw.get("duration_minutes"))
        if not instruction:
            problems.append(f"step {index} has no instruction.")
        elif len(instruction) > MAX_INSTRUCTION_CHARS:
            problems.append(f"step {index} is too long; use one or two short sentences.")
        if not isinstance(phone_down, bool):
            problems.append(f"step {index} phone_down must be true or false.")
        if not ok_minutes or minutes < 0 or minutes > time_minutes:
            problems.append(f"step {index} duration_minutes must be a whole number from 0 to {time_minutes}.")
        # We always renumber ourselves, so a model that miscounts doesn't matter.
        steps.append(Step(number=index, instruction=instruction, phone_down=bool(phone_down), duration_minutes=minutes))

    if steps and sum(1 for s in steps if s.phone_down) < MIN_PHONE_DOWN_STEPS:
        problems.append(f"at least {MIN_PHONE_DOWN_STEPS} steps must have phone_down true.")

    total = sum(s.duration_minutes for s in steps)
    if steps and total > time_minutes * 1.2:
        problems.append(f"step durations add up to {total} minutes, more than the {time_minutes} available.")

    # Safety screen over every piece of text the user will read.
    all_text = [title, intro, reflection, closing] + [s.instruction for s in steps]
    for text in all_text:
        for reason in find_safety_violations(text):
            problems.append(f"unsafe or off-brief content ({reason}): \"{text[:80]}\"")

    if problems:
        raise MissionValidationError(problems)

    return Mission(
        title=title,
        intro=intro,
        estimated_minutes=min(max(total, 1), time_minutes),
        steps=steps,
        reflection_prompt=reflection,
        closing_message=closing,
    )
