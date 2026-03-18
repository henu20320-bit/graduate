from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models import AlertRecord
from app.schemas.alert_record import AlertPopup, AlertRecordRead
from app.schemas.common import ApiResponse, PaginatedResponse
from app.utils.response import success_response

router = APIRouter()


@router.get('', response_model=ApiResponse[PaginatedResponse[AlertRecordRead]])
def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse[PaginatedResponse[AlertRecordRead]]:
    total = db.query(AlertRecord).count()
    records = (
        db.query(AlertRecord)
        .options(joinedload(AlertRecord.species), joinedload(AlertRecord.detection_record))
        .order_by(AlertRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    payload = PaginatedResponse[AlertRecordRead](
        items=[AlertRecordRead.model_validate(record) for record in records],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.get('/latest', response_model=ApiResponse[AlertPopup | None])
def get_latest_alert(db: Session = Depends(get_db)) -> ApiResponse[AlertPopup | None]:
    statement = (
        select(AlertRecord)
        .options(joinedload(AlertRecord.species), joinedload(AlertRecord.detection_record))
        .order_by(AlertRecord.created_at.desc())
        .limit(1)
    )
    record = db.scalar(statement)
    if record is None or record.species is None or record.detection_record is None:
        return success_response(None, message='No alert record found.')

    popup = AlertPopup(
        alert_id=record.id,
        detection_record_id=record.detection_record_id,
        species_id=record.species_id,
        species_name=record.species.chinese_name or record.species.english_name or record.species.scientific_name or '未知鸟类',
        alert_level=record.alert_level,
        title='珍稀鸟类预警' if record.alert_level == 'high' else '鸟类关注预警',
        message=record.alert_message,
        confidence=record.detection_record.confidence,
        detected_at=record.detection_record.capture_time,
        result_path=record.detection_record.result_image_path,
        handled_status=record.handled_status,
    )
    return success_response(popup)


@router.get('/{alert_id}', response_model=ApiResponse[AlertRecordRead])
def get_alert(alert_id: int, db: Session = Depends(get_db)) -> ApiResponse[AlertRecordRead]:
    statement = (
        select(AlertRecord)
        .where(AlertRecord.id == alert_id)
        .options(joinedload(AlertRecord.species), joinedload(AlertRecord.detection_record))
    )
    record = db.scalar(statement)
    if record is None:
        raise HTTPException(status_code=404, detail='Alert record not found.')
    return success_response(AlertRecordRead.model_validate(record))
