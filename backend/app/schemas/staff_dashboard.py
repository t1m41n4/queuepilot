from pydantic import Field

from app.schemas.common import EmptyRequest


class StaffDashboardResponse(EmptyRequest):
    branch_id: int = Field(examples=[1])
    queue_status: str = Field(examples=["OPEN"])
    waiting: int = Field(ge=0, examples=[3])
    ready: int = Field(ge=0, examples=[1])
    checked_in: int = Field(ge=0, examples=[1])
    current_customer: str | None = Field(default=None, examples=["John Kamau"])


class StaffQueueItemResponse(EmptyRequest):
    queue_entry_id: int = Field(examples=[15])
    queue_number: str = Field(examples=["A014"])
    customer_name: str = Field(examples=["John Kamau"])
    status: str = Field(examples=["READY"])
    estimated_wait: int | None = Field(default=None, ge=0, examples=[8])
    action: str | None = Field(default=None, examples=["Check In"])
