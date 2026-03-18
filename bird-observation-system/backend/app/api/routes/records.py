from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models import DetectionRecord
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.detection_record import DetectionRecordRead
from app.utils.response import success_response

router = APIRouter()


@router.get('', response_model=ApiResponse[PaginatedResponse[DetectionRecordRead]])
def list_detection_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse[PaginatedResponse[DetectionRecordRead]]:
    total = db.query(DetectionRecord).count()
    records = (
        db.query(DetectionRecord)
        .options(joinedload(DetectionRecord.species), joinedload(DetectionRecord.alert_records))
        .order_by(DetectionRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    payload = PaginatedResponse[DetectionRecordRead](
        items=[DetectionRecordRead.model_validate(record) for record in records],
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(payload)


@router.get('/{record_id}', response_model=ApiResponse[DetectionRecordRead])
def get_detection_record(record_id: int, db: Session = Depends(get_db)) -> ApiResponse[DetectionRecordRead]:
    statement = (
        select(DetectionRecord)
        .where(DetectionRecord.id == record_id)
        .options(joinedload(DetectionRecord.species), joinedload(DetectionRecord.alert_records))
    )
    record = db.scalar(statement)
    if record is None:
        raise HTTPException(status_code=404, detail='Detection record not found.')
    return success_response(DetectionRecordRead.model_validate(record))
