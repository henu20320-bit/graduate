from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logger import get_logger
from app.models import AlertRecord, BirdSpecies, DetectionRecord
from app.schemas.alert_record import AlertPopup


class AlertService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = get_logger(self.__class__.__name__)

    def match_species(self, db: Session, class_name: str) -> BirdSpecies | None:
        normalized_name = class_name.strip().lower()
        if not normalized_name:
            return None

        statement = select(BirdSpecies).where(
            or_(
                func.lower(BirdSpecies.model_class_name) == normalized_name,
                func.lower(BirdSpecies.chinese_name) == normalized_name,
                func.lower(BirdSpecies.english_name) == normalized_name,
                func.lower(BirdSpecies.scientific_name) == normalized_name,
            )
        )
        return db.scalar(statement)

    def evaluate_alert_level(self, species: BirdSpecies | None, confidence: float, recent_alert_count: int = 0) -> str:
        if species is None or not species.is_rare:
            return 'none'

        if confidence < self.settings.medium_confidence_threshold:
            return 'none'

        if confidence < self.settings.rare_confidence_threshold:
            return 'medium' if species.rare_level in {'high', 'medium'} else 'none'

        level = 'high' if species.rare_level == 'high' else 'medium'
        if recent_alert_count >= self.settings.sustained_occurrence_threshold:
            level = 'high'
        return level

    def count_recent_alerts(self, db: Session, species_id: int, capture_time: datetime) -> int:
        window_start = capture_time - timedelta(minutes=self.settings.sustained_occurrence_minutes)
        statement = select(func.count(DetectionRecord.id)).where(
            DetectionRecord.species_id == species_id,
            DetectionRecord.is_alert.is_(True),
            DetectionRecord.capture_time >= window_start,
            DetectionRecord.capture_time <= capture_time,
        )
        count = db.scalar(statement)
        return int(count or 0)

    def build_alert_message(self, species: BirdSpecies, confidence: float, alert_level: str, recent_alert_count: int) -> str:
        species_name = species.chinese_name or species.english_name or species.scientific_name or '未知鸟类'
        if recent_alert_count >= self.settings.sustained_occurrence_threshold:
            return f'{species_name} 在短时间内持续出现，当前置信度 {confidence:.2f}，请立即关注现场情况。'
        if alert_level == 'high':
            return f'检测到珍稀保护鸟类 {species_name}，当前置信度 {confidence:.2f}，请及时核查并记录。'
        return f'检测到重点关注鸟类 {species_name}，当前置信度 {confidence:.2f}，建议持续观察。'

    def create_alert_record(
        self,
        db: Session,
        detection_record: DetectionRecord,
        species: BirdSpecies,
        alert_level: str,
        alert_message: str,
    ) -> AlertRecord:
        alert = AlertRecord(
            detection_record_id=detection_record.id,
            species_id=species.id,
            alert_level=alert_level,
            alert_message=alert_message,
            handled_status='pending',
        )
        db.add(alert)
        db.flush()
        return alert

    def build_popup_payload(
        self,
        alert_record: AlertRecord,
        detection_record: DetectionRecord,
        species: BirdSpecies,
    ) -> AlertPopup:
        return AlertPopup(
            alert_id=alert_record.id,
            detection_record_id=detection_record.id,
            species_id=species.id,
            species_name=species.chinese_name or species.english_name or species.scientific_name or '未知鸟类',
            alert_level=alert_record.alert_level,
            title='珍稀鸟类预警' if alert_record.alert_level == 'high' else '鸟类关注预警',
            message=alert_record.alert_message,
            confidence=detection_record.confidence,
            detected_at=detection_record.capture_time,
            result_path=detection_record.result_image_path,
            handled_status=alert_record.handled_status,
        )

    def send_sms_notification(self, popup: AlertPopup) -> None:
        self.logger.info('SMS notification hook reserved for alert %s', popup.alert_id)

    def send_email_notification(self, popup: AlertPopup) -> None:
        self.logger.info('Email notification hook reserved for alert %s', popup.alert_id)

    def process_detection_record(
        self,
        db: Session,
        detection_record: DetectionRecord,
        species: BirdSpecies | None,
    ) -> AlertPopup | None:
        if species is None:
            detection_record.is_alert = False
            detection_record.alert_level = 'none'
            return None

        recent_alert_count = self.count_recent_alerts(db, species.id, detection_record.capture_time)
        alert_level = self.evaluate_alert_level(species, detection_record.confidence, recent_alert_count)
        detection_record.is_alert = alert_level != 'none'
        detection_record.alert_level = alert_level
        detection_record.species_id = species.id

        if alert_level == 'none':
            return None

        alert_message = self.build_alert_message(species, detection_record.confidence, alert_level, recent_alert_count)
        alert_record = self.create_alert_record(db, detection_record, species, alert_level, alert_message)
        popup = self.build_popup_payload(alert_record, detection_record, species)
        self.send_sms_notification(popup)
        self.send_email_notification(popup)
        return popup
