from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AlertRecord(Base):
    __tablename__ = 'alert_records'
    __table_args__ = (
        Index('ix_alert_records_alert_level', 'alert_level'),
        Index('ix_alert_records_handled_status', 'handled_status'),
        Index('ix_alert_records_created_at', 'created_at'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    detection_record_id: Mapped[int] = mapped_column(ForeignKey('detection_records.id'), nullable=False)
    species_id: Mapped[int | None] = mapped_column(ForeignKey('bird_species.id'), nullable=True)
    alert_level: Mapped[str] = mapped_column(String(20), nullable=False)
    alert_message: Mapped[str] = mapped_column(Text, nullable=False)
    handled_status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending', server_default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    detection_record = relationship('DetectionRecord', back_populates='alert_records')
    species = relationship('BirdSpecies', back_populates='alert_records')
