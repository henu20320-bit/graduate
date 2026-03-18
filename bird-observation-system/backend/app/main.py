from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logger import configure_logging, get_logger
from app.models import AlertRecord, BirdSpecies, DetectionRecord, SystemLog  # noqa: F401

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info('Initializing database tables.')
    Base.metadata.create_all(bind=engine)
    yield
    logger.info('Shutting down Bird Observation backend.')


app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    debug=settings.debug,
    lifespan=lifespan,
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'Bird Observation System backend is running.'}
