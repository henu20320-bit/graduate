from datetime import datetime

from app.schemas.bird_species import BirdSpeciesRead
from app.schemas.common import ORMBaseSchema


class AlertPopup(ORMBaseSchema):
    alert_id: int | None = None
    detection_record_id: int | None = None
    species_id: int | None = None
    species_name: str
    alert_level: str
    title: str
    message: str
    confidence: float
    detected_at: datetime
    result_path: str | None = None
    handled_status: str = 'pending'
    sustained_occurrence: bool = False
    recent_alert_count: int = 0


class AlertRecordRead(ORMBaseSchema):
    id: int
    detection_record_id: int
    species_id: int | None = None
    alert_level: str
    alert_message: str
    handled_status: str
    created_at: datetime
    sustained_occurrence: bool = False
    recent_alert_count: int = 0
    species: BirdSpeciesRead | None = None
