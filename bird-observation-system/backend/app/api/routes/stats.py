from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.common import ApiResponse
from app.schemas.stats import CategoryChartData, MigrationTrendData, OverviewStats, RareBirdStats, TrendChartData
from app.services.stats_service import StatsService
from app.utils.response import success_response

router = APIRouter()


def get_stats_service() -> StatsService:
    return StatsService()


@router.get('/overview', response_model=ApiResponse[OverviewStats])
def get_overview_stats(
    db: Session = Depends(get_db),
    service: StatsService = Depends(get_stats_service),
) -> ApiResponse[OverviewStats]:
    return success_response(service.get_overview_stats(db))


@router.get('/species-frequency', response_model=ApiResponse[CategoryChartData])
def get_species_frequency(
    days: int = Query(7, description='Only supports 7 or 30 days.'),
    db: Session = Depends(get_db),
    service: StatsService = Depends(get_stats_service),
) -> ApiResponse[CategoryChartData]:
    return success_response(service.get_species_frequency(db, days=days))


@router.get('/daily-trend', response_model=ApiResponse[TrendChartData])
def get_daily_trend(
    days: int = Query(7, description='Only supports 7 or 30 days.'),
    db: Session = Depends(get_db),
    service: StatsService = Depends(get_stats_service),
) -> ApiResponse[TrendChartData]:
    return success_response(service.get_daily_trend(db, days=days))


@router.get('/rare-birds', response_model=ApiResponse[RareBirdStats])
def get_rare_birds_stats(
    days: int = Query(7, description='Only supports 7 or 30 days.'),
    db: Session = Depends(get_db),
    service: StatsService = Depends(get_stats_service),
) -> ApiResponse[RareBirdStats]:
    return success_response(service.get_rare_bird_stats(db, days=days))


@router.get('/migration-trend', response_model=ApiResponse[MigrationTrendData])
def get_migration_trend(
    days: int = Query(7, description='Only supports 7 or 30 days.'),
    db: Session = Depends(get_db),
    service: StatsService = Depends(get_stats_service),
) -> ApiResponse[MigrationTrendData]:
    return success_response(service.get_migration_trend(db, days=days))
