import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.database import get_db
from app.screening.models import ScreeningProfile, ScreeningResult
from app.screening.schemas import (
    ScreeningProfileCreate,
    ScreeningProfileResponse,
    ScreeningProfileUpdate,
    ScreeningResultResponse,
)
from app.screening.service import run_screening
from app.stocks.models import Stock

router = APIRouter(prefix="/api/screening", tags=["screening"])


@router.get("/profiles", response_model=list[ScreeningProfileResponse])
async def list_profiles(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ScreeningProfile)
        .where(ScreeningProfile.user_id == user.id)
        .order_by(ScreeningProfile.created_at)
    )
    return result.scalars().all()


@router.post("/profiles", response_model=ScreeningProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ScreeningProfileCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = ScreeningProfile(
        user_id=user.id,
        name=data.name,
        description=data.description,
        exchanges=data.exchanges,
        sectors=data.sectors,
        countries=data.countries,
        included_tickers=data.included_tickers,
        excluded_tickers=data.excluded_tickers,
        criteria=data.criteria,
        is_active=data.is_active,
        schedule=data.schedule,
    )
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


@router.put("/profiles/{profile_id}", response_model=ScreeningProfileResponse)
async def update_profile(
    profile_id: uuid.UUID,
    data: ScreeningProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ScreeningProfile).where(
            ScreeningProfile.id == profile_id,
            ScreeningProfile.user_id == user.id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.flush()
    await db.refresh(profile)
    return profile


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ScreeningProfile).where(
            ScreeningProfile.id == profile_id,
            ScreeningProfile.user_id == user.id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    await db.delete(profile)


@router.post("/profiles/{profile_id}/run", response_model=list[ScreeningResultResponse])
async def trigger_screening(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ScreeningProfile).where(
            ScreeningProfile.id == profile_id,
            ScreeningProfile.user_id == user.id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    results = await run_screening(db, profile)

    # Enrich with stock info
    response = []
    for r in results:
        stock_result = await db.execute(select(Stock).where(Stock.id == r.stock_id))
        stock = stock_result.scalar_one_or_none()
        resp = ScreeningResultResponse.model_validate(r)
        if stock:
            resp.stock_ticker = stock.ticker
            resp.stock_name = stock.name
        response.append(resp)

    return response


@router.get("/results/latest", response_model=list[ScreeningResultResponse])
async def get_latest_results(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Get results from profiles owned by this user
    result = await db.execute(
        select(ScreeningResult)
        .join(ScreeningProfile)
        .where(ScreeningProfile.user_id == user.id)
        .order_by(desc(ScreeningResult.run_at), desc(ScreeningResult.composite_score))
        .limit(limit)
    )
    screening_results = result.scalars().all()

    response = []
    for r in screening_results:
        stock_result = await db.execute(select(Stock).where(Stock.id == r.stock_id))
        stock = stock_result.scalar_one_or_none()
        resp = ScreeningResultResponse.model_validate(r)
        if stock:
            resp.stock_ticker = stock.ticker
            resp.stock_name = stock.name
        response.append(resp)

    return response
