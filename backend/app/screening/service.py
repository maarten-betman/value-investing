"""Screening orchestration — runs valuation calculations and criteria evaluation."""

import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.screening.criteria import CriterionResult, GrahamCriteria, evaluate_criteria
from app.screening.models import ScreeningProfile, ScreeningResult
from app.screening.valuations import (
    ValuationResult,
    calculate_composite_score,
    calculate_dcf,
    calculate_earnings_stability,
    calculate_graham_formula,
    calculate_graham_number,
    calculate_margin_of_safety,
    calculate_ncav_per_share,
)
from app.stocks.models import FinancialStatement, PriceHistory, Stock, ValuationSnapshot

logger = logging.getLogger(__name__)


async def calculate_stock_valuation(db: AsyncSession, stock: Stock) -> ValuationResult | None:
    """Calculate all valuation metrics for a stock based on its financial data."""

    # Get latest financials (annual)
    stmt_result = await db.execute(
        select(FinancialStatement)
        .where(
            FinancialStatement.stock_id == stock.id,
            FinancialStatement.period_type == "annual",
        )
        .order_by(desc(FinancialStatement.period_end))
        .limit(10)
    )
    statements = list(stmt_result.scalars().all())

    if not statements:
        logger.debug(f"No financial statements for {stock.ticker}")
        return None

    latest = statements[0]

    # Get latest price
    price_result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.stock_id == stock.id)
        .order_by(desc(PriceHistory.date))
        .limit(1)
    )
    latest_price_row = price_result.scalar_one_or_none()
    market_price = latest_price_row.close if latest_price_row else None

    # EPS history for stability
    eps_history = [s.eps for s in reversed(statements)]

    # Earnings growth (avg annual over available history)
    growth_rate = None
    if len(statements) >= 2:
        first_eps = statements[-1].eps
        last_eps = statements[0].eps
        years = len(statements) - 1
        if first_eps and last_eps and first_eps > 0 and years > 0:
            growth_rate = ((last_eps / first_eps) ** (Decimal("1") / Decimal(str(years))) - 1) * 100

    # Calculate valuations
    graham_number = calculate_graham_number(latest.eps, latest.book_value_per_share)
    graham_formula = calculate_graham_formula(latest.eps, growth_rate / 100 if growth_rate else None)
    ncav = calculate_ncav_per_share(
        latest.current_assets, latest.total_liabilities, latest.shares_outstanding
    )
    dcf = calculate_dcf(
        latest.free_cash_flow,
        growth_rate / 100 if growth_rate else None,
        shares_outstanding=latest.shares_outstanding,
    )

    # Ratios
    pe_ratio = None
    if market_price and latest.eps and latest.eps > 0:
        pe_ratio = market_price / latest.eps

    pb_ratio = None
    if market_price and latest.book_value_per_share and latest.book_value_per_share > 0:
        pb_ratio = market_price / latest.book_value_per_share

    current_ratio = None
    if latest.current_assets and latest.current_liabilities and latest.current_liabilities > 0:
        current_ratio = latest.current_assets / latest.current_liabilities

    debt_to_equity = None
    if latest.total_debt is not None and latest.total_equity and latest.total_equity > 0:
        debt_to_equity = latest.total_debt / latest.total_equity

    dividend_yield = None
    if latest.dividends_per_share and market_price and market_price > 0:
        dividend_yield = (abs(latest.dividends_per_share) / market_price) * 100

    # Best estimate of intrinsic value (average of available models)
    intrinsic_values = [v for v in [graham_number, graham_formula, dcf] if v and v > 0]
    best_intrinsic = (
        sum(intrinsic_values) / Decimal(str(len(intrinsic_values)))
        if intrinsic_values
        else None
    )
    mos = calculate_margin_of_safety(best_intrinsic, market_price)
    stability = calculate_earnings_stability(eps_history)

    result = ValuationResult(
        graham_number=graham_number,
        graham_formula_value=graham_formula,
        ncav_per_share=ncav,
        dcf_value=dcf,
        pe_ratio=pe_ratio,
        pb_ratio=pb_ratio,
        current_ratio=current_ratio,
        debt_to_equity=debt_to_equity,
        dividend_yield=dividend_yield,
        margin_of_safety_pct=mos,
        earnings_stability=stability,
    )

    result.composite_score = calculate_composite_score(result, market_price)
    return result


