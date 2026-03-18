from __future__ import annotations

import argparse
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("plot_experiments")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot thesis figures from experiment CSV results.")
    parser.add_argument("--input", required=True, help="Input comparison CSV path.")
    parser.add_argument("--output-dir", required=True, help="Output figure directory.")
    return parser.parse_args()


def save_bar_chart(df: pd.DataFrame, metric: str, output_dir: Path) -> None:
    if metric not in df.columns:
        logger.warning("Skip plotting %s because the column does not exist.", metric)
        return

    plt.figure(figsize=(9, 5))
    colors = ["#2f6f5f", "#1f5f8b", "#c2410c", "#5b7083", "#d97706"]
    bars = plt.bar(df["experiment_name"], df[metric], color=colors[: len(df)])
    plt.title(f"{metric.upper()} Comparison")
    plt.xlabel("Experiment")
    plt.ylabel(metric.upper())
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.xticks(rotation=15)
    for bar in bars:
        height = bar.get_height()
        if pd.notna(height):
            plt.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.3f}", ha="center", va="bottom")
    plt.tight_layout()
    output_path = output_dir / f"{metric}_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info("Figure saved to %s", output_path)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    for metric in ["precision", "recall", "map50", "map50_95", "fps"]:
        save_bar_chart(df, metric, output_dir)


if __name__ == "__main__":
    main()