from typing import Annotated

from fastapi import APIRouter, Path

from app.api.errors import not_implemented
from app.schemas.common import NOT_IMPLEMENTED_RESPONSES


router = APIRouter(prefix="/banks", tags=["banks"])


@router.get("", responses=NOT_IMPLEMENTED_RESPONSES)
async def list_banks() -> None:
    not_implemented()


@router.get("/{bank_id}/branches", responses=NOT_IMPLEMENTED_RESPONSES)
async def list_bank_branches(
    bank_id: Annotated[int, Path(ge=1)],
) -> None:
    not_implemented()
