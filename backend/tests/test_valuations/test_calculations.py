"""Tests for Graham valuation calculations."""

from decimal import Decimal

from app.screening.valuations import (
    calculate_dcf,
    calculate_earnings_stability,
    calculate_graham_formula,
    calculate_graham_number,
    calculate_margin_of_safety,
    calculate_ncav_per_share,
)


class TestGrahamNumber:
    def test_basic_calculation(self):
        result = calculate_graham_number(Decimal("5"), Decimal("30"))
        # √(22.5 × 5 × 30) = √3375 ≈ 58.09
        assert result is not None
        assert Decimal("58") < result < Decimal("59")

    def test_negative_eps_returns_none(self):
        assert calculate_graham_number(Decimal("-2"), Decimal("30")) is None

    def test_zero_bvps_returns_none(self):
        assert calculate_graham_number(Decimal("5"), Decimal("0")) is None

    def test_none_inputs(self):
        assert calculate_graham_number(None, Decimal("30")) is None
        assert calculate_graham_number(Decimal("5"), None) is None


class TestGrahamFormula:
    def test_basic_calculation(self):
        # V = (EPS × (8.5 + 2g) × 4.4) / Y
        # V = (5 × (8.5 + 2×5) × 4.4) / 4.4 = 5 × 18.5 = 92.5
        result = calculate_graham_formula(
            Decimal("5"), Decimal("5"), Decimal("4.4")
        )
        assert result is not None
        assert Decimal("92") < result < Decimal("93")

    def test_negative_eps_returns_none(self):
        assert calculate_graham_formula(Decimal("-5"), Decimal("5")) is None

    def test_none_growth_returns_none(self):
        assert calculate_graham_formula(Decimal("5"), None) is None


class TestNCAV:
    def test_basic_calculation(self):
        result = calculate_ncav_per_share(
            Decimal("500000000"), Decimal("300000000"), Decimal("10000000")
        )
        # (500M - 300M) / 10M = 20
        assert result == Decimal("20.0000")

    def test_negative_ncav(self):
        result = calculate_ncav_per_share(
            Decimal("200000000"), Decimal("300000000"), Decimal("10000000")
        )
        assert result is not None
        assert result < 0

    def test_zero_shares(self):
        assert calculate_ncav_per_share(Decimal("500"), Decimal("300"), Decimal("0")) is None


class TestDCF:
    def test_basic_calculation(self):
        result = calculate_dcf(
            Decimal("50000000"),
            Decimal("0.05"),
            Decimal("0.10"),
            Decimal("0.02"),
            10,
            Decimal("10000000"),
        )
        assert result is not None
        assert result > 0

    def test_negative_fcf_returns_none(self):
        assert calculate_dcf(Decimal("-50000000"), Decimal("0.05")) is None

    def test_none_fcf_returns_none(self):
        assert calculate_dcf(None, Decimal("0.05")) is None


class TestMarginOfSafety:
    def test_undervalued(self):
        result = calculate_margin_of_safety(Decimal("100"), Decimal("50"))
        assert result == Decimal("50.00")

    def test_overvalued(self):
        result = calculate_margin_of_safety(Decimal("50"), Decimal("100"))
        assert result == Decimal("-100.00")

    def test_fair_value(self):
        result = calculate_margin_of_safety(Decimal("100"), Decimal("100"))
        assert result == Decimal("0.00")


class TestEarningsStability:
    def test_all_positive_growing(self):
        eps = [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4"), Decimal("5")]
        result = calculate_earnings_stability(eps)
        assert result is not None
        assert result > Decimal("80")

    def test_mixed_earnings(self):
        eps = [Decimal("1"), Decimal("-1"), Decimal("2"), Decimal("-2"), Decimal("3")]
        result = calculate_earnings_stability(eps)
        assert result is not None
        assert result < Decimal("70")

    def test_too_few_years(self):
        assert calculate_earnings_stability([Decimal("1"), Decimal("2")]) is None
