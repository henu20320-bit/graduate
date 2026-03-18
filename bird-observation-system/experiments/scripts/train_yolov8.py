from __future__ import annotations

import argparse
import csv
import json
import logging
from pathlib import Path
from typing import Any

import yaml
from ultralytics import YOLO


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("train_yolov8")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def resolve_path(base_dir: Path, value: str | None) -> str | None:
    if not value:
        return value
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((base_dir / path).resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a YOLOv8 model for bird detection.")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config.")
    return parser.parse_args()


def build_train_kwargs(config: dict[str, Any], config_dir: Path) -> dict[str, Any]:
    project = resolve_path(config_dir, config.get("project", "../experiments/results"))
    data = resolve_path(config_dir, config["data"])
    kwargs = {
        "data": data,
        "project": project,
        "name": config.get("name", "yolov8_baseline"),
        "epochs": int(config.get("epochs", 100)),
        "imgsz": int(config.get("imgsz", 640)),
        "batch": config.get("batch", 16),
        "device": config.get("device", "cpu"),
        "workers": int(config.get("workers", 4)),
        "patience": int(config.get("patience", 30)),
        "optimizer": config.get("optimizer", "auto"),
        "seed": int(config.get("seed", 42)),
        "cache": bool(config.get("cache", False)),
        "verbose": bool(config.get("verbose", True)),
        "plots": True,
        "save": True,
        "exist_ok": True,
    }
    return kwargs


def summarize_training(run_dir: Path) -> dict[str, Any]:
    metrics = {
        "run_dir": str(run_dir),
        "best_weights": str(run_dir / "weights" / "best.pt"),
        "results_csv": str(run_dir / "results.csv"),
    }
    csv_file = run_dir / "results.csv"
    if csv_file.exists():
        with csv_file.open("r", encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        if rows:
            last_row = rows[-1]
            for key, candidates in {
                "precision": ["metrics/precision(B)", "metrics/precision"],
                "recall": ["metrics/recall(B)", "metrics/recall"],
                "map50": ["metrics/mAP50(B)", "metrics/mAP50"],
                "map50_95": ["metrics/mAP50-95(B)", "metrics/mAP50-95"],
                "fitness": ["fitness"],
            }.items():
                metrics[key] = next((float(last_row[c]) for c in candidates if c in last_row and last_row[c] != ""), None)
    return metrics


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_yaml(config_path)
    config_dir = config_path.parent

    model_path = resolve_path(config_dir, config["model"])
    logger.info("Training YOLOv8 model from %s", model_path)

    model = YOLO(model_path)
    train_kwargs = build_train_kwargs(config, config_dir)
    model.train(**train_kwargs)

    run_dir = Path(train_kwargs["project"]) / train_kwargs["name"]
    summary = summarize_training(run_dir)
    summary_path = run_dir / "training_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Training finished. Summary saved to %s", summary_path)


if __name__ == "__main__":
    main()