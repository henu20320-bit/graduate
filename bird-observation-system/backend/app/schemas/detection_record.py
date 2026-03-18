from datetime import datetime

from pydantic import Field

from app.schemas.alert_record import AlertRecordRead
from app.schemas.bird_species import BirdSpeciesRead
from app.schemas.common import ORMBaseSchema


class DetectionRecordRead(ORMBaseSchema):
    id: int
    source_type: str
    source_file: str | None = None
    species_id: int | None = None
    confidence: float
    bbox_x1: float
    bbox_y1: float
    bbox_x2: float
    bbox_y2: float
    capture_time: datetime
    location: str | None = None
    is_alert: bool
    alert_level: str
    result_image_path: str | None = None
    created_at: datetime
    species: BirdSpeciesRead | None = None
    alert_records: list[AlertRecordRead] = Field(default_factory=list)
