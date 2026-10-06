import copy
import json
import unittest

from app.services.fallback import build_fallback_mission
from app.services.safety import find_safety_violations
from app.services.validation import MissionValidationError, extract_json, validate_mission
from app.models.mission import NEED_OPTIONS, TIME_OPTIONS
from tests.fake_ollama import GOOD_MISSION


def mission_with(**changes):
    data = copy.deepcopy(GOOD_MISSION)
    data.update(changes)
    return data


class ValidationTests(unittest.TestCase):
    def test_good_mission_passes_and_is_renumbered(self):
        data = mission_with()
        data["steps"][2]["number"] = 99  # a miscounting model should not matter
        mission = validate_mission(data, 30)
        self.assertEqual([s.number for s in mission.steps], [1, 2, 3, 4, 5])
        self.assertLessEqual(mission.estimated_minutes, 30)

    def test_fenced_json_is_accepted(self):
        text = "Here you go:\n```json\n" + json.dumps(GOOD_MISSION) + "\n```"
        self.assertEqual(extract_json(text)["title"], "The Quiet Corner")

    def test_non_json_is_rejected(self):
        for bad in ["", "   ", "go outside!", None, "{not json}"]:
            with self.assertRaises(MissionValidationError):
                extract_json(bad)

    def test_wrong_step_counts_rejected(self):
        for count in (0, 3, 8):
            data = mission_with(steps=[GOOD_MISSION["steps"][0]] * count)
            with self.assertRaises(MissionValidationError):
                validate_mission(data, 30)

    def test_missing_fields_rejected(self):
        for key in ("title", "intro", "reflection_prompt", "closing_message", "steps"):
            data = mission_with()
            del data[key]
            with self.assertRaises(MissionValidationError, msg=key):
                validate_mission(data, 30)

    def test_closing_must_tell_user_to_close_app(self):
        with self.assertRaises(MissionValidationError):
            validate_mission(mission_with(closing_message="Great job, enjoy your day!"), 30)

    def test_needs_at_least_two_phone_down_steps(self):
        data = mission_with()
        for step in data["steps"]:
            step["phone_down"] = False
        with self.assertRaises(MissionValidationError):
            validate_mission(data, 30)

    def test_durations_cannot_exceed_time_available(self):
        data = mission_with()
        for step in data["steps"]:
            step["duration_minutes"] = 15
        with self.assertRaises(MissionValidationError):
            validate_mission(data, 30)

    def test_bad_types_rejected(self):
        data = mission_with()
        data["steps"][0]["phone_down"] = "yes"
        data["steps"][1]["duration_minutes"] = "five"
        with self.assertRaises(MissionValidationError):
            validate_mission(data, 30)
        with self.assertRaises(MissionValidationError):
            validate_mission(["not", "an", "object"], 30)

    def test_overlong_instruction_rejected(self):
        data = mission_with()
        data["steps"][0]["instruction"] = "Walk. " * 100
        with self.assertRaises(MissionValidationError):
            validate_mission(data, 30)

    def test_unsafe_step_rejected(self):
        data = mission_with()
        data["steps"][0]["instruction"] = "Climb the wall and enter the abandoned warehouse."
        with self.assertRaises(MissionValidationError) as ctx:
            validate_mission(data, 30)
        self.assertTrue(any("unsafe" in p for p in ctx.exception.problems))


class SafetyAdversarialTests(unittest.TestCase):
    UNSAFE = [
        "Hop the fence and trespass through the yard.",
        "Walk onto private property and look around.",
        "Climb the tallest tree you can find.",
        "Run across the road without stopping.",
        "Ignore the warning signs and keep walking.",
        "Talk to a stranger and ask them for directions.",
        "Get completely lost on purpose.",
        "Go out after dark and wander the woods.",
        "Buy a coffee from the first shop you see.",
        "Open Google Maps to find the nearest park.",
        "Keep your phone out and scroll while you walk.",
        "Keep your screen on and follow the map.",
        "Go into the abandoned building at the end of the street.",
        "Swim across the pond.",
        "Cross the highway wherever you like.",
        "Eat the wild berries you find.",
        "Chase the nearest animal.",
        "Ignore any storm warning and carry on.",
    ]
    SAFE = [
        "Walk toward a street, path, or outdoor area you have never explored.",
        "Look for something blue. Do not search your phone for it. Just notice.",
        "Use the pedestrian crossing to get to the other side, then look up.",
        "The goal is not to get lost. The goal is to notice.",
        "Sit on a bench and listen to the furthest sound you can hear.",
        "Start walking at a comfortable pace and keep your phone in your pocket.",
    ]

    def test_unsafe_text_is_flagged(self):
        for text in self.UNSAFE:
            self.assertTrue(find_safety_violations(text), msg=f"should be flagged: {text}")

    def test_safe_text_passes(self):
        for text in self.SAFE:
            self.assertEqual(find_safety_violations(text), [], msg=f"should pass: {text}")


class FallbackTests(unittest.TestCase):
    def test_every_fallback_passes_the_same_validator(self):
        for time_minutes in TIME_OPTIONS:
            for need in NEED_OPTIONS:
                mission = build_fallback_mission(time_minutes, need)
                validated = validate_mission(mission.to_dict(), time_minutes)
                self.assertLessEqual(sum(s.duration_minutes for s in validated.steps), time_minutes)
                self.assertIn("close", validated.closing_message.lower())


if __name__ == "__main__":
    unittest.main()
