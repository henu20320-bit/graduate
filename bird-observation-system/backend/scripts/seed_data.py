from datetime import datetime, timedelta
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.models import AlertRecord, BirdSpecies, DetectionRecord


def main() -> None:
    db = SessionLocal()
    try:
        if db.query(BirdSpecies).count() > 0:
            print('Seed data already exists, skipping.')
            return

        species_list = [
            BirdSpecies(
                chinese_name='麻雀',
                english_name='Sparrow',
                scientific_name='Passer montanus',
                category='Passeriformes',
                is_rare=False,
                rare_level='none',
                description='Common urban bird species.',
            ),
            BirdSpecies(
                chinese_name='黑脸琵鹭',
                english_name='Black-faced Spoonbill',
                scientific_name='Platalea minor',
                category='Pelecaniformes',
                is_rare=True,
                rare_level='high',
                description='National first-class protected bird.',
            ),
            BirdSpecies(
                chinese_name='白鹭',
                english_name='Little Egret',
                scientific_name='Egretta garzetta',
                category='Pelecaniformes',
                is_rare=False,
                rare_level='none',
                description='Wetland indicator species.',
            ),
        ]
        db.add_all(species_list)
        db.commit()

        for item in species_list:
            db.refresh(item)

        detection = DetectionRecord(
            source_type='image',
            source_file='demo.jpg',
            species_id=species_list[1].id,
            confidence=0.86,
            bbox_x1=120,
            bbox_y1=80,
            bbox_x2=300,
            bbox_y2=260,
            capture_time=datetime.utcnow() - timedelta(minutes=10),
            location='Shanghai Wetland Park',
            is_alert=True,
            alert_level='high',
            result_image_path='outputs/demo_result.jpg',
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)

        alert = AlertRecord(
            detection_record_id=detection.id,
            species_id=species_list[1].id,
            alert_level='high',
            alert_message='Detected a rare protected bird: Black-faced Spoonbill.',
            handled_status='pending',
        )
        db.add(alert)
        db.commit()
        print('Seed data inserted successfully.')
    finally:
        db.close()


if __name__ == '__main__':
    main()
