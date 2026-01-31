import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ScreeningProfile(Base):
    __tablename__ = "screening_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    exchanges: Mapped[list | None] = mapped_column(JSONB, default=list)
    sectors: Mapped[list | None] = mapped_column(JSONB, default=list)
    countries: Mapped[list | None] = mapped_column(JSONB, default=list)
    included_tickers: Mapped[list | None] = mapped_column(JSONB, default=list)
    excluded_tickers: Mapped[list | None] = mapped_column(JSONB, default=list)
    criteria: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    schedule: Mapped[str | None] = mapped_column(String(50))  # cron expression
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    results: Mapped[list["ScreeningResult"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class ScreeningResult(Base):
    __tablename__ = "screening_results"
    __table_args__ = (
        Index("ix_screening_results_profile_run", "profile_id", "run_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("screening_profiles.id", ondelete="CASCADE"), nullable=False
    )
    stock_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    passed_criteria: Mapped[dict | None] = mapped_column(JSONB)
    failed_criteria: Mapped[dict | None] = mapped_column(JSONB)
    composite_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    margin_of_safety_pct: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    recommendation: Mapped[str | None] = mapped_column(String(20))  # strong_buy, buy, hold, avoid

    profile: Mapped["ScreeningProfile"] = relationship(back_populates="results")
