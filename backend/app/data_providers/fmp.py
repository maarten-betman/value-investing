import logging
from typing import Any

import httpx

from app.config import settings
from app.data_providers.base import DataProvider
from app.data_providers.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

# Cache TTLs
CACHE_TTL_PRICES = 86400  # 1 day
CACHE_TTL_FUNDAMENTALS = 604800  # 7 days
CACHE_TTL_PROFILE = 604800  # 7 days
CACHE_TTL_NEWS = 3600  # 1 hour
CACHE_TTL_STOCK_LIST = 86400  # 1 day


class FMPProvider(DataProvider):
    """Financial Modeling Prep data provider."""

    def __init__(self):
        self.base_url = settings.fmp_base_url
        self.api_key = settings.fmp_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def _request(self, endpoint: str, params: dict | None = None) -> Any:
        """Make an authenticated request to FMP API with retry logic."""
        client = await self._get_client()
        url = f"{self.base_url}/{endpoint}"
        request_params = {"apikey": self.api_key}
        if params:
            request_params.update(params)

        retries = 3
        for attempt in range(retries):
            try:
                response = await client.get(url, params=request_params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limited — wait and retry
                    wait = 2 ** (attempt + 1)
                    logger.warning(f"FMP rate limited, retrying in {wait}s")
                    import asyncio

                    await asyncio.sleep(wait)
                    continue
                logger.error(f"FMP API error: {e.response.status_code} for {endpoint}")
                raise
            except httpx.RequestError as e:
                if attempt < retries - 1:
                    wait = 2 ** (attempt + 1)
                    logger.warning(f"FMP request error, retrying in {wait}s: {e}")
                    import asyncio

                    await asyncio.sleep(wait)
                    continue
                raise

        return None

    async def _cached_request(
        self, cache_key: str, endpoint: str, params: dict | None = None, ttl: int = CACHE_TTL_PRICES
    ) -> Any:
        """Request with Redis caching."""
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached

        data = await self._request(endpoint, params)
        if data is not None:
            await cache_set(cache_key, data, ttl)
        return data

    async def get_stock_list(self, exchange: str = "EURONEXT") -> list[dict[str, Any]]:
        cache_key = f"fmp:stock_list:{exchange}"
        data = await self._cached_request(
            cache_key, f"symbol/available-{exchange.lower()}", ttl=CACHE_TTL_STOCK_LIST
        )
        return data or []

    async def get_quote(self, ticker: str) -> dict[str, Any] | None:
        cache_key = f"fmp:quote:{ticker}"
        data = await self._cached_request(
            cache_key, f"quote/{ticker}", ttl=CACHE_TTL_PRICES
        )
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    async def get_historical_prices(
        self, ticker: str, from_date: str | None = None, to_date: str | None = None
    ) -> list[dict[str, Any]]:
        params = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        cache_key = f"fmp:prices:{ticker}:{from_date}:{to_date}"
        data = await self._cached_request(
            cache_key, f"historical-price-full/{ticker}", params=params, ttl=CACHE_TTL_PRICES
        )
        if data and isinstance(data, dict):
            return data.get("historical", [])
        return []

    async def get_income_statement(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[dict[str, Any]]:
        cache_key = f"fmp:income:{ticker}:{period}:{limit}"
        data = await self._cached_request(
            cache_key,
            f"income-statement/{ticker}",
            params={"period": period, "limit": str(limit)},
            ttl=CACHE_TTL_FUNDAMENTALS,
        )
        return data or []

    async def get_balance_sheet(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[dict[str, Any]]:
        cache_key = f"fmp:balance:{ticker}:{period}:{limit}"
        data = await self._cached_request(
            cache_key,
            f"balance-sheet-statement/{ticker}",
            params={"period": period, "limit": str(limit)},
            ttl=CACHE_TTL_FUNDAMENTALS,
        )
        return data or []

    async def get_cash_flow_statement(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[dict[str, Any]]:
        cache_key = f"fmp:cashflow:{ticker}:{period}:{limit}"
        data = await self._cached_request(
            cache_key,
            f"cash-flow-statement/{ticker}",
            params={"period": period, "limit": str(limit)},
            ttl=CACHE_TTL_FUNDAMENTALS,
        )
        return data or []

    async def get_company_profile(self, ticker: str) -> dict[str, Any] | None:
        cache_key = f"fmp:profile:{ticker}"
        data = await self._cached_request(
            cache_key, f"profile/{ticker}", ttl=CACHE_TTL_PROFILE
        )
        if data and isinstance(data, list) and len(data) > 0:
            return data[0]
        return None

    async def get_stock_news(
        self, ticker: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        params: dict[str, str] = {"limit": str(limit)}
        if ticker:
            params["tickers"] = ticker
        cache_key = f"fmp:news:{ticker}:{limit}"
        data = await self._cached_request(
            cache_key, "stock_news", params=params, ttl=CACHE_TTL_NEWS
        )
        return data or []

    async def search(self, query: str, exchange: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, str] = {"query": query, "limit": "20"}
        if exchange:
            params["exchange"] = exchange
        # Don't cache search results
        data = await self._request("search", params)
        return data or []

    async def get_key_metrics(self, ticker: str, period: str = "annual", limit: int = 10) -> list[dict[str, Any]]:
        cache_key = f"fmp:metrics:{ticker}:{period}:{limit}"
        data = await self._cached_request(
            cache_key,
            f"key-metrics/{ticker}",
            params={"period": period, "limit": str(limit)},
            ttl=CACHE_TTL_FUNDAMENTALS,
        )
        return data or []

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# Singleton instance
fmp_provider = FMPProvider()
