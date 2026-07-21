from pydantic import BaseModel, ConfigDict


class EmptyRequest(BaseModel):
    """Strict placeholder for an endpoint whose request contract is not specified."""

    model_config = ConfigDict(extra="forbid")


class NotImplementedResponse(BaseModel):
    detail: str = "Not implemented"


NOT_IMPLEMENTED_RESPONSES = {
    501: {
        "description": "This endpoint is reserved for a future milestone.",
        "model": NotImplementedResponse,
    }
}
