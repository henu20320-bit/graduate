from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DetectionRecord(Base):
    __tablename__ = 'detection_records'
    __table_args__ = (
        Index('ix_detection_records_capture_time', 'capture_time'),
        Index('ix_detection_records_source_type', 'source_type'),
        Index('ix_detection_records_species_id', 'species_id'),
        Index('ix_detection_records_alert_level', 'alert_level'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    species_id: Mapped[int | None] = mapped_column(ForeignKey('bird_species.id'), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_x1: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y1: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_x2: Mapped[float] = mapped_column(Float, nullable=False)
    bbox_y2: Mapped[float] = mapped_column(Float, nullable=False)
    capture_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_alert: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='0')
    alert_level: Mapped[str] = mapped_column(String(20), nullable=False, default='none', server_default='none')
    result_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    species = relationship('BirdSpecies', back_populates='detection_records')
    alert_records = relationship('AlertRecord', back_populates='detection_record', cascade='all, delete-orphan')
