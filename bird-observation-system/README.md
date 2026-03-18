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

## Current Scope

The project currently includes:

- backend API, database, detection, alert, and statistics modules
- frontend dashboard skeleton for visualization and demonstration
- experiment scripts for YOLOv8 training, validation, testing, comparison, and plotting

## Quick Start

```bash
cd backend
.\.venv310\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py
python scripts/seed_data.py
uvicorn app.main:app --reload
```

## Experiment Module

See `experiments/README.md` for:

- dataset template
- training and evaluation scripts
- comparison experiment runner
- CSV export and plotting scripts