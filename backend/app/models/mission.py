"""Plain data classes for a mission. No framework needed."""
from dataclasses import dataclass, field, asdict
from typing import List, Optional

# The only values the app accepts from the check-in screen.
TIME_OPTIONS = (15, 30, 60, 90)
NEED_OPTIONS = ("clear_head", "explore", "move", "be_alone", "surprise")
ENVIRONMENT_OPTIONS = ("unsure", "city", "park", "suburb", "countryside")

# Human-readable text used inside the AI prompt.
NEED_DESCRIPTIONS = {
    "clear_head": "Clear my head (calm, slow, sensory, low-effort)",
    "explore": "Explore (curiosity, noticing new corners of somewhere familiar)",
    "move": "Move (gently active walking; never strenuous or risky)",
    "be_alone": "Be alone (quiet, solitary, in ordinary public places only)",
    "surprise": "Surprise me (playful and unexpected, but still safe)",
}
ENVIRONMENT_DESCRIPTIONS = {
    "unsure": "not specified; assume ordinary public streets, paths or green spaces",
    "city": "a city or town with streets, pavements and small public spaces",
    "park": "a park or other public green space",
    "suburb": "a suburban neighbourhood with residential streets",
    "countryside": "countryside or a small village with public footpaths",
}


@dataclass
class Step:
    number: int
    instruction: str
    phone_down: bool
    duration_minutes: int


@dataclass
class Mission:
    title: str
    intro: str
    estimated_minutes: int
    steps: List[Step]
    reflection_prompt: str
    closing_message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MissionResult:
    """What the API returns: the mission plus honest info about where it came from."""

    mission: Mission
    source: str  # "gemma" or "fallback"
    model: Optional[str] = None
    retried: bool = False
    fallback_reason: Optional[str] = None  # e.g. "ollama_unavailable"
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "mission": self.mission.to_dict(),
            "source": self.source,
            "model": self.model,
            "retried": self.retried,
            "fallback_reason": self.fallback_reason,
        }
