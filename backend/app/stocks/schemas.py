import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class StockResponse(BaseModel):
    id: uuid.UUID
    ticker: str
    name: str
    exchange: str
    sector: str | None
    industry: str | None
    currency: str
    country: str | None
    market_cap: Decimal | None
    is_active: bool
    last_data_refresh: datetime | None

    model_config = {"from_attributes": True}


class StockSearchResult(BaseModel):
    ticker: str
    name: str
    exchange: str


class StockListParams(BaseModel):
    exchange: str | None = None
    sector: str | None = None
    country: str | None = None
    is_active: bool = True
    page: int = 1
    per_page: int = 50


class PriceHistoryResponse(BaseModel):
    date: date
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    adj_close: Decimal | None
    volume: int | None

    model_config = {"from_attributes": True}


class FinancialStatementResponse(BaseModel):
    period_type: str
    period_end: date
    revenue: Decimal | None
    net_income: Decimal | None
    eps: Decimal | None
    book_value_per_share: Decimal | None
    total_assets: Decimal | None
    total_liabilities: Decimal | None
    current_assets: Decimal | None
    current_liabilities: Decimal | None
    total_debt: Decimal | None
    total_equity: Decimal | None
    dividends_per_share: Decimal | None
    free_cash_flow: Decimal | None
    operating_cash_flow: Decimal | None

    model_config = {"from_attributes": True}


class ValuationSnapshotResponse(BaseModel):
    calculated_at: datetime
    market_price: Decimal | None
    graham_number: Decimal | None
    graham_formula_value: Decimal | None
    ncav_per_share: Decimal | None
    dcf_value: Decimal | None
    pe_ratio: Decimal | None
    pb_ratio: Decimal | None
    current_ratio: Decimal | None
    debt_to_equity: Decimal | None
    dividend_yield: Decimal | None
    margin_of_safety_pct: Decimal | None
    earnings_stability: Decimal | None
    composite_score: Decimal | None

    model_config = {"from_attributes": True}


class StockDetailResponse(StockResponse):
    latest_valuation: ValuationSnapshotResponse | None = None
