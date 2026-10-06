"""A pretend Ollama server for tests. It speaks just enough of Ollama's HTTP API.

`behaviour` decides how it answers /api/chat. Every request body is recorded in
`requests` so tests can check what the app actually sent.
"""
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GOOD_MISSION = {
    "title": "The Quiet Corner",
    "intro": "A short wander to find one small place you usually walk past.",
    "estimated_minutes": 25,
    "steps": [
        {"number": 1, "instruction": "Step outside and walk toward the nearest tree you can see.", "phone_down": True, "duration_minutes": 5},
        {"number": 2, "instruction": "Look for something blue. Do not search your phone for it. Just notice.", "phone_down": True, "duration_minutes": 5},
        {"number": 3, "instruction": "Turn toward the most interesting sound you can hear.", "phone_down": True, "duration_minutes": 5},
        {"number": 4, "instruction": "Find something that looks older than you and look at it for a minute.", "phone_down": False, "duration_minutes": 5},
        {"number": 5, "instruction": "Pause somewhere comfortable and notice three things you would normally walk past.", "phone_down": False, "duration_minutes": 5},
    ],
    "reflection_prompt": "What did you notice that you normally miss?",
    "closing_message": "You're done. Close OFFLINE.",
}

def good_for(minutes):
    """The good mission, with durations scaled to fit the time the app asked for."""
    mission = json.loads(json.dumps(GOOD_MISSION))
    each = max(1, minutes // 6)
    for step in mission["steps"]:
        step["duration_minutes"] = each
    mission["estimated_minutes"] = each * len(mission["steps"])
    return mission


UNSAFE_MISSION = json.loads(json.dumps(GOOD_MISSION))
UNSAFE_MISSION["steps"][0]["instruction"] = "Climb over the fence into the private property next door."


class FakeOllama:
    def __init__(self, behaviour="good", models=None):
        self.behaviour = behaviour  # good | invalid_then_good | always_invalid | unsafe_then_good | slow | model_missing | garbage_fenced
        self.models = models if models is not None else ["gemma3:4b"]
        self.requests = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # keep test output quiet
                pass

            def _send(self, code, body):
                data = json.dumps(body).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                if self.path == "/api/tags":
                    self._send(200, {"models": [{"name": m} for m in owner.models]})
                else:
                    self._send(404, {"error": "not found"})

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                owner.requests.append(body)
                n = len(owner.requests)
                b = owner.behaviour
                asked = re.search(r"Time available: (\d+)", json.dumps(body))
                good = json.dumps(good_for(int(asked.group(1)) if asked else 30))
                if b == "model_missing":
                    return self._send(404, {"error": f"model '{body.get('model')}' not found, try pulling it first"})
                if b == "slow":
                    time.sleep(3)
                    return self._send(200, {"message": {"content": good}})
                if b == "invalid_then_good":
                    text = "Sure! Here is a fun idea: go outside." if n == 1 else good
                elif b == "always_invalid":
                    text = json.dumps({"title": "Oops", "steps": []})
                elif b == "unsafe_then_good":
                    text = json.dumps(UNSAFE_MISSION) if n == 1 else good
                elif b == "always_unsafe":
                    text = json.dumps(UNSAFE_MISSION)
                elif b == "garbage_fenced":
                    text = "```json\n" + good + "\n```"
                else:
                    text = good
                self._send(200, {"message": {"role": "assistant", "content": text}})

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.02), daemon=True)

    @property
    def url(self):
        return f"http://127.0.0.1:{self.server.server_address[1]}"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
