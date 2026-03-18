from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class SplitSummary:
    split: str
    image_count: int
    label_count: int
    matched_pairs: int
    missing_images_for_labels: int
    missing_labels_for_images: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a YOLO-style dataset and export summary files.")
    parser.add_argument("--dataset-root", required=True, help="Dataset root path, such as ../datasets.")
    parser.add_argument("--yaml", required=True, help="Path to dataset yaml file.")
    parser.add_argument(
        "--output-dir",
        default="../experiments/results/logs/dataset_audit",
        help="Directory used to save audit reports.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def image_basenames(images_dir: Path) -> set[str]:
    names: set[str] = set()
    for suffix in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
        names.update(file.stem for file in images_dir.glob(suffix))
    return names


def label_basenames(labels_dir: Path) -> set[str]:
    return {file.stem for file in labels_dir.glob("*.txt")}


def collect_class_counts(labels_dir: Path) -> Counter:
    counter: Counter = Counter()
    for label_file in labels_dir.glob("*.txt"):
        for raw_line in label_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 5:
                continue
            counter[int(parts[0])] += 1
    return counter


def audit_split(dataset_root: Path, split: str) -> tuple[SplitSummary, list[str], list[str], Counter]:
    images_dir = dataset_root / split / "images"
    labels_dir = dataset_root / split / "labels"
    image_names = image_basenames(images_dir)
    label_names = label_basenames(labels_dir)

    missing_images = sorted(label_names - image_names)
    missing_labels = sorted(image_names - label_names)
    matched_pairs = len(image_names & label_names)
    summary = SplitSummary(
        split=split,
        image_count=len(image_names),
        label_count=len(label_names),
        matched_pairs=matched_pairs,
        missing_images_for_labels=len(missing_images),
        missing_labels_for_images=len(missing_labels),
    )
    return summary, missing_images, missing_labels, collect_class_counts(labels_dir)


def main() -> None:
    args = parse_args()
    dataset_root = Path(args.dataset_root).resolve()
    yaml_path = Path(args.yaml).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    config = load_yaml(yaml_path)
    split_names = ["train", "valid", "test"]
    split_summaries: list[SplitSummary] = []
    missing_reports: dict[str, dict[str, list[str]]] = {}
    total_class_counts: Counter = Counter()

    for split in split_names:
        summary, missing_images, missing_labels, class_counts = audit_split(dataset_root, split)
        split_summaries.append(summary)
        missing_reports[split] = {
            "labels_without_images": missing_images,
            "images_without_labels": missing_labels,
        }
        total_class_counts.update(class_counts)

    summary_csv = output_dir / "dataset_split_summary.csv"
    with summary_csv.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "split",
                "image_count",
                "label_count",
                "matched_pairs",
                "missing_images_for_labels",
                "missing_labels_for_images",
            ],
        )
        writer.writeheader()
        for item in split_summaries:
            writer.writerow(item.__dict__)

    class_name_map = config.get("names", {})
    class_csv = output_dir / "class_distribution.csv"
    with class_csv.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["class_id", "class_name", "box_count"])
        writer.writeheader()
        for class_id in sorted(total_class_counts):
            class_name = class_name_map.get(class_id, str(class_id))
            writer.writerow(
                {
                    "class_id": class_id,
                    "class_name": class_name,
                    "box_count": total_class_counts[class_id],
                }
            )

    report_json = output_dir / "dataset_audit_report.json"
    report_json.write_text(
        json.dumps(
            {
                "dataset_root": str(dataset_root),
                "yaml": str(yaml_path),
                "splits": [item.__dict__ for item in split_summaries],
                "missing_reports": missing_reports,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Audit summary saved to: {summary_csv}")
    print(f"Class distribution saved to: {class_csv}")
    print(f"Detailed report saved to: {report_json}")


if __name__ == "__main__":
    main()