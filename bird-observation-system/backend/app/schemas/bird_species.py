from datetime import datetime

from app.schemas.common import ORMBaseSchema


class BirdSpeciesBase(ORMBaseSchema):
    chinese_name: str
    model_class_name: str | None = None
    english_name: str | None = None
    scientific_name: str | None = None
    category: str | None = None
    iucn_status: str = 'unknown'
    china_protection_type: str = 'none'
    attention_level: str = 'none'
    is_rare: bool = False
    rare_level: str = 'none'
    description: str | None = None
    image_url: str | None = None


class BirdSpeciesRead(BirdSpeciesBase):
    id: int
    created_at: datetime
    updated_at: datetime
