from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import inspect, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import engine


def main() -> None:
    inspector = inspect(engine)
    columns = {column['name'] for column in inspector.get_columns('bird_species')}
    with engine.begin() as connection:
        if 'model_class_name' not in columns:
            connection.execute(text('ALTER TABLE bird_species ADD COLUMN model_class_name VARCHAR(100)'))
            print('Added column: bird_species.model_class_name')
        connection.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_bird_species_model_class_name ON bird_species (model_class_name)'))
        print('Ensured index: ix_bird_species_model_class_name')


if __name__ == '__main__':
    main()
