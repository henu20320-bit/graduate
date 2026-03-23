from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BirdSpecies(Base):
    __tablename__ = 'bird_species'
    __table_args__ = (
        Index('ix_bird_species_chinese_name', 'chinese_name'),
        Index('ix_bird_species_model_class_name', 'model_class_name'),
        Index('ix_bird_species_is_rare', 'is_rare'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chinese_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    model_class_name: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    english_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scientific_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_rare: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='0')
    rare_level: Mapped[str] = mapped_column(String(20), nullable=False, default='none', server_default='none')
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    detection_records = relationship('DetectionRecord', back_populates='species')
    alert_records = relationship('AlertRecord', back_populates='species')
