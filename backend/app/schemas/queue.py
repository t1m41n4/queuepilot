from pydantic import Field

from app.schemas.common import EmptyRequest


class QueueJoinRequest(EmptyRequest):
    branch_id: int = Field(ge=1, examples=[1])
    customer_name: str = Field(examples=["John Kamau"])


class QueueJoinResponse(EmptyRequest):
    queue_entry_id: int = Field(examples=[15])
    queue_number: str = Field(examples=["A014"])
    status: str = Field(examples=["WAITING"])
    estimated_wait: int = Field(examples=[20])


class QueueEntryResponse(EmptyRequest):
    queue_number: str = Field(examples=["A014"])
    branch_name: str = Field(examples=["Equity Bank - CBD"])
    status: str = Field(examples=["READY"])
    position: int = Field(examples=[2])
    estimated_wait: int = Field(examples=[8])


class QueueCancellationRequest(EmptyRequest):
    pass


class QueueCancellationResponse(EmptyRequest):
    message: str = Field(examples=["Queue cancelled successfully."])
