import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class PortfolioCreate(BaseModel):
    name: str
    description: str | None = None
    currency: str = "EUR"


class PortfolioUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    currency: str | None = None


class PortfolioResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HoldingResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    stock_id: uuid.UUID
    stock_ticker: str | None = None
    stock_name: str | None = None
    shares: Decimal
    avg_cost_basis: Decimal
    first_purchased: date | None
    notes: str | None
    current_price: Decimal | None = None
    current_value: Decimal | None = None
    gain_loss: Decimal | None = None
    gain_loss_pct: Decimal | None = None

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    stock_id: uuid.UUID
    type: str  # buy, sell, dividend
    shares: Decimal
    price_per_share: Decimal
    fees: Decimal = Decimal("0")
    executed_at: datetime
    notes: str | None = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    stock_id: uuid.UUID
    stock_ticker: str | None = None
    type: str
    shares: Decimal
    price_per_share: Decimal
    fees: Decimal
    executed_at: datetime
    notes: str | None

    model_config = {"from_attributes": True}
