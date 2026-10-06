# OFFLINE

*An AI adventure guide designed to become unnecessary.*

Built for **Hacktoberfest 2026, Challenge 2: Open-Source AI ("Touch Grass")**.

## What OFFLINE is

You open the app, say how much time you have and what you need, and a **local Gemma model** writes you a short outdoor mission: a few sensory, non-optimized steps like *"turn toward the most interesting sound you can hear."* Then the app tells you to put your phone down. It reveals the next step only when you come back for it, and its last message is: **"You're done. Close OFFLINE."**

It is deliberately *not* a chatbot, a hiking planner, or a map app.

## Why it exists

Most AI products are built to keep you talking to them. OFFLINE's success condition is the opposite: **the best interaction with OFFLINE is closing OFFLINE.** No feeds, streaks, badges, or accounts. The screen should be the shortest part of the experience.

## How local Gemma works

1. The frontend sends only three coarse choices: time (15/30/60/90), a need, and an optional rough setting (city, park, ...).
2. The FastAPI backend builds a prompt (`backend/app/prompts/mission_prompt.py`) and sends it to **Ollama** running on your machine, asking for JSON that matches a schema.
3. **Gemma writes the entire mission**: title, premise, every step, the reflection question and the closing line.
4. The backend validates the answer (structure, 4-7 steps, at least two phone-down steps, durations that fit your time, a closing line that says to close the app) and runs a safety screen over every sentence.
5. If the answer is unusable, the backend **retries once**, telling Gemma exactly what was wrong. If that fails too, or Ollama is down, slow or missing the model, you get a safe hand-written mission, and the app **says so honestly** instead of pretending Gemma wrote it.

No paid AI API, no API keys, no cloud inference.

```
React + TypeScript + Vite   (frontend/)
        |
        | HTTP  (/api, proxied by Vite in development)
        v
FastAPI backend             (backend/)
        |
        | local HTTP call
        v
Ollama  ->  Gemma (open-weight model)
        |
        v
Structured mission JSON -> validated + safety-screened -> frontend
```

## Prerequisites

- **Python 3.10+** and **Node.js 20.19+ or 22.12+** (required by Vite 7)
- **Ollama** (below), and enough free RAM for the model (the default 4B model is a ~3.3 GB download; as a rough guide, 8 GB of RAM is comfortable)
- Internet is needed **once** to install dependencies and download the model. After that, everything runs on your machine.

## Ollama and model setup

1. Install Ollama from <https://ollama.com/download> and start it (the desktop app starts it for you; or run `ollama serve`).
2. Pull a Gemma model. The default is `gemma3:4b`:
   ```bash
   ollama pull gemma3:4b
   ```
3. Check that it's installed:
   ```bash
   ollama list
   ```
   You should see `gemma3:4b` in the list. Optionally try it: `ollama run gemma3:4b`.

Want a different size or a newer Gemma? Pull it, then set `OFFLINE_MODEL` (see below). For example `gemma3:1b` is smaller and faster; `gemma3:12b` writes better but needs more memory.

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```

The backend now runs at <http://127.0.0.1:8000>. Check it:

```bash
curl http://127.0.0.1:8000/api/health
# {"status":"ok","ollama_reachable":true,"model":"gemma3:4b","model_available":true}
```

**Test Gemma without the frontend** (a good first step):

```bash
python3 -m app.cli --time 30 --need surprise
```

The output includes `"source": "gemma"` when Gemma's mission passed all checks, or `"source": "fallback"` plus a `fallback_reason` when it didn't.

## Frontend setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The dev server forwards `/api` to the backend.

**On your phone:** the dev server is reachable on your local network (Vite prints a "Network" URL). Open it on a phone on the same Wi-Fi. Only the laptop needs Ollama; the phone just talks to the dev server.

To type-check and build for production: `npm run build`.

## Environment variables (all optional)

| Variable | Default | What it does |
| --- | --- | --- |
| `OFFLINE_MODEL` | `gemma3:4b` | Which Ollama model writes missions. Swap models without touching code. |
| `OLLAMA_HOST` | `http://localhost:11434` | Where Ollama is listening. |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | How long the backend waits for the model before using a fallback. |
| `OFFLINE_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Browser origins allowed to call the API directly. |
| `OFFLINE_BACKEND_URL` | `http://127.0.0.1:8000` | (Frontend dev server) where to forward `/api`. |
| `VITE_API_BASE` | *(empty)* | (Frontend) call a backend at a different address instead of using the proxy. |

