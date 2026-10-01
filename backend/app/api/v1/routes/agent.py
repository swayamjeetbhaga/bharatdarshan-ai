import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import chat as chat_service
from app.agent._completion import QuotaExhaustedError
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.agent import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    history = [{"role": m.role, "content": m.content} for m in data.history]
    try:
        return await chat_service.ask(
            data.message,
            history,
            place_name=data.place_name,
            district=data.district,
            attraction_id=data.attraction_id,
            db=db,
        )
    except QuotaExhaustedError as exc:
        logger.error("agent chat: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception:
        logger.exception("agent chat failed")
        raise HTTPException(status_code=502, detail="AI helper is temporarily unavailable.")
