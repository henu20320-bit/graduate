from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError

from app.core.database import engine


def ensure_bird_species_columns() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if 'bird_species' not in table_names:
        return

    columns = {column['name'] for column in inspector.get_columns('bird_species')}

    with engine.begin() as connection:
        if 'model_class_name' not in columns:
            try:
                connection.execute(text('ALTER TABLE bird_species ADD COLUMN model_class_name VARCHAR(100)'))
            except OperationalError as exc:
                if 'duplicate column name' not in str(exc).lower():
                    raise
        if 'iucn_status' not in columns:
            try:
                connection.execute(text("ALTER TABLE bird_species ADD COLUMN iucn_status VARCHAR(20) DEFAULT 'unknown'"))
            except OperationalError as exc:
                if 'duplicate column name' not in str(exc).lower():
                    raise
        if 'china_protection_type' not in columns:
            try:
                connection.execute(
                    text("ALTER TABLE bird_species ADD COLUMN china_protection_type VARCHAR(30) DEFAULT 'none'")
                )
            except OperationalError as exc:
                if 'duplicate column name' not in str(exc).lower():
                    raise
        if 'attention_level' not in columns:
            try:
                connection.execute(text("ALTER TABLE bird_species ADD COLUMN attention_level VARCHAR(20) DEFAULT 'none'"))
            except OperationalError as exc:
                if 'duplicate column name' not in str(exc).lower():
                    raise

        connection.execute(
            text('CREATE UNIQUE INDEX IF NOT EXISTS ix_bird_species_model_class_name ON bird_species (model_class_name)')
        )
        connection.execute(
            text(
                'CREATE INDEX IF NOT EXISTS ix_bird_species_china_protection_type '
                'ON bird_species (china_protection_type)'
            )
        )
        connection.execute(
            text('CREATE INDEX IF NOT EXISTS ix_bird_species_attention_level ON bird_species (attention_level)')
        )
