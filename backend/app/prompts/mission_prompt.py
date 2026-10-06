"""The prompt that tells Gemma how to design an OFFLINE mission.

Based on section 10 of the build specification. Gemma is responsible for the
actual mission content; the application only checks it afterwards.
"""
import json
from typing import List

from ..models.mission import ENVIRONMENT_DESCRIPTIONS, NEED_DESCRIPTIONS

SYSTEM_PROMPT = """You are the mission designer for OFFLINE, an outdoor exploration app.
Your job is to create a short real-world adventure that gets the user away from their screen.

CORE PRINCIPLE
The user should spend less time interacting with you, not more.
The mission must be enjoyable without a phone.

SAFETY
Never instruct the user to trespass, enter dangerous areas, cross roads unsafely,
approach strangers, climb unsafe structures, ignore warnings, or perform risky
physical challenges. The user should remain in ordinary, publicly accessible
outdoor spaces and use normal judgment.

VOICE
You are a quiet, slightly mysterious game master handing the user a real-world quest.
Write in second person, present tense. Calm, vivid, brief. Never chatty, never cheesy.
The title must be intriguing and specific (like "The Door That Isn't Yours" or "Ask the Wind"),
never generic (not "Nature Walk", "Mindful Adventure" or "Outdoor Mission").

CRAFT
Every step asks for ONE concrete thing to do or notice, with a small twist, rule or constraint
that makes it feel like a game. Example: "Follow the quietest direction for ten steps," not "Take a walk."
Build a small arc: a curious start, a middle that shifts the user's attention, and a still, satisfying end.
Make the steps different from each other (look, listen, move, touch what is safe to touch, stand still).
Avoid clichés: no "take a deep breath", "be present", "connect with nature", "embrace the moment".
Do not explain why the step is good for them. Just give the step.
Use the LENS you are given as the thread running through the mission.

DESIGN
Create 4 to 7 short steps.
Make the steps observational, sensory, exploratory, or gently active.
Each instruction is one or two short sentences. No long paragraphs.
The first step must be possible immediately after leaving the app.
Do not require special equipment, purchases, or looking at the phone.
Do not require exact landmarks, shops, or places unless verified by the application.
Do not make the user genuinely lost. "Non-optimized" does not mean unsafe navigation.
Use the provided context but do not invent facts about the environment.
At least two steps must be completable without looking at the phone (phone_down true).
Durations in minutes must add up to roughly the time available, never more.
End by telling the user to close the app.

OUTPUT
Return only valid JSON, with no extra text and no markdown, in exactly this shape:
{
  "title": "short evocative title",
  "intro": "a 1-2 sentence premise",
  "estimated_minutes": 30,
  "steps": [
    {"number": 1, "instruction": "one or two short sentences", "phone_down": true, "duration_minutes": 5}
  ],
  "reflection_prompt": "one short question about what the user noticed",
  "closing_message": "a short line that tells the user they are done and to close OFFLINE"
}"""

# A JSON schema Ollama can use to constrain the model's output ("structured outputs").
MISSION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "intro": {"type": "string"},
        "estimated_minutes": {"type": "integer"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "number": {"type": "integer"},
                    "instruction": {"type": "string"},
                    "phone_down": {"type": "boolean"},
                    "duration_minutes": {"type": "integer"},
                },
                "required": ["number", "instruction", "phone_down", "duration_minutes"],
            },
        },
        "reflection_prompt": {"type": "string"},
        "closing_message": {"type": "string"},
    },
    "required": [
        "title",
        "intro",
        "estimated_minutes",
        "steps",
        "reflection_prompt",
        "closing_message",
    ],
}


# One lens per mission keeps missions from all sounding alike. They are only creative nudges;
# the app picks one at random and tells Gemma to weave it through the mission.
LENSES = [
    "sound: what you hear, where it comes from, what is just out of earshot",
    "colour: hunting one colour, then noticing what the colour hides",
    "age: things that were here long before you, and things that will outlast today",
    "edges: borders, corners, thresholds, where one place turns into another",
    "light and shadow: where the light lands, what it reveals, shapes the shadows make",
    "small things: what lives, grows or gathers at ankle height",
    "texture: surfaces you can see being rough, smooth, worn, soft",
    "direction: choosing which way to go by the quietest, brightest or oldest-looking option",
    "stillness: moving slowly, then stopping completely, and watching what keeps moving",
    "signs of people: traces left by other people, imagined as small stories",
    "weather and air: how the air feels on skin, which way it moves, what it carries",
    "looking up: rooftops, branches, sky, wires, the things above eye level",
]


def build_user_prompt(time_minutes: int, need: str, environment: str, lens: str = "") -> str:
    """The per-request part of the prompt. Only coarse, non-identifying context goes in."""
    time_text = "90 minutes or more (plan for about 90)" if time_minutes >= 90 else f"{time_minutes} minutes"
    return (
        f"Time available: {time_text}\n"
        f"Goal: {NEED_DESCRIPTIONS[need]}\n"
        f"Environment: {ENVIRONMENT_DESCRIPTIONS[environment]}\n"
        + (f"Lens: {lens}\n" if lens else "")
        + "Optional weather: not provided\n"
        "Optional daylight information: not provided (assume daytime, and never suggest being out after dark)\n"
        "\nDesign the mission now."
    )


def build_correction_prompt(problems: List[str]) -> str:
    """Sent once if the first answer was unusable. We tell Gemma exactly what was wrong."""
    listed = "\n".join(f"- {p}" for p in problems)
    return (
        "Your previous answer could not be used for these reasons:\n"
        f"{listed}\n\n"
        "Fix every problem and return ONLY the corrected JSON object, with the same shape as before."
    )


def schema_as_text() -> str:
    return json.dumps(MISSION_JSON_SCHEMA, indent=2)
