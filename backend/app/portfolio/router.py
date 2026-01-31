import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database import get_db
from app.portfolio.models import Holding, Portfolio, Transaction
from app.portfolio.schemas import (
    HoldingResponse,
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
    TransactionCreate,
    TransactionResponse,
)
from app.stocks.models import PriceHistory, Stock

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])


@router.get("", response_model=list[PortfolioResponse])
async def list_portfolios(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == user.id).order_by(Portfolio.created_at)
    )
    return result.scalars().all()


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    data: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    portfolio = Portfolio(user_id=user.id, **data.model_dump())
    db.add(portfolio)
    await db.flush()
    await db.refresh(portfolio)
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
    )
    portfolio = result.scalar_one_or_none()
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: uuid.UUID,
    data: PortfolioUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
    )
    portfolio = result.scalar_one_or_none()
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(portfolio, key, value)

    await db.flush()
    await db.refresh(portfolio)
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
    )
    portfolio = result.scalar_one_or_none()
    if portfolio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    await db.delete(portfolio)


@router.get("/{portfolio_id}/holdings", response_model=list[HoldingResponse])
async def get_holdings(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Verify ownership
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
    )
    if port_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    result = await db.execute(
        select(Holding).where(Holding.portfolio_id == portfolio_id)
    )
    holdings = result.scalars().all()

    response = []
    for h in holdings:
        stock_result = await db.execute(select(Stock).where(Stock.id == h.stock_id))
        stock = stock_result.scalar_one_or_none()

        # Get latest price
        price_result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.stock_id == h.stock_id)
            .order_by(desc(PriceHistory.date))
            .limit(1)
        )
        latest_price = price_result.scalar_one_or_none()

        resp = HoldingResponse.model_validate(h)
        if stock:
            resp.stock_ticker = stock.ticker
            resp.stock_name = stock.name
        if latest_price and latest_price.close:
            resp.current_price = latest_price.close
            resp.current_value = latest_price.close * h.shares
            cost = h.avg_cost_basis * h.shares
            resp.gain_loss = resp.current_value - cost
            if cost > 0:
                resp.gain_loss_pct = (resp.gain_loss / cost * 100).quantize(Decimal("0.01"))

        response.append(resp)

    return response


@router.post("/{portfolio_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    portfolio_id: uuid.UUID,
    data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Verify ownership
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
    )
    if port_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    # Verify stock exists
    stock_result = await db.execute(select(Stock).where(Stock.id == data.stock_id))
    stock = stock_result.scalar_one_or_none()
    if stock is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock not found")

    transaction = Transaction(portfolio_id=portfolio_id, **data.model_dump())
    db.add(transaction)

    # Update or create holding
    holding_result = await db.execute(
        select(Holding).where(
            Holding.portfolio_id == portfolio_id,
            Holding.stock_id == data.stock_id,
        )
    )
    holding = holding_result.scalar_one_or_none()

    if data.type == "buy":
        if holding:
            total_cost = holding.avg_cost_basis * holding.shares + data.price_per_share * data.shares
            holding.shares += data.shares
            holding.avg_cost_basis = total_cost / holding.shares
        else:
            holding = Holding(
                portfolio_id=portfolio_id,
                stock_id=data.stock_id,
                shares=data.shares,
                avg_cost_basis=data.price_per_share,
                first_purchased=data.executed_at.date(),
            )
            db.add(holding)
    elif data.type == "sell":
        if holding is None or holding.shares < data.shares:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient shares to sell",
            )
        holding.shares -= data.shares
        if holding.shares == 0:
            await db.delete(holding)

    await db.flush()
    await db.refresh(transaction)

    resp = TransactionResponse.model_validate(transaction)
    resp.stock_ticker = stock.ticker
    return resp


@router.get("/{portfolio_id}/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    port_result = await db.execute(
        select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.user_id == user.id)
    )
    if port_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    result = await db.execute(
        select(Transaction)
        .where(Transaction.portfolio_id == portfolio_id)
        .order_by(desc(Transaction.executed_at))
    )
    transactions = result.scalars().all()

    response = []
    for t in transactions:
        stock_result = await db.execute(select(Stock).where(Stock.id == t.stock_id))
        stock = stock_result.scalar_one_or_none()
        resp = TransactionResponse.model_validate(t)
        if stock:
            resp.stock_ticker = stock.ticker
        response.append(resp)

    return response
