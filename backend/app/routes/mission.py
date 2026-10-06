from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from ..services.mission_generator import generate_mission

router = APIRouter()


class MissionRequest(BaseModel):
    """Only coarse choices from the check-in screen. No location, no identity."""

    time_minutes: Literal[15, 30, 60, 90]
    need: Literal["clear_head", "explore", "move", "be_alone", "surprise"]
    environment: Literal["unsure", "city", "park", "suburb", "countryside"] = "unsure"


@router.post("/api/mission")
async def create_mission(request: MissionRequest) -> dict:
    """Generate a mission. Always returns a usable mission (Gemma's, or a safe fallback)."""
    result = await generate_mission(request.time_minutes, request.need, request.environment)
    return result.to_dict()
