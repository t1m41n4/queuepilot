from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.bank import BankResponse, BranchResponse
from app.services.bank_directory import BankDirectory


router = APIRouter(prefix="/banks", tags=["banks"])


@router.get("", response_model=list[BankResponse])
async def list_banks(db: Session = Depends(get_db)) -> list[BankResponse]:
    return [BankResponse.model_validate(bank, from_attributes=True) for bank in BankDirectory(db).banks()]


@router.get("/{bank_id}/branches", response_model=list[BranchResponse])
async def list_bank_branches(
    bank_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
) -> list[BranchResponse]:
    return [BranchResponse(**branch) for branch in BankDirectory(db).branches(bank_id)]
