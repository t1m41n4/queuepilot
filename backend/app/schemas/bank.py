from pydantic import Field

from app.schemas.common import EmptyRequest


class BankResponse(EmptyRequest):
    id: int = Field(examples=[1])
    name: str = Field(examples=["QueuePilot Demo Bank"])


class BranchResponse(EmptyRequest):
    id: int = Field(examples=[1])
    name: str = Field(examples=["QueuePilot CBD"])
    queue_status: str = Field(examples=["OPEN"])
    estimated_wait: int = Field(ge=0, examples=[10])
    recommended: bool = Field(examples=[True])
