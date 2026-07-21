from fastapi import APIRouter, status

from app.api.errors import not_implemented
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.schemas.common import NOT_IMPLEMENTED_RESPONSES


router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post(
    "/chat",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    responses={200: {"model": AssistantChatResponse}, **NOT_IMPLEMENTED_RESPONSES},
)
async def chat(request: AssistantChatRequest) -> None:
    not_implemented()
