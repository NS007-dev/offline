"""A simple safety screen for mission text.

The AI prompt already asks Gemma to stay safe, but we never trust a model
alone. This module scans every piece of mission text for instructions that
break the spec's safety rules (trespassing, climbing, ignoring signs, etc.).

It is deliberately a blunt tool: if it is unsure, the mission is rejected and
we retry or use a hand-written fallback. A false alarm costs us one retry.
A miss could put someone in danger.
"""
import re
from typing import List

# If one of these appears shortly BEFORE a match, the text is telling the user
# NOT to do the thing ("Do not search your phone"), so it is fine.
_NEGATION = re.compile(
    r"(do not|don't|dont|never|without|avoid|not to|not about|isn't|is not|no need to|no need)\W+(\w+\W+){0,3}$",
    re.IGNORECASE,
)

# (pattern, short description of the rule it protects)
_RULES = [
    (r"\btrespass", "trespassing"),
    (r"\bprivate (property|land|garden|yard|grounds)", "private property"),
    (r"\b(climb|scale|clamber)\b", "climbing"),
    (r"\b(jump|leap|dive)(ing)?\b", "jumping or diving"),
    (r"\b(swim|wade|paddle (in|into|across))\b", "water activities"),
    (r"\b(run|sprint|dash|race)\b[^.!?]{0,30}\b(traffic|road|street|cars?|vehicles?)\b", "running near traffic"),
    (r"\b(ignore|disregard|bypass|duck under|step over|go past|walk past)\b[^.!?]{0,30}\b(signs?|warnings?|barriers?|fences?|ropes?|tape|gates?|closures?)\b", "ignoring signs or barriers"),
    (r"\b(talk|speak|chat) to (a |some |any )?(stranger|strangers|random|someone you don't know|people you don't know)", "approaching strangers"),
    (r"\bapproach\b[^.!?]{0,25}\b(strangers?|someone you don't know|people you don't know)", "approaching strangers"),
    (r"\bask (a |some |any )?(stranger|strangers|passer-?by)", "approaching strangers"),
    (r"\b(get|become|be|getting|becoming) (genuinely |truly |completely |totally |properly |really )?lost\b", "being lost"),
    (r"\blose (your|the) (way|bearings)\b", "being lost"),
    (r"\b(after dark|at night|in the dark|midnight|nightfall)\b", "darkness"),
    (r"\b(alone|by yourself)\b[^.!?]{0,30}\b(woods|forest|isolated|remote|deserted|secluded|dark)\b", "isolation"),
    (r"\b(enter|go into|sneak into|break into|slip into|explore inside)\b[^.!?]{0,25}\b(buildings?|houses?|propert(y|ies)|construction|sites?|warehouses?|tunnels?|caves?|abandoned|ruins?)\b", "entering restricted places"),
    (r"\b(buy|purchase|shop for|spend money)\b", "purchases"),
    (r"\b(binoculars|flashlight|torch|headlamp|hiking boots|tent|compass|rope|backpack)\b", "special equipment"),
    (r"\b(eat|taste|drink|swallow|pick and eat)\b[^.!?]{0,25}\b(wild|berries|mushrooms?|plants?|leaves|water from)\b", "eating or drinking wild things"),
    (r"\b(approach|touch|feed|chase|corner|pet)\b[^.!?]{0,20}\b(wildlife|wild animals?|animals?|snakes?|birds? nests?|stray)\b", "approaching animals"),
    # Phone-heavy instructions go against the whole point of the app.
    (r"\b(google|search (online|the web|the internet|your phone)|look (it|this|that|them) up|open (your )?(maps?|google maps|a map|an app|the app)|use (your )?(gps|maps?|phone|app)|keep (your )?(phone|screen) (out|on|open|in (your )?hand|handy|up)|check (your )?(phone|screen)|scroll|stay on (your )?phone|film|livestream|record (a )?(video|audio))\b", "requires phone use"),
    (r"\b(emergency|evacuation|storm|flood|heat) (warning|alert)\b[^.!?]{0,30}\b(ignore|anyway|regardless)\b", "ignoring warnings"),
]
_COMPILED = [(re.compile(p, re.IGNORECASE), why) for p, why in _RULES]

# Crossing a road is only acceptable if the same sentence mentions a safe way.
_CROSS = re.compile(
    r"\bcross\b[^.!?]{0,20}\b(road|roads|street|highway|motorway|freeway|railway|tracks?|junction|intersection)\b",
    re.IGNORECASE,
)
_SAFE_CROSSING = re.compile(
    r"(crosswalk|crossing|pedestrian|signal|safely|traffic light|zebra|bridge|underpass)", re.IGNORECASE
)


def _sentence_around(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("!", 0, start), text.rfind("?", 0, start))
    candidates = [i for i in (text.find(".", end), text.find("!", end), text.find("?", end)) if i != -1]
    right = min(candidates) if candidates else len(text)
    return text[left + 1 : right]


def find_safety_violations(text: str) -> List[str]:
    """Return a list of short reasons this text is unsafe (empty list = OK)."""
    problems: List[str] = []

    for pattern, why in _COMPILED:
        for match in pattern.finditer(text):
            before = text[max(0, match.start() - 40) : match.start()]
            if _NEGATION.search(before):
                continue  # "Do not search your phone" is allowed
            problems.append(why)
            break

    for match in _CROSS.finditer(text):
        before = text[max(0, match.start() - 40) : match.start()]
        sentence = _sentence_around(text, match.start(), match.end())
        if not _SAFE_CROSSING.search(sentence) and not _NEGATION.search(before):
            problems.append("crossing roads or tracks without a safe crossing")
            break

    return sorted(set(problems))
