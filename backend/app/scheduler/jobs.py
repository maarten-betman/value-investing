"""Scheduled job definitions for automated data sync and screening."""

import logging

from sqlalchemy import select

from app.database import async_session_factory
from app.screening.models import ScreeningProfile
from app.screening.service import run_screening
from app.stocks.models import Stock
from app.stocks.service import sync_eod_prices, sync_fundamentals, sync_stock_universe

logger = logging.getLogger(__name__)


async def job_sync_stock_universe():
    """Sync the list of available stocks from configured exchanges."""
    logger.info("Starting stock universe sync")
    async with async_session_factory() as db:
        try:
            count = await sync_stock_universe(db, exchange="EURONEXT")
            await db.commit()
            logger.info(f"Stock universe sync complete: {count} new stocks")
        except Exception:
            await db.rollback()
            logger.exception("Stock universe sync failed")


async def job_sync_eod_prices():
    """Sync end-of-day prices for all active stocks."""
    logger.info("Starting EOD price sync")
    async with async_session_factory() as db:
        try:
            result = await db.execute(select(Stock).where(Stock.is_active == True))  # noqa: E712
            stocks = result.scalars().all()

            total = 0
            for stock in stocks:
                try:
                    count = await sync_eod_prices(db, stock)
                    total += count
                except Exception:
                    logger.exception(f"Failed to sync prices for {stock.ticker}")

            await db.commit()
            logger.info(f"EOD price sync complete: {total} new prices across {len(stocks)} stocks")
        except Exception:
            await db.rollback()
            logger.exception("EOD price sync failed")


async def job_sync_fundamentals():
    """Sync financial statements for all active stocks."""
    logger.info("Starting fundamentals sync")
    async with async_session_factory() as db:
        try:
            result = await db.execute(select(Stock).where(Stock.is_active == True))  # noqa: E712
            stocks = result.scalars().all()

            total = 0
            for stock in stocks:
                try:
                    count = await sync_fundamentals(db, stock)
                    total += count
                except Exception:
                    logger.exception(f"Failed to sync fundamentals for {stock.ticker}")

            await db.commit()
            logger.info(f"Fundamentals sync complete: {total} new statements")
        except Exception:
            await db.rollback()
            logger.exception("Fundamentals sync failed")


async def job_run_all_screenings():
    """Run all active screening profiles."""
    logger.info("Starting screening runs")
    async with async_session_factory() as db:
        try:
            result = await db.execute(
                select(ScreeningProfile).where(ScreeningProfile.is_active == True)  # noqa: E712
            )
            profiles = result.scalars().all()

            for profile in profiles:
                try:
                    results = await run_screening(db, profile)
                    logger.info(f"Screening '{profile.name}': {len(results)} results")
                except Exception:
                    logger.exception(f"Screening '{profile.name}' failed")

            await db.commit()
            logger.info(f"All screenings complete: {len(profiles)} profiles executed")
        except Exception:
            await db.rollback()
            logger.exception("Screening runs failed")
