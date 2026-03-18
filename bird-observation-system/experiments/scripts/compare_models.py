from __future__ import annotations

import argparse
import csv
import json
import logging
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from ultralytics import YOLO


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("compare_models")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run baseline and comparison experiments.")
    parser.add_argument("--config", required=True, help="Path to the comparison config YAML.")
    return parser.parse_args()


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


def parse_results_csv(results_csv: Path) -> dict[str, float | None]:
    with results_csv.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        return {"precision": None, "recall": None, "map50": None, "map50_95": None}
    row = rows[-1]

    def pick(candidates: list[str]) -> float | None:
        for candidate in candidates:
            raw = row.get(candidate)
            if raw not in (None, ""):
                return float(raw)
        return None

    return {
        "precision": pick(["metrics/precision(B)", "metrics/precision"]),
        "recall": pick(["metrics/recall(B)", "metrics/recall"]),
        "map50": pick(["metrics/mAP50(B)", "metrics/mAP50"]),
        "map50_95": pick(["metrics/mAP50-95(B)", "metrics/mAP50-95"]),
    }


def run_yolov8_experiment(exp: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    model_path = resolve_path(base_dir, exp["model"])
    data_path = resolve_path(base_dir, exp["data"])
    project = resolve_path(base_dir, exp.get("project", "../experiments/results"))
    run_name = exp.get("run_name", exp["name"])

    logger.info("Running YOLOv8 experiment: %s", exp["name"])
    model = YOLO(model_path)
    model.train(
        data=data_path,
        project=project,
        name=run_name,
        epochs=int(exp.get("epochs", 100)),
        imgsz=int(exp.get("imgsz", 640)),
        batch=exp.get("batch", 16),
        device=exp.get("device", "cpu"),
        workers=int(exp.get("workers", 4)),
        plots=True,
        exist_ok=True,
    )

    run_dir = Path(project) / run_name
    parsed = parse_results_csv(run_dir / "results.csv")
    parsed.update(
        {
            "experiment_name": exp["name"],
            "model_type": "yolov8",
            "weights": str(run_dir / "weights" / "best.pt"),
            "fps": exp.get("fps"),
        }
    )
    return parsed


def run_yolov5_experiment(exp: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    repo_path = Path(resolve_path(base_dir, exp["repo_path"]))
    data_path = resolve_path(base_dir, exp["data"])
    project = resolve_path(base_dir, exp.get("project", "../experiments/results"))
    run_name = exp.get("run_name", exp["name"])

    train_script = repo_path / "train.py"
    if not train_script.exists():
        raise FileNotFoundError(f"YOLOv5 train.py not found: {train_script}")

    command = [
        "python",
        str(train_script),
        "--weights",
        str(exp.get("weights", "yolov5s.pt")),
        "--data",
        data_path,
        "--epochs",
        str(exp.get("epochs", 100)),
        "--img",
        str(exp.get("imgsz", 640)),
        "--batch",
        str(exp.get("batch", 16)),
        "--device",
        str(exp.get("device", "cpu")),
        "--project",
        project,
        "--name",
        run_name,
        "--exist-ok",
    ]
    logger.info("Running YOLOv5 experiment: %s", exp["name"])
    subprocess.run(command, cwd=repo_path, check=True)

    run_dir = Path(project) / run_name
    parsed = parse_results_csv(run_dir / "results.csv")
    parsed.update(
        {
            "experiment_name": exp["name"],
            "model_type": "yolov5",
            "weights": str(run_dir / "weights" / "best.pt"),
            "fps": exp.get("fps"),
        }
    )
    return parsed


def run_custom_command_experiment(exp: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    command = exp["train_command"]
    logger.info("Running custom comparison experiment: %s", exp["name"])
    subprocess.run(command, shell=True, check=True, cwd=base_dir)

    metrics_file = Path(resolve_path(base_dir, exp["metrics_file"]))
    if not metrics_file.exists():
        raise FileNotFoundError(f"Metrics file not found: {metrics_file}")
    metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
    metrics["experiment_name"] = exp["name"]
    metrics["model_type"] = exp.get("type", "custom_command")
    return metrics


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = load_yaml(config_path)
    base_dir = config_path.parent

    rows: list[dict[str, Any]] = []
    for exp in config.get("experiments", []):
        exp_type = exp.get("type", "yolov8").lower()
        if exp_type == "yolov8":
            rows.append(run_yolov8_experiment(exp, base_dir))
        elif exp_type == "yolov5":
            rows.append(run_yolov5_experiment(exp, base_dir))
        elif exp_type in {"custom_command", "fasterrcnn"}:
            rows.append(run_custom_command_experiment(exp, base_dir))
        else:
            raise ValueError(f"Unsupported comparison type: {exp_type}")

    output_csv = Path(resolve_path(base_dir, config.get("output_csv", "../experiments/results/csv/comparison_summary.csv")))
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_csv, index=False, encoding="utf-8-sig")
    logger.info("Comparison summary saved to %s", output_csv)


if __name__ == "__main__":
    main()