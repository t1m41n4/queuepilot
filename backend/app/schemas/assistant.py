from pydantic import Field

from app.schemas.common import EmptyRequest


class AssistantChatRequest(EmptyRequest):
    queue_entry_id: int = Field(ge=1, examples=[15])
    question: str = Field(examples=["Why did my ETA increase?"])


class AssistantChatResponse(EmptyRequest):
    answer: str = Field(
        examples=[
            "Your estimated waiting time increased because service is taking longer "
            "than the average at your selected branch."
        ]
    )
