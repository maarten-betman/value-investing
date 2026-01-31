import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database import get_db
from app.stocks.models import FinancialStatement, PriceHistory, Stock, ValuationSnapshot
from app.stocks.schemas import (
    FinancialStatementResponse,
    PriceHistoryResponse,
    StockDetailResponse,
    StockResponse,
    ValuationSnapshotResponse,
)

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("", response_model=list[StockResponse])
async def list_stocks(
    exchange: str | None = None,
    sector: str | None = None,
    country: str | None = None,
    is_active: bool = True,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    query = select(Stock).where(Stock.is_active == is_active)

    if exchange:
        query = query.where(Stock.exchange == exchange)
    if sector:
        query = query.where(Stock.sector == sector)
    if country:
        query = query.where(Stock.country == country)

    query = query.order_by(Stock.ticker).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/search", response_model=list[StockResponse])
async def search_stocks(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    query = select(Stock).where(
        (Stock.ticker.ilike(f"%{q}%")) | (Stock.name.ilike(f"%{q}%"))
    ).limit(20)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{stock_id}", response_model=StockDetailResponse)
async def get_stock(
    stock_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(select(Stock).where(Stock.id == stock_id))
    stock = result.scalar_one_or_none()
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    # Get latest valuation
    val_result = await db.execute(
        select(ValuationSnapshot)
        .where(ValuationSnapshot.stock_id == stock_id)
        .order_by(desc(ValuationSnapshot.calculated_at))
        .limit(1)
    )
    latest_val = val_result.scalar_one_or_none()

    response = StockDetailResponse.model_validate(stock)
    if latest_val:
        response.latest_valuation = ValuationSnapshotResponse.model_validate(latest_val)
    return response


@router.get("/{stock_id}/financials", response_model=list[FinancialStatementResponse])
async def get_financials(
    stock_id: uuid.UUID,
    period_type: str = Query("annual", pattern="^(annual|quarterly)$"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FinancialStatement)
        .where(
            FinancialStatement.stock_id == stock_id,
            FinancialStatement.period_type == period_type,
        )
        .order_by(desc(FinancialStatement.period_end))
    )
    return result.scalars().all()


@router.get("/{stock_id}/prices", response_model=list[PriceHistoryResponse])
async def get_prices(
    stock_id: uuid.UUID,
    limit: int = Query(365, ge=1, le=5000),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.stock_id == stock_id)
        .order_by(desc(PriceHistory.date))
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{stock_id}/valuations", response_model=list[ValuationSnapshotResponse])
async def get_valuations(
    stock_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ValuationSnapshot)
        .where(ValuationSnapshot.stock_id == stock_id)
        .order_by(desc(ValuationSnapshot.calculated_at))
        .limit(limit)
    )
    return result.scalars().all()
