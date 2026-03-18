from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.common import ApiResponse
from app.schemas.inference import DetectionResult
from app.services import get_bird_detection_service, get_detection_persistence_service
from app.services.bird_detection_service import BirdDetectionService
from app.services.detection_persistence_service import DetectionPersistenceService
from app.utils.media import save_upload_file
from app.utils.response import success_response

router = APIRouter()
settings = get_settings()


@router.post('/image', response_model=ApiResponse[DetectionResult])
async def detect_image(
    file: UploadFile = File(...),
    weight_path: str | None = None,
    service: BirdDetectionService = Depends(get_bird_detection_service),
    persistence_service: DetectionPersistenceService = Depends(get_detection_persistence_service),
    db: Session = Depends(get_db),
) -> ApiResponse[DetectionResult]:
    try:
        image_path, original_name = await save_upload_file(file, settings.uploads_dir)
        result = service.detect_image(image_path=image_path, weight_path=weight_path, source_name=original_name)
        result = persistence_service.save_detection_result(db, result)
        return success_response(result, message='Image detection completed successfully.')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post('/video', response_model=ApiResponse[DetectionResult])
async def detect_video(
    file: UploadFile = File(...),
    weight_path: str | None = None,
    service: BirdDetectionService = Depends(get_bird_detection_service),
    persistence_service: DetectionPersistenceService = Depends(get_detection_persistence_service),
    db: Session = Depends(get_db),
) -> ApiResponse[DetectionResult]:
    try:
        video_path, original_name = await save_upload_file(file, settings.uploads_dir)
        result = service.detect_video(video_path=video_path, weight_path=weight_path, source_name=original_name)
        result = persistence_service.save_detection_result(db, result)
        return success_response(result, message='Video detection completed successfully.')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get('/camera/start', response_model=ApiResponse[dict])
def start_camera_detection(
    camera_index: int = Query(settings.camera_index, ge=0),
    weight_path: str | None = None,
    service: BirdDetectionService = Depends(get_bird_detection_service),
) -> ApiResponse[dict]:
    try:
        payload = service.start_camera_detection(camera_index=camera_index, weight_path=weight_path)
        return success_response(payload, message='Camera detection started.')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get('/camera/stop', response_model=ApiResponse[dict])
def stop_camera_detection(
    service: BirdDetectionService = Depends(get_bird_detection_service),
) -> ApiResponse[dict]:
    try:
        payload = service.stop_camera_detection()
        return success_response(payload, message='Camera detection stopped.')
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get('/camera/stream', response_model=ApiResponse[DetectionResult | dict | None])
def stream_camera_result(
    service: BirdDetectionService = Depends(get_bird_detection_service),
) -> ApiResponse[DetectionResult | dict | None]:
    result = service.get_latest_camera_result()
    if result is not None:
        return success_response(result, message='Latest camera detection fetched successfully.')
    return success_response(service.get_camera_status(), message='Camera has not produced any detection result yet.')
