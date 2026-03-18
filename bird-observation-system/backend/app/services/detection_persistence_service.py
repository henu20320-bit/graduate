from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models import DetectionRecord
from app.schemas.inference import DetectionResult
from app.services.alert_service import AlertService
from app.services.system_log_service import SystemLogService


class DetectionPersistenceService:
    def __init__(self, alert_service: AlertService) -> None:
        self.alert_service = alert_service
        self.logger = get_logger(self.__class__.__name__)

    def save_detection_result(self, db: Session, result: DetectionResult, location: str | None = None) -> DetectionResult:
        capture_time = datetime.utcnow()
        alerts = []
        try:
            for detection in result.detections:
                species = self.alert_service.match_species(db, detection.class_name)
                if species is not None:
                    detection.species_id = species.id
                    detection.species_name = species.chinese_name or species.english_name or species.scientific_name
                    detection.is_rare = species.is_rare

                record = DetectionRecord(
                    source_type=result.source_type,
                    source_file=result.source_name,
                    species_id=species.id if species is not None else None,
                    confidence=detection.confidence,
                    bbox_x1=detection.bbox[0],
                    bbox_y1=detection.bbox[1],
                    bbox_x2=detection.bbox[2],
                    bbox_y2=detection.bbox[3],
                    capture_time=capture_time,
                    location=location,
                    is_alert=False,
                    alert_level='none',
                    result_image_path=result.result_path,
                )
                db.add(record)
                db.flush()

                popup = self.alert_service.process_detection_record(db, record, species)
                detection.alert_level = record.alert_level
                if popup is not None:
                    alerts.append(popup)

            result.alerts = alerts
            db.commit()
            SystemLogService.write_log(
                db,
                module='detection',
                action='save_detection_result',
                status='success',
                message=f'Saved {len(result.detections)} detection records and {len(alerts)} alerts.',
            )
            return result
        except Exception as exc:
            db.rollback()
            self.logger.exception('Failed to persist detection result.')
            try:
                SystemLogService.write_log(
                    db,
                    module='detection',
                    action='save_detection_result',
                    status='failed',
                    message=str(exc),
                )
            except Exception:
                self.logger.exception('Failed to write system log after persistence error.')
            raise RuntimeError(f'Failed to persist detection result: {exc}') from exc
