from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any

from ultralytics import YOLO


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("test_yolov8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test a YOLOv8 model on the test split.")
    parser.add_argument("--data", required=True, help="Path to dataset YAML.")
    parser.add_argument("--weights", required=True, help="Path to model weights.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size.")
    parser.add_argument("--batch", type=int, default=16, help="Batch size.")
    parser.add_argument("--device", default="cpu", help="Device id, cpu or cuda.")
    parser.add_argument("--project", default="../experiments/results", help="Test output directory.")
    parser.add_argument("--name", default="yolov8_test", help="Test run name.")
    return parser.parse_args()


def metric_value(result: Any, attr: str) -> float | None:
    value = getattr(result.box, attr, None)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    args = parse_args()
    model = YOLO(str(Path(args.weights).resolve()))

    start = time.perf_counter()
    result = model.val(
        data=str(Path(args.data).resolve()),
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        split="test",
        project=str(Path(args.project).resolve()),
        name=args.name,
        plots=True,
        save_json=False,
        exist_ok=True,
    )
    elapsed = time.perf_counter() - start

    fps = None
    if elapsed > 0:
        fps = round(max(1, args.batch) / elapsed, 4)

    summary = {
        "weights": str(Path(args.weights).resolve()),
        "data": str(Path(args.data).resolve()),
        "precision": metric_value(result, "mp"),
        "recall": metric_value(result, "mr"),
        "map50": metric_value(result, "map50"),
        "map50_95": metric_value(result, "map"),
        "fps": fps,
        "split": "test",
        "elapsed_seconds": round(elapsed, 4),
    }
    output_path = Path(args.project).resolve() / args.name / "test_summary.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Test summary saved to %s", output_path)


if __name__ == "__main__":
    main()