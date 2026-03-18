from app.schemas.common import ORMBaseSchema


class OverviewStats(ORMBaseSchema):
    totalDetections: int
    todayDetections: int
    rareBirdDetections: int
    alertCount: int


class ChartSeriesItem(ORMBaseSchema):
    name: str
    value: int | float


class CategoryChartData(ORMBaseSchema):
    categories: list[str]
    series: list[dict]


class TrendPoint(ORMBaseSchema):
    date: str
    value: int


class TrendChartData(ORMBaseSchema):
    dates: list[str]
    series: list[dict]


class RareBirdStats(ORMBaseSchema):
    totalRareAlerts: int
    highAlerts: int
    mediumAlerts: int
    speciesDistribution: list[ChartSeriesItem]


class MigrationTrendPoint(ORMBaseSchema):
    date: str
    species: str
    count: int


class MigrationTrendData(ORMBaseSchema):
    dates: list[str]
    legend: list[str]
    series: list[dict]
