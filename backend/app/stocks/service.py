"""Stock data sync and management service."""

import logging
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_providers.fmp import fmp_provider
from app.stocks.models import FinancialStatement, PriceHistory, Stock

logger = logging.getLogger(__name__)


async def sync_stock_universe(db: AsyncSession, exchange: str = "EURONEXT") -> int:
    """Sync the list of available stocks from FMP for a given exchange."""
    stock_list = await fmp_provider.get_stock_list(exchange)
    if not stock_list:
        logger.warning(f"No stocks returned from FMP for exchange {exchange}")
        return 0

    created = 0
    for item in stock_list:
        ticker = item.get("symbol", "")
        if not ticker:
            continue

        existing = await db.execute(select(Stock).where(Stock.ticker == ticker))
        if existing.scalar_one_or_none():
            continue

        # Fetch profile for additional info
        profile = await fmp_provider.get_company_profile(ticker)

        stock = Stock(
            ticker=ticker,
            name=item.get("name", ticker),
            exchange=exchange,
            sector=profile.get("sector") if profile else None,
            industry=profile.get("industry") if profile else None,
            currency=profile.get("currency", "EUR") if profile else "EUR",
            country=profile.get("country") if profile else None,
            market_cap=profile.get("mktCap") if profile else None,
        )
        db.add(stock)
        created += 1

    await db.flush()
    logger.info(f"Synced {created} new stocks for {exchange}")
    return created


async def sync_eod_prices(db: AsyncSession, stock: Stock, from_date: str | None = None) -> int:
    """Sync end-of-day prices for a stock."""
    prices = await fmp_provider.get_historical_prices(stock.ticker, from_date=from_date)
    if not prices:
        return 0

    created = 0
    for p in prices:
        price_date = date.fromisoformat(p["date"])

        existing = await db.execute(
            select(PriceHistory).where(
                PriceHistory.stock_id == stock.id,
                PriceHistory.date == price_date,
            )
        )
        if existing.scalar_one_or_none():
            continue

        price = PriceHistory(
            stock_id=stock.id,
            date=price_date,
            open=p.get("open"),
            high=p.get("high"),
            low=p.get("low"),
            close=p.get("close"),
            adj_close=p.get("adjClose"),
            volume=p.get("volume"),
        )
        db.add(price)
        created += 1

    await db.flush()
    stock.last_data_refresh = datetime.now(timezone.utc)
    return created


async def sync_fundamentals(db: AsyncSession, stock: Stock) -> int:
    """Sync financial statements (income, balance sheet, cash flow) for a stock."""
    income = await fmp_provider.get_income_statement(stock.ticker, period="annual", limit=10)
    balance = await fmp_provider.get_balance_sheet(stock.ticker, period="annual", limit=10)
    cashflow = await fmp_provider.get_cash_flow_statement(stock.ticker, period="annual", limit=10)

    # Index balance sheet and cash flow by date for joining
    balance_by_date = {b.get("date", ""): b for b in balance}
    cashflow_by_date = {c.get("date", ""): c for c in cashflow}

    created = 0
    for inc in income:
        period_end_str = inc.get("date", "")
        if not period_end_str:
            continue

        period_end = date.fromisoformat(period_end_str)

        existing = await db.execute(
            select(FinancialStatement).where(
                FinancialStatement.stock_id == stock.id,
                FinancialStatement.period_type == "annual",
                FinancialStatement.period_end == period_end,
            )
        )
        if existing.scalar_one_or_none():
            continue

        bal = balance_by_date.get(period_end_str, {})
        cf = cashflow_by_date.get(period_end_str, {})

        shares = inc.get("weightedAverageShsOut") or inc.get("weightedAverageShsOutDil")
        total_equity = bal.get("totalStockholdersEquity")
        bvps = None
        if shares and total_equity and shares > 0:
            bvps = total_equity / shares

        stmt = FinancialStatement(
            stock_id=stock.id,
            period_type="annual",
            period_end=period_end,
            revenue=inc.get("revenue"),
            net_income=inc.get("netIncome"),
            eps=inc.get("eps"),
            book_value_per_share=bvps,
            total_assets=bal.get("totalAssets"),
            total_liabilities=bal.get("totalLiabilities"),
            current_assets=bal.get("totalCurrentAssets"),
            current_liabilities=bal.get("totalCurrentLiabilities"),
            total_debt=bal.get("totalDebt"),
            total_equity=total_equity,
            dividends_per_share=inc.get("dividendsPaid"),
            free_cash_flow=cf.get("freeCashFlow"),
            operating_cash_flow=cf.get("operatingCashFlow"),
            shares_outstanding=shares,
            raw_data={"income": inc, "balance": bal, "cashflow": cf},
        )
        db.add(stmt)
        created += 1

    await db.flush()
    return created
