"""Settings, read from environment variables so nothing is hard-coded.

Nothing here is secret. There are no API keys in OFFLINE: the AI runs locally.
"""
import os

# Where Ollama is listening. This is its default address.
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

# Which Gemma model to ask Ollama for. Swap it by changing this variable.
# Run `ollama list` to see what you have installed.
OFFLINE_MODEL = os.getenv("OFFLINE_MODEL", "gemma3:4b")

# Small local models can be slow on laptops, so we wait a while before giving up.
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

# Which browser origins may call the API (the Vite dev server by default).
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "OFFLINE_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]
