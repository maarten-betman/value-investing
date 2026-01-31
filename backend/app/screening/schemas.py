import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel


class ScreeningProfileCreate(BaseModel):
    name: str
    description: str | None = None
    exchanges: list[str] = ["EURONEXT"]
    sectors: list[str] = []
    countries: list[str] = []
    included_tickers: list[str] = []
    excluded_tickers: list[str] = []
    criteria: dict[str, Any] = {}
    is_active: bool = True
    schedule: str | None = "0 19 * * 1-5"  # Weekdays at 19:00


class ScreeningProfileUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    exchanges: list[str] | None = None
    sectors: list[str] | None = None
    countries: list[str] | None = None
    included_tickers: list[str] | None = None
    excluded_tickers: list[str] | None = None
    criteria: dict[str, Any] | None = None
    is_active: bool | None = None
    schedule: str | None = None


class ScreeningProfileResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    exchanges: list[str] | None
    sectors: list[str] | None
    countries: list[str] | None
    included_tickers: list[str] | None
    excluded_tickers: list[str] | None
    criteria: dict[str, Any] | None
    is_active: bool
    schedule: str | None
    last_run_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScreeningResultResponse(BaseModel):
    id: uuid.UUID
    stock_id: uuid.UUID
    stock_ticker: str | None = None
    stock_name: str | None = None
    run_at: datetime
    passed_criteria: dict[str, Any] | None
    failed_criteria: dict[str, Any] | None
    composite_score: Decimal | None
    margin_of_safety_pct: Decimal | None
    recommendation: str | None

    model_config = {"from_attributes": True}
