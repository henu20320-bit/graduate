from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import inspect, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import engine


def ensure_column(connection, columns: set[str], name: str, ddl: str) -> None:
    if name in columns:
        return
    connection.execute(text(ddl))
    print(f'Added column: bird_species.{name}')


def main() -> None:
    inspector = inspect(engine)
    columns = {column['name'] for column in inspector.get_columns('bird_species')}

    with engine.begin() as connection:
        ensure_column(connection, columns, 'model_class_name', 'ALTER TABLE bird_species ADD COLUMN model_class_name VARCHAR(100)')
        ensure_column(connection, columns, 'iucn_status', "ALTER TABLE bird_species ADD COLUMN iucn_status VARCHAR(20) DEFAULT 'unknown'")
        ensure_column(
            connection,
            columns,
            'china_protection_type',
            "ALTER TABLE bird_species ADD COLUMN china_protection_type VARCHAR(30) DEFAULT 'none'",
        )
        ensure_column(
            connection,
            columns,
            'attention_level',
            "ALTER TABLE bird_species ADD COLUMN attention_level VARCHAR(20) DEFAULT 'none'",
        )

        connection.execute(text("UPDATE bird_species SET iucn_status = COALESCE(iucn_status, 'unknown')"))
        connection.execute(text("UPDATE bird_species SET china_protection_type = COALESCE(china_protection_type, 'none')"))
        connection.execute(text("UPDATE bird_species SET attention_level = COALESCE(attention_level, 'none')"))

        connection.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_bird_species_model_class_name ON bird_species (model_class_name)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS ix_bird_species_china_protection_type ON bird_species (china_protection_type)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS ix_bird_species_attention_level ON bird_species (attention_level)'))

        print('Ensured indexes: ix_bird_species_model_class_name, ix_bird_species_china_protection_type, ix_bird_species_attention_level')


if __name__ == '__main__':
    main()
