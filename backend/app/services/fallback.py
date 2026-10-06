"""Hand-written safe missions, used when Gemma is unavailable or keeps failing.

Spec section 9: "use a safe fallback mission rather than crashing."
They also run through the same validator as Gemma's output (see the tests),
so a fallback can never be less safe than an AI mission.
"""
from typing import List

from ..models.mission import Mission, Step

# Each template: title, intro, reflection, then (instruction, phone_down, weight) steps.
# "weight" decides how much of the available time each step gets.
_TEMPLATES = {
    "clear_head": {
        "title": "The Slow Walk",
        "intro": "You don't need to get anywhere. Walk slowly and let your head catch up with your feet.",
        "reflection": "What did you notice once you slowed down?",
        "steps": [
            ("Step outside and walk at half your normal speed. Let your arms hang loose.", True, 4),
            ("Find a place with some sky overhead. Take five slow breaths and watch the clouds, or the light.", True, 3),
            ("Listen for the furthest sound you can hear. Stay with it until it fades or changes.", True, 3),
            ("Keep walking, and notice what your hands feel: air, fabric, sun, or cold.", True, 4),
            ("Pause somewhere comfortable and safe. Look at one ordinary thing for a full minute.", False, 2),
        ],
    },
    "explore": {
        "title": "The Unfamiliar Route",
        "intro": "The goal is not to get somewhere. The goal is to notice somewhere you normally ignore.",
        "reflection": "What did you notice that you normally miss?",
        "steps": [
            ("Walk toward a street, path, or outdoor area you have not explored before, staying in public places.", True, 4),
            ("When you reach it, look for something blue. Do not search your phone for it. Just notice.", True, 2),
            ("Turn toward the most interesting sound you can hear and walk a little way toward it.", True, 3),
            ("Find something that looks older than you. Spend one minute looking at it.", False, 2),
            ("Sit or stand somewhere comfortable and safe. Notice three things you would normally walk past.", False, 3),
        ],
    },
    "move": {
        "title": "Three Turns",
        "intro": "A gentle walk with a few simple choices. Your legs set the pace, your curiosity picks the way.",
        "reflection": "What is one thing you saw along the way that you want to see again?",
        "steps": [
            ("Start walking at a comfortable pace and keep your phone in your pocket.", True, 4),
            ("At the next junction or path split, take whichever way has more trees, sky, or light.", True, 3),
            ("Repeat that choice once more. Pick the way that feels quieter than the other.", True, 4),
            ("Walk with a slightly longer stride for a minute and notice how your breathing changes.", True, 2),
            ("Slow down, turn around, and take the same way back at an easy pace.", True, 4),
        ],
    },
    "be_alone": {
        "title": "A Bench of Your Own",
        "intro": "A small quiet outing, in an ordinary public place, for no one but you.",
        "reflection": "What was it like to have this time to yourself?",
        "steps": [
            ("Head toward the nearest calm public place: a quiet path, a green corner, or a bench.", True, 3),
            ("Find somewhere comfortable where you can see what is around you. Sit or stand there.", True, 2),
            ("Close your eyes for a few breaths, if it feels comfortable, and listen to the space around you.", True, 3),
            ("Open your eyes and slowly look at the edges of what you can see, not the middle.", True, 3),
            ("Stay a few minutes more with no goal at all, and then walk home the way you like.", True, 3),
        ],
    },
    "surprise": {
        "title": "The Color Hunt",
        "intro": "Today the world is sorted by color. Go outside and see what it hands you.",
        "reflection": "Which color surprised you the most?",
        "steps": [
            ("Walk out of the door and look for something red. Notice it without taking a photo.", True, 3),
            ("Now find something round. Keep walking until you spot one.", True, 3),
            ("Look for something that is moving, but not a person or a vehicle: leaves, birds, water, or clouds.", True, 3),
            ("Find the smallest living thing you can see and watch it for one minute.", False, 2),
            ("Pick your favorite thing you have seen so far, and give it a silly name in your head.", False, 2),
        ],
    },
}

CLOSING = "You're done. Close OFFLINE."


def _scale(weights: List[int], total_minutes: int) -> List[int]:
    """Spread the available time across steps by weight, using whole minutes (at least 1)."""
    usable = max(len(weights), int(total_minutes * 0.9))  # leave a little slack
    weight_sum = sum(weights)
    minutes = [max(1, round(usable * w / weight_sum)) for w in weights]
    # Rounding can overshoot; trim from the longest step until we're inside the limit.
    while sum(minutes) > total_minutes:
        longest = minutes.index(max(minutes))
        minutes[longest] -= 1
    return minutes


def build_fallback_mission(time_minutes: int, need: str) -> Mission:
    template = _TEMPLATES.get(need, _TEMPLATES["surprise"])
    weights = [w for _, _, w in template["steps"]]
    minutes = _scale(weights, time_minutes)
    steps = [
        Step(number=i, instruction=text, phone_down=down, duration_minutes=mins)
        for i, ((text, down, _), mins) in enumerate(zip(template["steps"], minutes), start=1)
    ]
    return Mission(
        title=template["title"],
        intro=template["intro"],
        estimated_minutes=sum(minutes),
        steps=steps,
        reflection_prompt=template["reflection"],
        closing_message=CLOSING,
    )
