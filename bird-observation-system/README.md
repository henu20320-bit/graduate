# Bird Observation System

## Project Structure

```text
bird-observation-system/
├── backend/
├── frontend/
├── datasets/
├── experiments/
└── docs/
```

## Phase 1 Scope

Phase 1 focuses on:

- backend project skeleton
- configuration management
- database models and initialization
- basic REST API framework

## Quick Start

```bash
cd backend
pip install -r requirements.txt
python scripts/init_db.py
python scripts/seed_data.py
uvicorn app.main:app --reload
```

## Next Phase

Phase 2 will add the YOLOv8 inference service, image/video/camera detection pipeline, and result persistence.
