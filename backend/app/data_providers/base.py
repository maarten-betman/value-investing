from abc import ABC, abstractmethod
from typing import Any


class DataProvider(ABC):
    """Abstract base class for financial data providers."""

    @abstractmethod
    async def get_stock_list(self, exchange: str) -> list[dict[str, Any]]:
        """Get list of stocks for a given exchange."""

    @abstractmethod
    async def get_quote(self, ticker: str) -> dict[str, Any] | None:
        """Get current quote for a ticker."""

    @abstractmethod
    async def get_historical_prices(
        self, ticker: str, from_date: str | None = None, to_date: str | None = None
    ) -> list[dict[str, Any]]:
        """Get historical daily prices for a ticker."""

    @abstractmethod
    async def get_income_statement(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get income statements."""

    @abstractmethod
    async def get_balance_sheet(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get balance sheets."""

    @abstractmethod
    async def get_cash_flow_statement(
        self, ticker: str, period: str = "annual", limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get cash flow statements."""

    @abstractmethod
    async def get_company_profile(self, ticker: str) -> dict[str, Any] | None:
        """Get company profile information."""

    @abstractmethod
    async def get_stock_news(
        self, ticker: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get news articles, optionally filtered by ticker."""

    @abstractmethod
    async def search(self, query: str, exchange: str | None = None) -> list[dict[str, Any]]:
        """Search for stocks by name or ticker."""
