from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean a YOLO dataset by moving orphan label files to a backup directory.")
    parser.add_argument("--dataset-root", required=True, help="Dataset root path, such as ../datasets.")
    parser.add_argument(
        "--backup-dir",
        default="../datasets/_cleanup_backup",
        help="Directory used to store moved orphan label files.",
    )
    return parser.parse_args()


def image_basenames(images_dir: Path) -> set[str]:
    names: set[str] = set()
    for suffix in ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"):
        names.update(file.stem for file in images_dir.glob(suffix))
    return names


def clean_split(dataset_root: Path, split: str, backup_dir: Path) -> int:
    images_dir = dataset_root / split / "images"
    labels_dir = dataset_root / split / "labels"
    image_names = image_basenames(images_dir)
    moved_count = 0

    for label_file in labels_dir.glob("*.txt"):
        if label_file.stem in image_names:
            continue
        target_dir = backup_dir / split / "labels"
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(label_file), str(target_dir / label_file.name))
        moved_count += 1

    return moved_count


def main() -> None:
    args = parse_args()
    dataset_root = Path(args.dataset_root).resolve()
    backup_dir = Path(args.backup_dir).resolve()

    total_moved = 0
    for split in ("train", "valid", "test"):
        moved = clean_split(dataset_root, split, backup_dir)
        total_moved += moved
        print(f"{split}: moved {moved} orphan label files.")

    print(f"Cleanup completed. Total moved files: {total_moved}")
    print(f"Backup directory: {backup_dir}")


if __name__ == "__main__":
    main()