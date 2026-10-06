import os
import re
import unittest
from pathlib import Path

from app import config
from app.models.mission import ENVIRONMENT_OPTIONS, NEED_OPTIONS, TIME_OPTIONS
from app.services import ollama_client
from app.services.mission_generator import generate_mission
from tests.fake_ollama import FakeOllama


class GeneratorTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._saved = (config.OLLAMA_HOST, config.OFFLINE_MODEL, config.OLLAMA_TIMEOUT_SECONDS)
        config.OFFLINE_MODEL = "gemma3:4b"
        config.OLLAMA_TIMEOUT_SECONDS = 5

    def tearDown(self):
        config.OLLAMA_HOST, config.OFFLINE_MODEL, config.OLLAMA_TIMEOUT_SECONDS = self._saved

    async def test_every_time_and_every_need_generates_a_mission(self):
        with FakeOllama("good") as fake:
            config.OLLAMA_HOST = fake.url
            for t in TIME_OPTIONS:
                for need in NEED_OPTIONS:
                    result = await generate_mission(t, need)
                    self.assertEqual(result.source, "gemma", msg=f"{t} {need}")
                    self.assertFalse(result.retried)
                    self.assertGreaterEqual(len(result.mission.steps), 4)
            self.assertEqual(len(fake.requests), len(TIME_OPTIONS) * len(NEED_OPTIONS))

    async def test_prompt_contains_the_check_in_choices_and_a_schema(self):
        with FakeOllama("good") as fake:
            config.OLLAMA_HOST = fake.url
            await generate_mission(60, "move", "park")
            body = fake.requests[0]
            self.assertEqual(body["model"], "gemma3:4b")
            self.assertFalse(body["stream"])
            self.assertIn("properties", body["format"])  # structured output requested
            user = body["messages"][1]["content"]
            self.assertIn("60 minutes", user)
            self.assertIn("Move", user)
            self.assertIn("park", user)

    async def test_each_mission_gets_a_creative_lens_and_the_voice_rules(self):
        with FakeOllama("good") as fake:
            config.OLLAMA_HOST = fake.url
            await generate_mission(30, "explore", "city", lens="sound: test lens")
            await generate_mission(30, "explore", "city")
            first = fake.requests[0]["messages"]
            self.assertIn("Lens: sound: test lens", first[1]["content"])
            self.assertIn("game master", first[0]["content"])
            self.assertEqual(fake.requests[0]["options"]["temperature"], 1.0)
            self.assertIn("Lens: ", fake.requests[1]["messages"][1]["content"])  # random one was chosen

    async def test_invalid_output_retries_once_with_correction(self):
        with FakeOllama("invalid_then_good") as fake:
            config.OLLAMA_HOST = fake.url
            result = await generate_mission(30, "surprise")
            self.assertEqual(result.source, "gemma")
            self.assertTrue(result.retried)
            self.assertEqual(len(fake.requests), 2)
            last = fake.requests[1]["messages"][-1]
            self.assertEqual(last["role"], "user")
            self.assertIn("could not be used", last["content"])

    async def test_unsafe_output_is_rejected_then_corrected(self):
        with FakeOllama("unsafe_then_good") as fake:
            config.OLLAMA_HOST = fake.url
            result = await generate_mission(30, "explore")
            self.assertEqual(result.source, "gemma")
            self.assertTrue(result.retried)
            self.assertNotIn("fence", " ".join(s.instruction for s in result.mission.steps).lower())

    async def test_still_invalid_after_retry_uses_fallback_not_a_crash(self):
        for behaviour in ("always_invalid", "always_unsafe"):
            with FakeOllama(behaviour) as fake:
                config.OLLAMA_HOST = fake.url
                result = await generate_mission(30, "clear_head")
                self.assertEqual(result.source, "fallback")
                self.assertEqual(result.fallback_reason, "invalid_output")
                self.assertEqual(len(fake.requests), 2)  # exactly one retry, never more
                self.assertGreaterEqual(len(result.mission.steps), 4)

    async def test_markdown_fenced_json_still_works(self):
        with FakeOllama("garbage_fenced") as fake:
            config.OLLAMA_HOST = fake.url
            result = await generate_mission(30, "surprise")
            self.assertEqual(result.source, "gemma")

    async def test_ollama_not_running_falls_back(self):
        config.OLLAMA_HOST = "http://127.0.0.1:9"  # nothing listens here
        result = await generate_mission(30, "surprise")
        self.assertEqual(result.source, "fallback")
        self.assertEqual(result.fallback_reason, "ollama_unavailable")

    async def test_model_missing_falls_back(self):
        with FakeOllama("model_missing") as fake:
            config.OLLAMA_HOST = fake.url
            result = await generate_mission(30, "surprise")
            self.assertEqual(result.source, "fallback")
            self.assertEqual(result.fallback_reason, "model_missing")
            self.assertEqual(len(fake.requests), 1)  # no pointless retry

    async def test_slow_model_times_out_and_falls_back(self):
        config.OLLAMA_TIMEOUT_SECONDS = 1
        with FakeOllama("slow") as fake:
            config.OLLAMA_HOST = fake.url
            result = await generate_mission(30, "surprise")
            self.assertEqual(result.source, "fallback")
            self.assertEqual(result.fallback_reason, "timeout")


class HealthTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._saved = (config.OLLAMA_HOST, config.OFFLINE_MODEL)

    def tearDown(self):
        config.OLLAMA_HOST, config.OFFLINE_MODEL = self._saved

    async def test_reports_model_available(self):
        with FakeOllama(models=["gemma3:4b"]) as fake:
            config.OLLAMA_HOST, config.OFFLINE_MODEL = fake.url, "gemma3:4b"
            status = await ollama_client.check_status()
            self.assertTrue(status["ollama_reachable"])
            self.assertTrue(status["model_available"])

    async def test_latest_tag_counts_as_installed(self):
        with FakeOllama(models=["gemma3:latest"]) as fake:
            config.OLLAMA_HOST, config.OFFLINE_MODEL = fake.url, "gemma3"
            self.assertTrue((await ollama_client.check_status())["model_available"])

    async def test_reports_model_missing(self):
        with FakeOllama(models=["llama3:8b"]) as fake:
            config.OLLAMA_HOST, config.OFFLINE_MODEL = fake.url, "gemma3:4b"
            status = await ollama_client.check_status()
            self.assertTrue(status["ollama_reachable"])
            self.assertFalse(status["model_available"])

    async def test_reports_ollama_down(self):
        config.OLLAMA_HOST = "http://127.0.0.1:9"
        status = await ollama_client.check_status()
        self.assertFalse(status["ollama_reachable"])
        self.assertFalse(status["model_available"])


class PrivacyTests(unittest.IsolatedAsyncioTestCase):
    async def test_only_coarse_choices_are_sent_to_the_model(self):
        saved = config.OLLAMA_HOST
        try:
            with FakeOllama("good") as fake:
                config.OLLAMA_HOST = fake.url
                await generate_mission(30, "surprise", "city")
                sent = repr(fake.requests[0]).lower()
                for word in ("latitude", "longitude", "lat:", "lon:", "gps", "coordinates", "ip address"):
                    self.assertNotIn(word, sent)
        finally:
            config.OLLAMA_HOST = saved

    def test_backend_source_never_writes_or_stores_user_data(self):
        """A blunt static check: no files opened for writing, no databases, no cookies/sessions."""
        app_dir = Path(__file__).resolve().parent.parent / "app"
        banned = [r"open\([^)]*['\"][wa]b?\+?['\"]", r"sqlite3", r"\.write_text\(", r"\.write_bytes\(", r"shelve", r"pickle", r"set_cookie", r"SessionMiddleware"]
        for path in app_dir.rglob("*.py"):
            text = path.read_text()
            for pattern in banned:
                self.assertIsNone(re.search(pattern, text), msg=f"{path.name} matches {pattern}")


if __name__ == "__main__":
    unittest.main()
