"""A tiny client for the local Ollama server. Standard library only (no extra installs).

Ollama runs on your own machine, so no mission data leaves your computer.
"""
import asyncio
import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from .. import config


class OllamaError(Exception):
    """Base class. `code` is a short machine-readable reason shown to the frontend."""

    code = "ollama_error"


class OllamaUnavailable(OllamaError):
    code = "ollama_unavailable"


class OllamaModelMissing(OllamaError):
    code = "model_missing"


class OllamaTimeout(OllamaError):
    code = "timeout"


def _post_json(url: str, payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        if err.code == 404 or "not found" in body.lower():
            raise OllamaModelMissing(f"Model '{payload.get('model')}' is not installed.") from err
        raise OllamaError(f"Ollama returned HTTP {err.code}.") from err
    except TimeoutError as err:
        raise OllamaTimeout("The local model took too long to answer.") from err
    except urllib.error.URLError as err:
        if isinstance(err.reason, TimeoutError):
            raise OllamaTimeout("The local model took too long to answer.") from err
        raise OllamaUnavailable("Could not reach Ollama. Is it running?") from err
    except (ConnectionError, OSError) as err:
        raise OllamaUnavailable("Could not reach Ollama. Is it running?") from err
    except json.JSONDecodeError as err:
        raise OllamaError("Ollama sent an unreadable reply.") from err


def _get_json(url: str, timeout: float) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as err:
        raise OllamaUnavailable("Could not reach Ollama. Is it running?") from err


async def chat(
    messages: List[Dict[str, str]],
    schema: Optional[dict] = None,
    model: Optional[str] = None,
) -> str:
    """Send a chat to Ollama and return the model's text reply."""
    payload: Dict[str, Any] = {
        "model": model or config.OFFLINE_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 1.0},
    }
    if schema is not None:
        payload["format"] = schema  # structured output: Ollama constrains the JSON shape
    # Run the blocking call in a worker thread so the web server stays responsive.
    data = await asyncio.to_thread(
        _post_json, f"{config.OLLAMA_HOST}/api/chat", payload, config.OLLAMA_TIMEOUT_SECONDS
    )
    try:
        return data["message"]["content"]
    except (KeyError, TypeError) as err:
        raise OllamaError("Ollama's reply had no message.") from err


async def check_status() -> Dict[str, Any]:
    """Used by GET /api/health: is Ollama reachable, and is our model installed?"""
    status: Dict[str, Any] = {
        "ollama_reachable": False,
        "model": config.OFFLINE_MODEL,
        "model_available": False,
    }
    try:
        data = await asyncio.to_thread(_get_json, f"{config.OLLAMA_HOST}/api/tags", 3.0)
    except OllamaUnavailable:
        return status
    status["ollama_reachable"] = True
    installed = {m.get("name", "") for m in data.get("models", []) if isinstance(m, dict)}
    wanted = config.OFFLINE_MODEL
    # "gemma3" and "gemma3:latest" mean the same thing to Ollama.
    candidates = {wanted, f"{wanted}:latest"} if ":" not in wanted else {wanted}
    status["model_available"] = bool(candidates & installed)
    return status
