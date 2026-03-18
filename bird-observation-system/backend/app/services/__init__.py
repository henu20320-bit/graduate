from functools import lru_cache

from app.services.bird_detection_service import BirdDetectionService


@lru_cache
def get_bird_detection_service() -> BirdDetectionService:
    return BirdDetectionService()