async def run_screening(db: AsyncSession, profile: ScreeningProfile) -> list[ScreeningResult]:
    """Run a screening profile against all matching stocks."""
    # Build stock query based on profile filters
    query = select(Stock).where(Stock.is_active == True)  # noqa: E712

    if profile.exchanges:
        query = query.where(Stock.exchange.in_(profile.exchanges))
    if profile.sectors:
        query = query.where(Stock.sector.in_(profile.sectors))
    if profile.countries:
        query = query.where(Stock.country.in_(profile.countries))
    if profile.included_tickers:
        query = query.where(Stock.ticker.in_(profile.included_tickers))
    if profile.excluded_tickers:
        query = query.where(Stock.ticker.notin_(profile.excluded_tickers))

    stocks_result = await db.execute(query)
    stocks = stocks_result.scalars().all()

    criteria = GrahamCriteria.from_dict(profile.criteria or {})
    results: list[ScreeningResult] = []
    now = datetime.now(timezone.utc)

    for stock in stocks:
        valuation = await calculate_stock_valuation(db, stock)
        if valuation is None:
            continue

        # Save valuation snapshot
        snapshot = ValuationSnapshot(
            stock_id=stock.id,
            market_price=valuation.pe_ratio,  # Will fix below
            graham_number=valuation.graham_number,
            graham_formula_value=valuation.graham_formula_value,
            ncav_per_share=valuation.ncav_per_share,
            dcf_value=valuation.dcf_value,
            pe_ratio=valuation.pe_ratio,
            pb_ratio=valuation.pb_ratio,
            current_ratio=valuation.current_ratio,
            debt_to_equity=valuation.debt_to_equity,
            dividend_yield=valuation.dividend_yield,
            margin_of_safety_pct=valuation.margin_of_safety_pct,
            earnings_stability=valuation.earnings_stability,
            composite_score=valuation.composite_score,
        )

        # Get latest price for snapshot
        price_result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.stock_id == stock.id)
            .order_by(desc(PriceHistory.date))
            .limit(1)
        )
        latest_price_row = price_result.scalar_one_or_none()
        snapshot.market_price = latest_price_row.close if latest_price_row else None

        db.add(snapshot)

        # Count positive earnings years and dividend years from statements
        stmts_result = await db.execute(
            select(FinancialStatement)
            .where(
                FinancialStatement.stock_id == stock.id,
                FinancialStatement.period_type == "annual",
            )
            .order_by(desc(FinancialStatement.period_end))
            .limit(10)
        )
        stmts = list(stmts_result.scalars().all())

        positive_years = sum(1 for s in stmts if s.eps and s.eps > 0)
        dividend_years = sum(1 for s in stmts if s.dividends_per_share and s.dividends_per_share != 0)

        # Calculate avg earnings growth
        avg_growth = None
        if len(stmts) >= 2 and stmts[-1].eps and stmts[0].eps and stmts[-1].eps > 0:
            years = len(stmts) - 1
            avg_growth = (
                (stmts[0].eps / stmts[-1].eps) ** (Decimal("1") / Decimal(str(years))) - 1
            ) * 100

        # Evaluate criteria
        criterion_results = evaluate_criteria(
            valuation, criteria, positive_years, dividend_years, avg_growth
        )
        passed = {cr.name: {"value": cr.actual_value, "threshold": cr.threshold} for cr in criterion_results if cr.passed}
        failed = {cr.name: {"value": cr.actual_value, "threshold": cr.threshold} for cr in criterion_results if not cr.passed}

        # Determine recommendation
        pass_rate = len(passed) / len(criterion_results) if criterion_results else 0
        if pass_rate >= 0.8:
            recommendation = "strong_buy"
        elif pass_rate >= 0.6:
            recommendation = "buy"
        elif pass_rate >= 0.4:
            recommendation = "hold"
        else:
            recommendation = "avoid"

        screening_result = ScreeningResult(
            profile_id=profile.id,
            stock_id=stock.id,
            run_at=now,
            passed_criteria=passed,
            failed_criteria=failed,
            composite_score=valuation.composite_score,
            margin_of_safety_pct=valuation.margin_of_safety_pct,
            recommendation=recommendation,
        )
        db.add(screening_result)
        results.append(screening_result)

    profile.last_run_at = now
    await db.flush()

    logger.info(f"Screening '{profile.name}' completed: {len(results)} stocks evaluated")
    return results
