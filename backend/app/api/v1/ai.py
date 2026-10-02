"""VisionTrack ANPR — AI Assistant API."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models import User
from app.schemas import AIQueryRequest, AIQueryResponse, APIResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/query", response_model=APIResponse[AIQueryResponse],
             summary="Ask the AI assistant")
async def ai_query(
    data: AIQueryRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send a natural language query to the Vision Assistant.
    The AI will convert your question into structured queries against the ANPR database.
    """
    service = AIService(db)
    response = await service.query(data.message, user_id=user.id)
    return APIResponse(data=response)
