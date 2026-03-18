from datetime import datetime

from app.schemas.bird_species import BirdSpeciesRead
from app.schemas.common import ORMBaseSchema


class AlertRecordRead(ORMBaseSchema):
    id: int
    detection_record_id: int
    species_id: int | None = None
    alert_level: str
    alert_message: str
    handled_status: str
    created_at: datetime
    species: BirdSpeciesRead | None = None
