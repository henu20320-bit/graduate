from __future__ import annotations

from pathlib import Path
import sys

import yaml
from sqlalchemy import inspect, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
DATASET_YAML = PROJECT_DIR / 'datasets' / 'data.yaml'

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal, engine
from app.models import BirdSpecies


KNOWN_METADATA: dict[str, dict[str, object]] = {
    'bailu': {
        'chinese_name': '白鹭',
        'english_name': 'Little Egret',
        'scientific_name': 'Egretta garzetta',
        'category': 'Pelecaniformes',
        'is_rare': False,
        'rare_level': 'none',
        'description': 'Wetland indicator species.',
    },
    'heishuiji': {
        'chinese_name': '黑水鸡',
        'english_name': None,
        'scientific_name': None,
        'category': 'Gruiformes',
        'is_rare': False,
        'rare_level': 'none',
        'description': 'Metadata imported from dataset class mapping.',
    },
    'yuanyang': {
        'chinese_name': '鸳鸯',
        'english_name': 'Mandarin Duck',
        'scientific_name': 'Aix galericulata',
        'category': 'Anseriformes',
        'is_rare': False,
        'rare_level': 'none',
        'description': 'Metadata imported from dataset class mapping.',
    },
}


def ensure_model_class_name_column() -> None:
    inspector = inspect(engine)
    columns = {column['name'] for column in inspector.get_columns('bird_species')}
    if 'model_class_name' in columns:
        return

    with engine.begin() as connection:
        connection.execute(text('ALTER TABLE bird_species ADD COLUMN model_class_name VARCHAR(100)'))
        connection.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_bird_species_model_class_name ON bird_species (model_class_name)'))


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

    return [item for item in ordered if item]


def build_species_payload(model_class_name: str) -> dict[str, object]:
    payload = {
        'chinese_name': model_class_name,
        'model_class_name': model_class_name,
        'english_name': model_class_name,
        'scientific_name': None,
        'category': 'dataset_import',
        'is_rare': False,
        'rare_level': 'none',
        'description': 'Imported from dataset class mapping. Metadata can be refined later.',
        'image_url': None,
    }
    payload.update(KNOWN_METADATA.get(model_class_name, {}))
    payload['model_class_name'] = model_class_name
    return payload


def upsert_species(db, model_class_name: str) -> tuple[str, str]:
    payload = build_species_payload(model_class_name)
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
    if not species.english_name and payload.get('english_name'):
        species.english_name = str(payload['english_name'])
    if not species.scientific_name and payload.get('scientific_name'):
        species.scientific_name = str(payload['scientific_name'])
    if not species.category and payload.get('category'):
        species.category = str(payload['category'])
    if not species.description and payload.get('description'):
        species.description = str(payload['description'])
    if payload.get('is_rare'):
        species.is_rare = bool(payload['is_rare'])
        species.rare_level = str(payload['rare_level'])
    return ('updated', model_class_name)


def main() -> None:
    ensure_model_class_name_column()
    class_names = load_dataset_class_names()

    db = SessionLocal()
    created = 0
    updated = 0
    try:
        for class_name in class_names:
            action, _ = upsert_species(db, class_name)
            if action == 'created':
                created += 1
            else:
                updated += 1
        db.commit()
        print(f'Species mapping synchronized successfully. created={created}, updated={updated}, total_classes={len(class_names)}')
    finally:
        db.close()


if __name__ == '__main__':
    main()
