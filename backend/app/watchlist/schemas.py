import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class WatchlistItemCreate(BaseModel):
    stock_id: uuid.UUID
    target_price: Decimal | None = None
    target_mos_pct: Decimal | None = None
    notes: str | None = None


class WatchlistItemUpdate(BaseModel):
    target_price: Decimal | None = None
    target_mos_pct: Decimal | None = None
    notes: str | None = None


class WatchlistItemResponse(BaseModel):
    id: uuid.UUID
    stock_id: uuid.UUID
    stock_ticker: str | None = None
    stock_name: str | None = None
    target_price: Decimal | None
    target_mos_pct: Decimal | None
    current_price: Decimal | None = None
    current_mos_pct: Decimal | None = None
    notes: str | None
    added_at: datetime

    model_config = {"from_attributes": True}
