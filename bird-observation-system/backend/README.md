# Backend

## Overview

This backend provides the phase 1 and phase 2 foundation for the bird observation system:

- FastAPI application bootstrap
- environment-based configuration
- SQLAlchemy ORM models
- unified API response structure
- YOLOv8 image, video, and camera inference service

## Run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/init_db.py
python scripts/seed_data.py
uvicorn app.main:app --reload
```

## Prepare Weights

Place your YOLOv8 weight file in `backend/weights/`.
Default weight name: `yolov8n.pt`

## Test APIs

- Health check: `GET /api/health`
- Image detection: `POST /api/detect/image`
- Video detection: `POST /api/detect/video`
- Start camera: `GET /api/detect/camera/start`
- Latest camera result: `GET /api/detect/camera/stream`
- Stop camera: `GET /api/detect/camera/stop`

## Notes

- SQLite is the default development database.
- To use MySQL, fill `MYSQL_DATABASE_URL` in `.env`.
- Camera detection returns the latest structured inference result. Streaming video transport can be added later with WebSocket or MJPEG.
