from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models import AlertRecord, BirdSpecies, DetectionRecord
from app.schemas.alert_record import AlertPopup
from app.schemas.stats import CategoryChartData, ChartSeriesItem, MigrationTrendData, OverviewStats, RareBirdStats, TrendChartData


class StatsService:
    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

    def _resolve_days(self, days: int | None) -> int:
        if days in {7, 30}:
            return days
        return 7

    def _date_range(self, days: int) -> tuple[datetime, datetime]:
        end = datetime.utcnow()
        start = end - timedelta(days=days - 1)
        return start.replace(hour=0, minute=0, second=0, microsecond=0), end

    def get_overview_stats(self, db: Session) -> OverviewStats:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        total = db.scalar(select(func.count(DetectionRecord.id))) or 0
        today = db.scalar(select(func.count(DetectionRecord.id)).where(DetectionRecord.capture_time >= today_start)) or 0
        rare = (
            db.scalar(
                select(func.count(DetectionRecord.id))
                .join(BirdSpecies, DetectionRecord.species_id == BirdSpecies.id)
                .where(BirdSpecies.is_rare.is_(True))
            )
            or 0
        )
        alerts = db.scalar(select(func.count(AlertRecord.id))) or 0
        return OverviewStats(
            totalDetections=int(total),
            todayDetections=int(today),
            rareBirdDetections=int(rare),
            alertCount=int(alerts),
        )

    def get_species_frequency(self, db: Session, days: int | None = None) -> CategoryChartData:
        resolved_days = self._resolve_days(days)
        start, end = self._date_range(resolved_days)
        statement = (
            select(
                func.coalesce(BirdSpecies.chinese_name, BirdSpecies.english_name, 'Unknown').label('species_name'),
                func.count(DetectionRecord.id).label('count'),
            )
            .join(BirdSpecies, DetectionRecord.species_id == BirdSpecies.id, isouter=True)
            .where(DetectionRecord.capture_time >= start, DetectionRecord.capture_time <= end)
            .group_by(BirdSpecies.chinese_name, BirdSpecies.english_name)
            .order_by(func.count(DetectionRecord.id).desc())
        )
        rows = db.execute(statement).all()
        categories = [str(row.species_name or 'Unknown') for row in rows]
        values = [int(row.count) for row in rows]
        return CategoryChartData(
            categories=categories,
            series=[{'name': f'{resolved_days}天检测频次', 'type': 'bar', 'data': values}],
        )

    def get_daily_trend(self, db: Session, days: int | None = None) -> TrendChartData:
        resolved_days = self._resolve_days(days)
        start, end = self._date_range(resolved_days)
        statement = (
            select(func.date(DetectionRecord.capture_time).label('date'), func.count(DetectionRecord.id).label('count'))
            .where(DetectionRecord.capture_time >= start, DetectionRecord.capture_time <= end)
            .group_by(func.date(DetectionRecord.capture_time))
            .order_by(func.date(DetectionRecord.capture_time))
        )
        rows = db.execute(statement).all()
        count_map = {str(row.date): int(row.count) for row in rows}
        dates = [(start + timedelta(days=index)).strftime('%Y-%m-%d') for index in range(resolved_days)]
        values = [count_map.get(item, 0) for item in dates]
        return TrendChartData(
            dates=dates,
            series=[{'name': '检测趋势', 'type': 'line', 'smooth': True, 'data': values}],
        )

    def get_rare_bird_stats(self, db: Session, days: int | None = None) -> RareBirdStats:
        resolved_days = self._resolve_days(days)
        start, end = self._date_range(resolved_days)
        total_rare = (
            db.scalar(
                select(func.count(AlertRecord.id))
                .join(BirdSpecies, AlertRecord.species_id == BirdSpecies.id)
                .where(
                    AlertRecord.created_at >= start,
                    AlertRecord.created_at <= end,
                    BirdSpecies.is_rare.is_(True),
                )
            )
            or 0
        )
        high = (
            db.scalar(
                select(func.count(AlertRecord.id)).where(
                    AlertRecord.created_at >= start,
                    AlertRecord.created_at <= end,
                    AlertRecord.alert_level == 'high',
                )
            )
            or 0
        )
        medium = (
            db.scalar(
                select(func.count(AlertRecord.id)).where(
                    AlertRecord.created_at >= start,
                    AlertRecord.created_at <= end,
                    AlertRecord.alert_level == 'medium',
                )
            )
            or 0
        )
        distribution_rows = db.execute(
            select(
                func.coalesce(BirdSpecies.chinese_name, BirdSpecies.english_name, 'Unknown').label('species_name'),
                func.count(AlertRecord.id).label('count'),
            )
            .join(BirdSpecies, AlertRecord.species_id == BirdSpecies.id)
            .where(AlertRecord.created_at >= start, AlertRecord.created_at <= end)
            .group_by(BirdSpecies.chinese_name, BirdSpecies.english_name)
            .order_by(func.count(AlertRecord.id).desc())
        ).all()
        distribution = [ChartSeriesItem(name=str(row.species_name), value=int(row.count)) for row in distribution_rows]
        return RareBirdStats(
            totalRareAlerts=int(total_rare),
            highAlerts=int(high),
            mediumAlerts=int(medium),
            speciesDistribution=distribution,
        )

    def get_migration_trend(self, db: Session, days: int | None = None) -> MigrationTrendData:
        resolved_days = self._resolve_days(days)
        start, end = self._date_range(resolved_days)
        statement = (
            select(
                func.date(DetectionRecord.capture_time).label('date'),
                func.coalesce(BirdSpecies.chinese_name, BirdSpecies.english_name, 'Unknown').label('species_name'),
                func.count(DetectionRecord.id).label('count'),
            )
            .join(BirdSpecies, DetectionRecord.species_id == BirdSpecies.id, isouter=True)
            .where(DetectionRecord.capture_time >= start, DetectionRecord.capture_time <= end)
            .group_by(func.date(DetectionRecord.capture_time), BirdSpecies.chinese_name, BirdSpecies.english_name)
            .order_by(func.date(DetectionRecord.capture_time), func.count(DetectionRecord.id).desc())
        )
        rows = db.execute(statement).all()

        dates = [(start + timedelta(days=index)).strftime('%Y-%m-%d') for index in range(resolved_days)]
        species_totals: dict[str, int] = defaultdict(int)
        matrix: dict[str, dict[str, int]] = defaultdict(dict)
        for row in rows:
            species_name = str(row.species_name or 'Unknown')
            date_key = str(row.date)
            count = int(row.count)
            species_totals[species_name] += count
            matrix[species_name][date_key] = count

        legend = [item[0] for item in sorted(species_totals.items(), key=lambda x: x[1], reverse=True)[:5]]
        series = []
        for species_name in legend:
            series.append(
                {
                    'name': species_name,
                    'type': 'line',
                    'smooth': True,
                    'data': [matrix[species_name].get(date, 0) for date in dates],
                }
            )
        return MigrationTrendData(dates=dates, legend=legend, series=series)

    def get_latest_alert_popup(self, db: Session) -> AlertPopup | None:
        statement = (
            select(AlertRecord)
            .join(DetectionRecord, AlertRecord.detection_record_id == DetectionRecord.id)
            .join(BirdSpecies, AlertRecord.species_id == BirdSpecies.id, isouter=True)
            .order_by(AlertRecord.created_at.desc())
            .limit(1)
        )
        alert = db.scalar(statement)
        if alert is None or alert.detection_record is None:
            return None
        species = alert.species
        species_name = '未知鸟类'
        if species is not None:
            species_name = species.chinese_name or species.english_name or species.scientific_name or species_name
        return AlertPopup(
            alert_id=alert.id,
            detection_record_id=alert.detection_record_id,
            species_id=alert.species_id,
            species_name=species_name,
            alert_level=alert.alert_level,
            title='珍稀鸟类预警' if alert.alert_level == 'high' else '鸟类关注预警',
            message=alert.alert_message,
            confidence=alert.detection_record.confidence,
            detected_at=alert.detection_record.capture_time,
            result_path=alert.detection_record.result_image_path,
            handled_status=alert.handled_status,
        )
