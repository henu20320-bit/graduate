from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import Base, engine
from app.models import AlertRecord, BirdSpecies, DetectionRecord, SystemLog  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print('Database tables initialized successfully.')


if __name__ == '__main__':
    main()
