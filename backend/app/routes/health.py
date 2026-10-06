from fastapi import APIRouter

from ..services import ollama_client

router = APIRouter()


@router.get("/api/health")
async def health() -> dict:
    """Confirms the backend is up and reports whether Ollama and the model are reachable."""
    return {"status": "ok", **(await ollama_client.check_status())}
