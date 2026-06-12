from decimal import Decimal
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ResellerBase(BaseModel):
    admin_id: uuid.UUID
    credits: Decimal = Decimal("0.00")
    balance: Decimal = Decimal("0.00")
    max_users: int = 100
    status: str = "ACTIVE"


class ResellerCreate(ResellerBase):
    pass


class ResellerUpdate(BaseModel):
    credits: Decimal | None = None
    balance: Decimal | None = None
    max_users: int | None = None
    status: str | None = None


class ResellerResponse(ResellerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TransactionBase(BaseModel):
    reseller_id: uuid.UUID
    type: str  # CREDIT, DEBIT, REFUND
    amount: Decimal
    description: str | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    admin_id: uuid.UUID | None = None
    created_at: datetime
