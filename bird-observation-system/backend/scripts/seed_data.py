from __future__ import annotations

import csv
from pathlib import Path
import sys

import yaml
from sqlalchemy import inspect, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
DATASET_YAML = PROJECT_DIR / 'datasets' / 'data.yaml'
MAPPING_CSV = PROJECT_DIR / 'docs' / 'bird_species_mapping_template.csv'

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal, engine
from app.models import BirdSpecies


EXCLUDED_CLASS_NAMES = {
    'bird',  # overly generic label
    'heyu',  # likely non-bird / mislabeled sample
}

CATEGORY_KEYWORDS = {
    '水鸟': 'waterbird',
    '涉禽': 'wader',
    '林鸟': 'forest_bird',
    '鸣禽': 'songbird',
    '鸭类': 'waterfowl',
    '雀形目': 'passeriformes',
}


def ensure_species_columns() -> None:
    inspector = inspect(engine)
    columns = {column['name'] for column in inspector.get_columns('bird_species')}

    with engine.begin() as connection:
        if 'model_class_name' not in columns:
            connection.execute(text('ALTER TABLE bird_species ADD COLUMN model_class_name VARCHAR(100)'))
        if 'iucn_status' not in columns:
            connection.execute(text("ALTER TABLE bird_species ADD COLUMN iucn_status VARCHAR(20) DEFAULT 'unknown'"))
        if 'china_protection_type' not in columns:
            connection.execute(
                text("ALTER TABLE bird_species ADD COLUMN china_protection_type VARCHAR(30) DEFAULT 'none'")
            )
        if 'attention_level' not in columns:
            connection.execute(text("ALTER TABLE bird_species ADD COLUMN attention_level VARCHAR(20) DEFAULT 'none'"))

        connection.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_bird_species_model_class_name ON bird_species (model_class_name)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS ix_bird_species_china_protection_type ON bird_species (china_protection_type)'))
        connection.execute(text('CREATE INDEX IF NOT EXISTS ix_bird_species_attention_level ON bird_species (attention_level)'))


def load_dataset_class_names() -> list[str]:
    if not DATASET_YAML.exists():
        raise FileNotFoundError(f'Dataset yaml not found: {DATASET_YAML}')

    payload = yaml.safe_load(DATASET_YAML.read_text(encoding='utf-8')) or {}
    names = payload.get('names', {})
    if isinstance(names, dict):
        ordered = [str(names[index]).strip() for index in sorted(names)]
    elif isinstance(names, list):
        ordered = [str(item).strip() for item in names]
    else:
        ordered = []

    filtered: list[str] = []
    for item in ordered:
        normalized = item.strip()
        if not normalized or normalized in EXCLUDED_CLASS_NAMES:
            continue
        filtered.append(normalized)
    return filtered


def infer_category(notes: str) -> str:
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword in notes:
            return category
    return 'dataset_import'


def load_csv_metadata() -> dict[str, dict[str, object]]:
    if not MAPPING_CSV.exists():
        raise FileNotFoundError(f'Mapping csv not found: {MAPPING_CSV}')

    metadata: dict[str, dict[str, object]] = {}
    with MAPPING_CSV.open('r', encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            model_class_name = (row.get('model_class_name') or '').strip()
            if not model_class_name or model_class_name in EXCLUDED_CLASS_NAMES:
                continue

            notes = (row.get('notes') or '').strip()
            scientific_name = (row.get('scientific_name') or 'unknown').strip()
            metadata[model_class_name] = {
                'chinese_name': (row.get('chinese_name_candidate') or model_class_name).strip(),
                'model_class_name': model_class_name,
                'english_name': None,
                'scientific_name': None if scientific_name in {'', 'unknown'} else scientific_name,
                'category': infer_category(notes),
                'iucn_status': (row.get('iucn_status') or 'unknown').strip() or 'unknown',
                'china_protection_type': (row.get('china_protection') or 'none').strip() or 'none',
                'attention_level': (row.get('system_alert_level') or 'none').strip() or 'none',
                'is_rare': (row.get('system_alert_level') or 'none').strip() in {'high', 'medium'},
                'rare_level': (row.get('system_alert_level') or 'none').strip() if (row.get('system_alert_level') or 'none').strip() in {'high', 'medium'} else 'none',
                'description': notes or '由物种映射表导入，可后续继续补充说明。',
                'image_url': None,
            }
    return metadata


def build_species_payload(model_class_name: str, csv_metadata: dict[str, dict[str, object]]) -> dict[str, object]:
    payload = {
        'chinese_name': model_class_name,
        'model_class_name': model_class_name,
        'english_name': None,
        'scientific_name': None,
        'category': 'dataset_import',
        'iucn_status': 'unknown',
        'china_protection_type': 'none',
        'attention_level': 'none',
        'is_rare': False,
        'rare_level': 'none',
        'description': '由数据集类别映射导入，可后续继续补充物种元数据。',
        'image_url': None,
    }
    payload.update(csv_metadata.get(model_class_name, {}))
    return payload


def upsert_species(db, model_class_name: str, csv_metadata: dict[str, dict[str, object]]) -> tuple[str, str]:
    payload = build_species_payload(model_class_name, csv_metadata)
    species = (
        db.query(BirdSpecies)
        .filter(
            (BirdSpecies.model_class_name == model_class_name)
            | (BirdSpecies.chinese_name == payload['chinese_name'])
        )
        .first()
    )

    if species is None:
        db.add(BirdSpecies(**payload))
        return ('created', model_class_name)

    species.model_class_name = model_class_name
    for key in ('chinese_name', 'english_name', 'scientific_name', 'category', 'description', 'image_url'):
        new_value = payload.get(key)
        old_value = getattr(species, key)
        if new_value and (old_value is None or old_value == '' or old_value == species.model_class_name):
            setattr(species, key, new_value)

    species.iucn_status = str(payload.get('iucn_status', species.iucn_status or 'unknown'))
    species.china_protection_type = str(payload.get('china_protection_type', species.china_protection_type or 'none'))
    species.attention_level = str(payload.get('attention_level', species.attention_level or 'none'))
    species.is_rare = bool(payload.get('is_rare', False))
    species.rare_level = str(payload.get('rare_level', 'none'))
    return ('updated', model_class_name)


def main() -> None:
    ensure_species_columns()
    class_names = load_dataset_class_names()
    csv_metadata = load_csv_metadata()

    db = SessionLocal()
    created = 0
    updated = 0
    try:
        for class_name in class_names:
            action, _ = upsert_species(db, class_name, csv_metadata)
            if action == 'created':
                created += 1
            else:
                updated += 1
        db.commit()
        print(
            'Species mapping synchronized successfully. '
            f'created={created}, updated={updated}, total_classes={len(class_names)}, '
            f'csv_entries={len(csv_metadata)}, excluded={sorted(EXCLUDED_CLASS_NAMES)}'
        )
    finally:
        db.close()


if __name__ == '__main__':
    main()
