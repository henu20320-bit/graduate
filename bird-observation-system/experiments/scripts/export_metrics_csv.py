from __future__ import annotations

import argparse
import csv
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("export_metrics_csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export training results into a thesis-friendly CSV.")
    parser.add_argument("--run-dir", required=True, help="YOLO run directory that contains results.csv.")
    parser.add_argument("--output", required=True, help="Output CSV path.")
    return parser.parse_args()


def read_last_row(csv_path: Path) -> dict[str, Any]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        raise ValueError(f"No rows found in {csv_path}")
    return rows[-1]


def find_value(row: dict[str, Any], candidates: list[str]) -> float | None:
    for candidate in candidates:
        raw = row.get(candidate)
        if raw not in (None, ""):
            return float(raw)
    return None


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    results_csv = run_dir / "results.csv"
    if not results_csv.exists():
        raise FileNotFoundError(f"results.csv not found: {results_csv}")

    last_row = read_last_row(results_csv)
    summary_json = run_dir / "training_summary.json"
    extra_summary: dict[str, Any] = {}
    if summary_json.exists():
        extra_summary = json.loads(summary_json.read_text(encoding="utf-8"))

    export_row = {
        "experiment_name": run_dir.name,
        "precision": find_value(last_row, ["metrics/precision(B)", "metrics/precision"]),
        "recall": find_value(last_row, ["metrics/recall(B)", "metrics/recall"]),
        "map50": find_value(last_row, ["metrics/mAP50(B)", "metrics/mAP50"]),
        "map50_95": find_value(last_row, ["metrics/mAP50-95(B)", "metrics/mAP50-95"]),
        "fitness": find_value(last_row, ["fitness"]),
        "best_weights": extra_summary.get("best_weights", str(run_dir / "weights" / "best.pt")),
        "results_csv": str(results_csv),
    }

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([export_row]).to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info("Metrics CSV exported to %s", output_path)


if __name__ == "__main__":
    main()