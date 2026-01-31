import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database import get_db
from app.stocks.models import PriceHistory, Stock, ValuationSnapshot
from app.watchlist.models import WatchlistItem
from app.watchlist.schemas import (
    WatchlistItemCreate,
    WatchlistItemResponse,
    WatchlistItemUpdate,
)

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemResponse])
async def list_watchlist(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WatchlistItem)
        .where(WatchlistItem.user_id == user.id)
        .order_by(WatchlistItem.added_at)
    )
    items = result.scalars().all()

    response = []
    for item in items:
        stock_result = await db.execute(select(Stock).where(Stock.id == item.stock_id))
        stock = stock_result.scalar_one_or_none()

        price_result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.stock_id == item.stock_id)
            .order_by(desc(PriceHistory.date))
            .limit(1)
        )
        latest_price = price_result.scalar_one_or_none()

        val_result = await db.execute(
            select(ValuationSnapshot)
            .where(ValuationSnapshot.stock_id == item.stock_id)
            .order_by(desc(ValuationSnapshot.calculated_at))
            .limit(1)
        )
        latest_val = val_result.scalar_one_or_none()

        resp = WatchlistItemResponse.model_validate(item)
        if stock:
            resp.stock_ticker = stock.ticker
            resp.stock_name = stock.name
        if latest_price:
            resp.current_price = latest_price.close
        if latest_val:
            resp.current_mos_pct = latest_val.margin_of_safety_pct

        response.append(resp)

    return response


@router.post("", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    data: WatchlistItemCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Verify stock exists
    stock_result = await db.execute(select(Stock).where(Stock.id == data.stock_id))
    stock = stock_result.scalar_one_or_none()
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    item = WatchlistItem(user_id=user.id, **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)

    resp = WatchlistItemResponse.model_validate(item)
    resp.stock_ticker = stock.ticker
    resp.stock_name = stock.name
    return resp


@router.put("/{item_id}", response_model=WatchlistItemResponse)
async def update_watchlist_item(
    item_id: uuid.UUID,
    data: WatchlistItemUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.id == item_id,
            WatchlistItem.user_id == user.id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    await db.flush()
    await db.refresh(item)
    return WatchlistItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.id == item_id,
            WatchlistItem.user_id == user.id,
        )
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    await db.delete(item)
