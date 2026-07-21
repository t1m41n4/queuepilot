from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.assistant import QueueOperationsAssistant


router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post(
    "/chat",
    response_model=AssistantChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        502: {"description": "Assistant provider unavailable"},
        503: {"description": "Assistant is not configured"},
    },
)
async def chat(
    request: AssistantChatRequest,
    db: Session = Depends(get_db),
) -> AssistantChatResponse:
    answer = await QueueOperationsAssistant(db).answer(request.queue_entry_id, request.question)
    return AssistantChatResponse(answer=answer)
