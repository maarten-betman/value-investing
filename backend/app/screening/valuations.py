"""Value investing valuation calculations based on Benjamin Graham's methodology."""

import math
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ValuationResult:
    graham_number: Decimal | None = None
    graham_formula_value: Decimal | None = None
    ncav_per_share: Decimal | None = None
    dcf_value: Decimal | None = None
    pe_ratio: Decimal | None = None
    pb_ratio: Decimal | None = None
    current_ratio: Decimal | None = None
    debt_to_equity: Decimal | None = None
    dividend_yield: Decimal | None = None
    margin_of_safety_pct: Decimal | None = None
    earnings_stability: Decimal | None = None
    composite_score: Decimal | None = None


def calculate_graham_number(eps: Decimal | None, book_value_per_share: Decimal | None) -> Decimal | None:
    """
    Graham Number = √(22.5 × EPS × Book Value per Share)

    A stock trading below its Graham Number may be undervalued.
    Requires both EPS and BVPS to be positive.
    """
    if eps is None or book_value_per_share is None:
        return None
    if eps <= 0 or book_value_per_share <= 0:
        return None

    product = Decimal("22.5") * eps * book_value_per_share
    return Decimal(str(math.sqrt(float(product)))).quantize(Decimal("0.0001"))


def calculate_graham_formula(
    eps: Decimal | None,
    growth_rate: Decimal | None,
    corporate_bond_yield: Decimal = Decimal("4.4"),
) -> Decimal | None:
    """
    Graham Formula (revised): V = (EPS × (8.5 + 2g) × 4.4) / Y

    Where:
    - EPS = trailing twelve months earnings per share
    - g = expected 5-year annual growth rate (as percentage, e.g., 5 for 5%)
    - 4.4 = Graham's baseline corporate bond yield
    - Y = current AAA corporate bond yield
    """
    if eps is None or growth_rate is None or eps <= 0:
        return None
    if corporate_bond_yield <= 0:
        return None

    value = (eps * (Decimal("8.5") + Decimal("2") * growth_rate) * Decimal("4.4")) / corporate_bond_yield
    return max(value, Decimal("0")).quantize(Decimal("0.0001"))


def calculate_ncav_per_share(
    current_assets: Decimal | None,
    total_liabilities: Decimal | None,
    shares_outstanding: Decimal | None,
) -> Decimal | None:
    """
    NCAV per share = (Current Assets - Total Liabilities) / Shares Outstanding

    Deep value metric. Stocks trading below NCAV are trading below liquidation value.
    """
    if current_assets is None or total_liabilities is None or shares_outstanding is None:
        return None
    if shares_outstanding <= 0:
        return None

    ncav = (current_assets - total_liabilities) / shares_outstanding
    return ncav.quantize(Decimal("0.0001"))


def calculate_dcf(
    free_cash_flow: Decimal | None,
    growth_rate: Decimal | None,
    discount_rate: Decimal = Decimal("0.10"),
    terminal_growth_rate: Decimal = Decimal("0.02"),
    projection_years: int = 10,
    shares_outstanding: Decimal | None = None,
) -> Decimal | None:
    """
    Simplified Discounted Cash Flow.

    Projects FCF forward, discounts to present value, adds terminal value.
    Returns per-share value if shares_outstanding is provided, else total.
    """
    if free_cash_flow is None or growth_rate is None:
        return None
    if free_cash_flow <= 0 or discount_rate <= 0:
        return None

    total_pv = Decimal("0")
    projected_fcf = free_cash_flow

    for year in range(1, projection_years + 1):
        projected_fcf = projected_fcf * (1 + growth_rate)
        discount_factor = (1 + discount_rate) ** year
        total_pv += projected_fcf / discount_factor

    # Terminal value using Gordon Growth Model
    terminal_fcf = projected_fcf * (1 + terminal_growth_rate)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
    terminal_pv = terminal_value / ((1 + discount_rate) ** projection_years)

    total_value = total_pv + terminal_pv

    if shares_outstanding and shares_outstanding > 0:
        return (total_value / shares_outstanding).quantize(Decimal("0.0001"))

    return total_value.quantize(Decimal("0.0001"))


