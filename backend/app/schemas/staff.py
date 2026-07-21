from pydantic import Field

from app.schemas.common import EmptyRequest


class StaffLoginRequest(EmptyRequest):
    email: str = Field(examples=["staff@queuepilot.local"])
    password: str = Field(examples=["password123"])


class StaffLoginResponse(EmptyRequest):
    access_token: str = Field(examples=["..."])
    token_type: str = Field(examples=["bearer"])


class CheckInByQueueEntryRequest(EmptyRequest):
    queue_entry_id: int = Field(ge=1, examples=[15])


class CheckInByQrTokenRequest(EmptyRequest):
    qr_token: str = Field(examples=["abc123xyz"])


StaffCheckInRequest = CheckInByQueueEntryRequest | CheckInByQrTokenRequest


class QueueEntryActionRequest(EmptyRequest):
    queue_entry_id: int = Field(ge=1, examples=[15])


class StaffActionRequest(EmptyRequest):
    pass
