from datetime import datetime

from app.schemas.common import ORMBaseSchema


class BirdSpeciesBase(ORMBaseSchema):
    chinese_name: str
    english_name: str | None = None
    scientific_name: str | None = None
    category: str | None = None
    is_rare: bool = False
    rare_level: str = 'none'
    description: str | None = None
    image_url: str | None = None


class BirdSpeciesRead(BirdSpeciesBase):
    id: int
    created_at: datetime
    updated_at: datetime
