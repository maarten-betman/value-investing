"""APScheduler configuration and job registration."""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.scheduler.jobs import (
    job_run_all_screenings,
    job_sync_eod_prices,
    job_sync_fundamentals,
    job_sync_stock_universe,
)

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)


def setup_scheduler():
    """Register all scheduled jobs."""

    # Sync stock universe — daily at 06:00 CET
    scheduler.add_job(
        job_sync_stock_universe,
        CronTrigger(hour=6, minute=0),
        id="sync_stock_universe",
        name="Sync Stock Universe",
        replace_existing=True,
    )

    # Sync EOD prices — daily at 18:30 CET (after market close)
    scheduler.add_job(
        job_sync_eod_prices,
        CronTrigger(hour=18, minute=30, day_of_week="mon-fri"),
        id="sync_eod_prices",
        name="Sync EOD Prices",
        replace_existing=True,
    )

    # Sync fundamentals — weekly on Sunday at 02:00
    scheduler.add_job(
        job_sync_fundamentals,
        CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="sync_fundamentals",
        name="Sync Fundamentals",
        replace_existing=True,
    )

    # Run screenings — daily at 19:00 CET on weekdays
    scheduler.add_job(
        job_run_all_screenings,
        CronTrigger(hour=19, minute=0, day_of_week="mon-fri"),
        id="run_all_screenings",
        name="Run All Screenings",
        replace_existing=True,
    )

    logger.info("Scheduler jobs registered")


def get_scheduler_status() -> list[dict]:
    """Get status of all scheduled jobs."""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return jobs
