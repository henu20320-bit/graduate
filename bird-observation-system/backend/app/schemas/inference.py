from app.schemas.common import ORMBaseSchema


class DetectionBox(ORMBaseSchema):
    class_id: int
    class_name: str
    confidence: float
    bbox: list[float]
    is_rare: bool = False
    alert_level: str = 'none'


class DetectionResult(ORMBaseSchema):
    source_type: str
    source_name: str
    detections: list[DetectionBox]
    inference_time_ms: float
    result_path: str
