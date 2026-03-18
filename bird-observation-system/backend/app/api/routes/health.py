from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.utils.response import success_response

router = APIRouter()


@router.get('/health', response_model=ApiResponse[dict])
def health_check() -> ApiResponse[dict]:
    return success_response({'status': 'ok'}, message='Bird observation backend is running.')
