"""The heart of the backend: ask Gemma for a mission, check it, retry once, else fall back.

Flow (spec section 9):
  1. Ask Gemma (via Ollama) for a mission as JSON.
  2. Validate structure + design rules + safety.
  3. If invalid, retry ONCE with a message listing exactly what was wrong.
  4. If still invalid (or Ollama is down/slow), return a safe hand-written mission.
"""
import logging
import random
from typing import Dict, List, Optional

from .. import config
from ..models.mission import MissionResult
from ..prompts.mission_prompt import (
    MISSION_JSON_SCHEMA,
    LENSES,
    SYSTEM_PROMPT,
    build_correction_prompt,
    build_user_prompt,
)
from . import ollama_client
from .fallback import build_fallback_mission
from .validation import MissionValidationError, extract_json, validate_mission

log = logging.getLogger("offline.generator")


def _fallback(time_minutes: int, need: str, reason: str, retried: bool = False) -> MissionResult:
    log.warning("Using fallback mission (reason=%s)", reason)
    return MissionResult(
        mission=build_fallback_mission(time_minutes, need),
        source="fallback",
        model=None,
        retried=retried,
        fallback_reason=reason,
    )


async def generate_mission(
    time_minutes: int, need: str, environment: str = "unsure", lens: Optional[str] = None
) -> MissionResult:
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(time_minutes, need, environment, lens or random.choice(LENSES))},
    ]

    retried = False
    for attempt in (1, 2):
        try:
            raw = await ollama_client.chat(messages, schema=MISSION_JSON_SCHEMA)
        except ollama_client.OllamaError as err:
            # Unavailable, model missing, or too slow: no point retrying.
            return _fallback(time_minutes, need, err.code, retried)

        try:
            mission = validate_mission(extract_json(raw), time_minutes)
            return MissionResult(
                mission=mission,
                source="gemma",
                model=config.OFFLINE_MODEL,
                retried=retried,
            )
        except MissionValidationError as err:
            log.info("Attempt %d rejected: %s", attempt, err.problems)
            if attempt == 2:
                return _fallback(time_minutes, need, "invalid_output", retried=True)
            retried = True
            messages = messages + [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": build_correction_prompt(err.problems)},
            ]

    return _fallback(time_minutes, need, "invalid_output", retried=True)  # pragma: no cover
