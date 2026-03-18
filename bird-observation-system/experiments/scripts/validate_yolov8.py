from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from ultralytics import YOLO


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("validate_yolov8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a YOLOv8 model on the validation split.")
    parser.add_argument("--data", required=True, help="Path to dataset YAML.")
    parser.add_argument("--weights", required=True, help="Path to model weights.")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size.")
    parser.add_argument("--batch", type=int, default=16, help="Batch size.")
    parser.add_argument("--device", default="cpu", help="Device id, cpu or cuda.")
    parser.add_argument("--project", default="../experiments/results", help="Validation output directory.")
    parser.add_argument("--name", default="yolov8_val", help="Validation run name.")
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
    result = model.val(
        data=str(Path(args.data).resolve()),
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        split="val",
        project=str(Path(args.project).resolve()),
        name=args.name,
        plots=True,
        save_json=False,
        exist_ok=True,
    )

    summary = {
        "weights": str(Path(args.weights).resolve()),
        "data": str(Path(args.data).resolve()),
        "precision": metric_value(result, "mp"),
        "recall": metric_value(result, "mr"),
        "map50": metric_value(result, "map50"),
        "map50_95": metric_value(result, "map"),
        "fps": None,
        "split": "val",
    }
    output_path = Path(args.project).resolve() / args.name / "validation_summary.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Validation summary saved to %s", output_path)


if __name__ == "__main__":
    main()