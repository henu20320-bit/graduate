from functools import lru_cache

from app.services.alert_service import AlertService
from app.services.bird_detection_service import BirdDetectionService
from app.services.detection_persistence_service import DetectionPersistenceService


@lru_cache
def get_bird_detection_service() -> BirdDetectionService:
    return BirdDetectionService()


@lru_cache
def get_alert_service() -> AlertService:
    return AlertService()


@lru_cache
def get_detection_persistence_service() -> DetectionPersistenceService:
    return DetectionPersistenceService(alert_service=get_alert_service())
