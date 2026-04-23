from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logger import configure_logging, get_logger
from app.core.schema_migration import ensure_bird_species_columns
from app.models import AlertRecord, BirdSpecies, DetectionRecord, SystemLog  # noqa: F401

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info('Initializing database tables.')
    Base.metadata.create_all(bind=engine)
    ensure_bird_species_columns()
    yield
    logger.info('Shutting down Bird Observation backend.')


app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    debug=settings.debug,
    lifespan=lifespan,
)
app.include_router(api_router, prefix=settings.api_v1_prefix)
app.mount('/outputs', StaticFiles(directory=settings.outputs_dir), name='outputs')
app.mount('/uploads', StaticFiles(directory=settings.uploads_dir), name='uploads')


@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'Bird Observation System backend is running.'}