Example: `OFFLINE_MODEL=gemma3:1b python3 -m uvicorn app.main:app --reload`

There are no secrets or API keys anywhere in this project.

## Running the tests

```bash
cd backend
python3 -m unittest discover -s tests -t . -v
```

These tests use a small pretend Ollama server, so you don't need Ollama running. They cover: every time option and every need, retry-then-fallback on invalid JSON, unsafe model output, Ollama not running, a missing model, a slow model, adversarial/odd mission text, and a check that the backend never writes user data anywhere.

## Troubleshooting

| Symptom | Likely cause and fix |
| --- | --- |
| Mission says "Gemma isn't running on this device" | Start Ollama (`ollama serve`, or open the app). Check `curl http://localhost:11434/api/tags`. |
| "The Gemma model isn't installed yet" | Run `ollama pull gemma3:4b`, or set `OFFLINE_MODEL` to a model shown by `ollama list`. |
| "Gemma took too long" | Smaller model (`gemma3:1b`), or raise `OLLAMA_TIMEOUT_SECONDS`. The first request after starting Ollama is slowest because the model is loading. |
| "Gemma's mission didn't pass the safety checks" | Normal now and then, especially with small models. The reason is logged by the backend (`Attempt 1 rejected: ...`). If it happens a lot, try a larger model. |
| Frontend says "Can't reach OFFLINE" | The backend isn't running. Start it (see Backend setup). |
| Phone can't open the Network URL | Same Wi-Fi? A firewall may block port 5173. |
| `address already in use` | Another program is using port 8000 or 5173. Stop it, or choose another port. |

## Privacy design

- **Local inference.** Mission text is generated by Gemma on your own machine via Ollama. Nothing is sent to a third-party AI provider.
- **No location.** OFFLINE never asks for GPS or browser location. The only context is what you tap: time, need, and an optional rough setting.
- **No accounts, no database, no analytics.** The backend writes no files and stores nothing (a test checks this). The browser stores nothing: no cookies, localStorage, sessionStorage or IndexedDB. Your reflection stays in memory until you close the tab.
- **No third-party requests.** No CDNs, web fonts, or trackers. The app talks only to your own backend.
- **Screen-time reminder is opt-in and local.** It is just a countdown inside the page that you start yourself. OFFLINE never watches your screen, history, keystrokes or other apps.

**Being precise about "offline":** the *running app* needs no internet, but installing it (`pip`, `npm`, `ollama pull`) does. Phone-down timers work by comparing against the clock, so they stay correct if your screen sleeps, but the page cannot buzz you while locked.

## Safety design

Safety is enforced in three layers, because a model alone should never be trusted:

1. **The prompt** tells Gemma the rules: ordinary public places only; no trespassing, climbing, unsafe road crossing, approaching strangers, ignoring signs or warnings, being genuinely lost, special equipment, purchases, or after-dark activity.
2. **A safety screen** (`backend/app/services/safety.py`) scans every sentence of the mission and rejects unsafe or phone-heavy instructions. It lets "Do not search your phone" through and blocks "Open Google Maps".
3. **A validator** (`backend/app/services/validation.py`) enforces the design rules: 4-7 steps, at least two phone-down steps, durations within your time, a final message that tells you to close the app.

Anything rejected is retried once, then replaced by a hand-written fallback mission that passes the same checks. The mission screen also reminds you to follow signs and traffic rules and use your own judgement. The screen is a blunt keyword filter, not a guarantee; it errs on the side of rejecting.

## Hacktoberfest challenge alignment

- **Open-source AI at the core:** Gemma, via Ollama, writes every mission.
- **Local inference, privacy, model swapping, low/no cost:** runs on your hardware, no keys, swap models with `OFFLINE_MODEL`.
- **Touch Grass:** the product's whole job is getting you off the screen: one instruction at a time, a bare phone-down mode, and an ending that says to close the app.

## Project layout

```
offline/
├── frontend/   React + TypeScript + Vite (screens in src/pages, shared bits in src/components)
├── backend/    FastAPI (app/routes) + the mission pipeline (app/services, app/prompts)
│   └── tests/  unit tests with a pretend Ollama server
├── README.md
└── LICENSE
```

## Future improvements

Only after the core experience is solid: optional browser location and weather/daylight context (kept ephemeral), a model selector in the UI, narration of the intro, Sentry tracing for model latency and errors, and deployment of the frontend and backend while keeping the local-AI story honest.