def calculate_margin_of_safety(
    intrinsic_value: Decimal | None, market_price: Decimal | None
) -> Decimal | None:
    """
    Margin of Safety = (Intrinsic Value - Market Price) / Intrinsic Value × 100

    Positive means stock is undervalued. Negative means overvalued.
    """
    if intrinsic_value is None or market_price is None:
        return None
    if intrinsic_value <= 0:
        return None

    mos = ((intrinsic_value - market_price) / intrinsic_value) * 100
    return mos.quantize(Decimal("0.01"))


def calculate_earnings_stability(eps_history: list[Decimal | None]) -> Decimal | None:
    """
    Score from 0-100 indicating how consistent earnings have been.

    Factors:
    - Proportion of positive earnings years
    - Year-over-year earnings growth consistency
    """
    valid_eps = [e for e in eps_history if e is not None]
    if len(valid_eps) < 3:
        return None

    # Proportion of positive earnings
    positive_count = sum(1 for e in valid_eps if e > 0)
    positive_ratio = Decimal(str(positive_count / len(valid_eps)))

    # Consistency of year-over-year direction (growth)
    growth_count = 0
    for i in range(1, len(valid_eps)):
        if valid_eps[i] >= valid_eps[i - 1]:
            growth_count += 1

    growth_ratio = Decimal(str(growth_count / (len(valid_eps) - 1))) if len(valid_eps) > 1 else Decimal("0")

    # Weighted score
    score = (positive_ratio * Decimal("60") + growth_ratio * Decimal("40"))
    return min(score, Decimal("100")).quantize(Decimal("0.01"))


def calculate_composite_score(
    valuation: ValuationResult,
    market_price: Decimal | None,
    weights: dict[str, float] | None = None,
) -> Decimal | None:
    """
    Weighted composite score (0-100) combining multiple valuation signals.
    Higher = more attractive from a value investing perspective.
    """
    if market_price is None or market_price <= 0:
        return None

    default_weights = {
        "graham_number": 0.25,
        "graham_formula": 0.20,
        "ncav": 0.15,
        "dcf": 0.20,
        "quality": 0.20,
    }
    w = weights or default_weights

    total_score = Decimal("0")
    total_weight = Decimal("0")

    # Graham Number score
    if valuation.graham_number is not None:
        ratio = valuation.graham_number / market_price
        score = min(ratio * Decimal("50"), Decimal("100"))
        total_score += score * Decimal(str(w["graham_number"]))
        total_weight += Decimal(str(w["graham_number"]))

    # Graham Formula score
    if valuation.graham_formula_value is not None:
        ratio = valuation.graham_formula_value / market_price
        score = min(ratio * Decimal("50"), Decimal("100"))
        total_score += score * Decimal(str(w["graham_formula"]))
        total_weight += Decimal(str(w["graham_formula"]))

    # NCAV score
    if valuation.ncav_per_share is not None:
        if valuation.ncav_per_share > 0:
            ratio = valuation.ncav_per_share / market_price
            score = min(ratio * Decimal("100"), Decimal("100"))
        else:
            score = Decimal("0")
        total_score += score * Decimal(str(w["ncav"]))
        total_weight += Decimal(str(w["ncav"]))

    # DCF score
    if valuation.dcf_value is not None:
        ratio = valuation.dcf_value / market_price
        score = min(ratio * Decimal("50"), Decimal("100"))
        total_score += score * Decimal(str(w["dcf"]))
        total_weight += Decimal(str(w["dcf"]))

    # Quality score (earnings stability + low debt)
    quality_score = Decimal("0")
    quality_factors = 0
    if valuation.earnings_stability is not None:
        quality_score += valuation.earnings_stability
        quality_factors += 1
    if valuation.debt_to_equity is not None and valuation.debt_to_equity >= 0:
        # Lower D/E = better. Score inversely.
        de_score = max(Decimal("100") - valuation.debt_to_equity * Decimal("100"), Decimal("0"))
        quality_score += de_score
        quality_factors += 1
    if quality_factors > 0:
        quality_score = quality_score / Decimal(str(quality_factors))
        total_score += quality_score * Decimal(str(w["quality"]))
        total_weight += Decimal(str(w["quality"]))

    if total_weight > 0:
        return (total_score / total_weight).quantize(Decimal("0.01"))

    return None
