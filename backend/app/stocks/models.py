import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    exchange: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    sector: Mapped[str | None] = mapped_column(String(100), index=True)
    industry: Mapped[str | None] = mapped_column(String(100))
    currency: Mapped[str] = mapped_column(String(10), default="EUR")
    country: Mapped[str | None] = mapped_column(String(50), index=True)
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_data_refresh: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    financial_statements: Mapped[list["FinancialStatement"]] = relationship(
        back_populates="stock", cascade="all, delete-orphan"
    )
    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="stock", cascade="all, delete-orphan"
    )
    valuation_snapshots: Mapped[list["ValuationSnapshot"]] = relationship(
        back_populates="stock", cascade="all, delete-orphan"
    )


class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    __table_args__ = (
        Index("ix_financial_statements_stock_period", "stock_id", "period_type", "period_end"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)  # annual, quarterly
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    revenue: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    net_income: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    eps: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    book_value_per_share: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    total_assets: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    total_liabilities: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    current_assets: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    current_liabilities: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    total_debt: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    total_equity: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    dividends_per_share: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    free_cash_flow: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    operating_cash_flow: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    shares_outstanding: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    raw_data: Mapped[dict | None] = mapped_column(JSONB)

    stock: Mapped["Stock"] = relationship(back_populates="financial_statements")


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (
        Index("ix_price_history_stock_date", "stock_id", "date", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    high: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    low: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    close: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    adj_close: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    volume: Mapped[int | None] = mapped_column(BigInteger)

    stock: Mapped["Stock"] = relationship(back_populates="price_history")


class ValuationSnapshot(Base):
    __tablename__ = "valuation_snapshots"
    __table_args__ = (
        Index("ix_valuation_snapshots_stock_date", "stock_id", "calculated_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    market_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    graham_number: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    graham_formula_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    ncav_per_share: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    dcf_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    pe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    pb_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    current_ratio: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    debt_to_equity: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    dividend_yield: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    margin_of_safety_pct: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    earnings_stability: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    composite_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    stock: Mapped["Stock"] = relationship(back_populates="valuation_snapshots")
