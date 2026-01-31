"""Graham screening criteria — configurable thresholds for stock filtering."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.screening.valuations import ValuationResult


@dataclass
class GrahamCriteria:
    """Default Graham screening criteria. All thresholds are configurable."""

    max_pe_ratio: Decimal = Decimal("15")
    max_pb_ratio: Decimal = Decimal("1.5")
    max_pe_times_pb: Decimal = Decimal("22.5")
    min_current_ratio: Decimal = Decimal("2.0")
    max_debt_to_equity: Decimal = Decimal("0.5")
    min_positive_earnings_years: int = 5
    min_dividend_years: int = 5
    min_earnings_growth_pct: Decimal = Decimal("3.0")
    min_margin_of_safety_pct: Decimal = Decimal("30.0")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GrahamCriteria":
        """Create criteria from a JSON-serializable dict (e.g., from screening profile)."""
        kwargs = {}
        field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
        for key, value in data.items():
            if key in field_types:
                if "Decimal" in str(field_types[key]):
                    kwargs[key] = Decimal(str(value))
                elif "int" in str(field_types[key]):
                    kwargs[key] = int(value)
                else:
                    kwargs[key] = value
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            k: float(v) if isinstance(v, Decimal) else v
            for k, v in self.__dict__.items()
        }


@dataclass
class CriterionResult:
    name: str
    passed: bool
    actual_value: Any = None
    threshold: Any = None
    description: str = ""


def evaluate_criteria(
    valuation: ValuationResult,
    criteria: GrahamCriteria,
    positive_earnings_years: int = 0,
    dividend_years: int = 0,
    avg_earnings_growth: Decimal | None = None,
) -> list[CriterionResult]:
    """Evaluate a stock's valuation against Graham criteria. Returns list of results."""
    results: list[CriterionResult] = []

    # P/E ratio
    if valuation.pe_ratio is not None:
        results.append(CriterionResult(
            name="pe_ratio",
            passed=valuation.pe_ratio <= criteria.max_pe_ratio,
            actual_value=float(valuation.pe_ratio),
            threshold=float(criteria.max_pe_ratio),
            description=f"P/E ratio {valuation.pe_ratio} vs max {criteria.max_pe_ratio}",
        ))

    # P/B ratio
    if valuation.pb_ratio is not None:
        results.append(CriterionResult(
            name="pb_ratio",
            passed=valuation.pb_ratio <= criteria.max_pb_ratio,
            actual_value=float(valuation.pb_ratio),
            threshold=float(criteria.max_pb_ratio),
            description=f"P/B ratio {valuation.pb_ratio} vs max {criteria.max_pb_ratio}",
        ))

    # P/E × P/B combined
    if valuation.pe_ratio is not None and valuation.pb_ratio is not None:
        combined = valuation.pe_ratio * valuation.pb_ratio
        results.append(CriterionResult(
            name="pe_times_pb",
            passed=combined <= criteria.max_pe_times_pb,
            actual_value=float(combined),
            threshold=float(criteria.max_pe_times_pb),
            description=f"P/E × P/B = {combined:.2f} vs max {criteria.max_pe_times_pb}",
        ))

    # Current ratio
    if valuation.current_ratio is not None:
        results.append(CriterionResult(
            name="current_ratio",
            passed=valuation.current_ratio >= criteria.min_current_ratio,
            actual_value=float(valuation.current_ratio),
            threshold=float(criteria.min_current_ratio),
            description=f"Current ratio {valuation.current_ratio} vs min {criteria.min_current_ratio}",
        ))

    # Debt to equity
    if valuation.debt_to_equity is not None:
        results.append(CriterionResult(
            name="debt_to_equity",
            passed=valuation.debt_to_equity <= criteria.max_debt_to_equity,
            actual_value=float(valuation.debt_to_equity),
            threshold=float(criteria.max_debt_to_equity),
            description=f"D/E {valuation.debt_to_equity} vs max {criteria.max_debt_to_equity}",
        ))

    # Positive earnings history
    results.append(CriterionResult(
        name="positive_earnings_years",
        passed=positive_earnings_years >= criteria.min_positive_earnings_years,
        actual_value=positive_earnings_years,
        threshold=criteria.min_positive_earnings_years,
        description=f"{positive_earnings_years} years positive earnings vs min {criteria.min_positive_earnings_years}",
    ))

    # Dividend history
    results.append(CriterionResult(
        name="dividend_years",
        passed=dividend_years >= criteria.min_dividend_years,
        actual_value=dividend_years,
        threshold=criteria.min_dividend_years,
        description=f"{dividend_years} years dividends vs min {criteria.min_dividend_years}",
    ))

    # Earnings growth
    if avg_earnings_growth is not None:
        results.append(CriterionResult(
            name="earnings_growth",
            passed=avg_earnings_growth >= criteria.min_earnings_growth_pct,
            actual_value=float(avg_earnings_growth),
            threshold=float(criteria.min_earnings_growth_pct),
            description=f"Avg growth {avg_earnings_growth}% vs min {criteria.min_earnings_growth_pct}%",
        ))

    # Margin of safety
    if valuation.margin_of_safety_pct is not None:
        results.append(CriterionResult(
            name="margin_of_safety",
            passed=valuation.margin_of_safety_pct >= criteria.min_margin_of_safety_pct,
            actual_value=float(valuation.margin_of_safety_pct),
            threshold=float(criteria.min_margin_of_safety_pct),
            description=f"MoS {valuation.margin_of_safety_pct}% vs min {criteria.min_margin_of_safety_pct}%",
        ))

    return results
