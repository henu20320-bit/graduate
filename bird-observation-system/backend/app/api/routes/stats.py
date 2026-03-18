from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.utils.response import success_response

router = APIRouter()


@router.get('/overview', response_model=ApiResponse[dict])
def get_overview_stats() -> ApiResponse[dict]:
    return success_response(
        {
            'totalDetections': 0,
            'todayDetections': 0,
            'rareBirdDetections': 0,
            'alertCount': 0,
        },
        message='Statistics skeleton is ready for phase 4.',
    )


@router.get('/species-frequency', response_model=ApiResponse[list[dict]])
def get_species_frequency() -> ApiResponse[list[dict]]:
    return success_response([], message='Species frequency endpoint reserved for phase 4.')


@router.get('/daily-trend', response_model=ApiResponse[list[dict]])
def get_daily_trend() -> ApiResponse[list[dict]]:
    return success_response([], message='Daily trend endpoint reserved for phase 4.')


@router.get('/rare-birds', response_model=ApiResponse[list[dict]])
def get_rare_birds_stats() -> ApiResponse[list[dict]]:
    return success_response([], message='Rare birds statistics endpoint reserved for phase 4.')


@router.get('/migration-trend', response_model=ApiResponse[list[dict]])
def get_migration_trend() -> ApiResponse[list[dict]]:
    return success_response([], message='Migration trend endpoint reserved for phase 4.')
