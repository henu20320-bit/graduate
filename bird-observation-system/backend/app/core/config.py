from functools import lru_cache
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    project_name: str = 'Bird Observation System'
    project_version: str = '0.1.0'
    api_v1_prefix: str = '/api'
    debug: bool = True

    database_url: str = f"sqlite:///{(BASE_DIR / 'bird_observation.db').as_posix()}"
    mysql_database_url: str | None = None

    uploads_dir: Path = BASE_DIR / 'uploads'
    outputs_dir: Path = BASE_DIR / 'outputs'
    weights_dir: Path = BASE_DIR / 'weights'
    log_level: str = 'INFO'

    yolo_default_weight: str = 'yolov8n.pt'
    image_result_suffix: str = '_result'
    video_result_suffix: str = '_result'
    camera_result_name: str = 'camera_latest.jpg'
    camera_index: int = 0
    camera_frame_interval: int = 5

    rare_confidence_threshold: float = 0.7
    medium_confidence_threshold: float = 0.6
    sustained_occurrence_minutes: int = 30
    sustained_occurrence_threshold: int = 3

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
    )

    @computed_field
    @property
    def effective_database_url(self) -> str:
        if self.mysql_database_url:
            return self.mysql_database_url

        database_url = self.database_url
        sqlite_prefix = 'sqlite:///'
        if database_url.startswith(sqlite_prefix):
            sqlite_path = database_url[len(sqlite_prefix) :]
            if sqlite_path.startswith('./'):
                return f"sqlite:///{(BASE_DIR / sqlite_path[2:]).as_posix()}"
        return database_url

    @computed_field
    @property
    def default_weight_path(self) -> Path:
        return self.weights_dir / self.yolo_default_weight


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    settings.weights_dir.mkdir(parents=True, exist_ok=True)
    return settings
