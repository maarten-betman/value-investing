import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.data_providers.cache import close_redis
from app.data_providers.fmp import fmp_provider
from app.portfolio.router import router as portfolio_router
from app.scheduler.setup import get_scheduler_status, scheduler, setup_scheduler
from app.screening.router import router as screening_router
from app.stocks.router import router as stocks_router
from app.watchlist.router import router as watchlist_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
logging.basicConfig(level=logging.INFO, format="%(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_scheduler()
    scheduler.start()
    logging.getLogger(__name__).info("Application started")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    await fmp_provider.close()
    await close_redis()
    logging.getLogger(__name__).info("Application stopped")


app = FastAPI(
    title="Value Investing Tracker",
    description="Stock screening and portfolio management using Graham's value investing methodology",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(stocks_router)
app.include_router(screening_router)
app.include_router(portfolio_router)
app.include_router(watchlist_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/scheduler/jobs")
async def list_scheduler_jobs():
    return get_scheduler_status()
