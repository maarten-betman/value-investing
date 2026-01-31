import pytest


@pytest.fixture
def sample_financials():
    """Sample financial data for testing valuation calculations."""
    return {
        "eps": 5.0,
        "book_value_per_share": 30.0,
        "current_assets": 500_000_000,
        "total_liabilities": 300_000_000,
        "shares_outstanding": 10_000_000,
        "free_cash_flow": 50_000_000,
        "total_debt": 100_000_000,
        "total_equity": 200_000_000,
        "current_liabilities": 150_000_000,
        "market_price": 40.0,
        "growth_rate": 0.05,
    }
