# Experiments

## Overview

This module contains the training and experiment scripts used for the thesis experiment section.

- YOLOv8 training
- validation and test evaluation
- CSV export for metrics
- comparison experiment runner
- figure generation for Precision, Recall, mAP, and FPS

## Directory Structure

```text
experiments/
鈹溾攢鈹€ configs/
鈹?  鈹溾攢鈹€ compare_models_example.yaml
鈹?  鈹溾攢鈹€ dataset_template.yaml
鈹?  鈹斺攢鈹€ train_yolov8.yaml
鈹溾攢鈹€ results/
鈹?  鈹溾攢鈹€ csv/
鈹?  鈹溾攢鈹€ figures/
鈹?  鈹斺攢鈹€ logs/
鈹溾攢鈹€ scripts/
鈹?  鈹溾攢鈹€ compare_models.py
鈹?  鈹溾攢鈹€ export_metrics_csv.py
鈹?  鈹溾攢鈹€ plot_experiments.py
鈹?  鈹溾攢鈹€ test_yolov8.py
鈹?  鈹溾攢鈹€ train_yolov8.py
鈹?  鈹斺攢鈹€ validate_yolov8.py
鈹斺攢鈹€ requirements.txt
```

## Before Running

You need to prepare the dataset before running training, validation, or test scripts.

Recommended dataset layout:

```text
datasets/
鈹斺攢鈹€ birds/
    鈹溾攢鈹€ images/
    鈹?  鈹溾攢鈹€ train/
    鈹?  鈹溾攢鈹€ val/
    鈹?  鈹斺攢鈹€ test/
    鈹溾攢鈹€ labels/
    鈹?  鈹溾攢鈹€ train/
    鈹?  鈹溾攢鈹€ val/
    鈹?  鈹斺攢鈹€ test/
    鈹斺攢鈹€ dataset.yaml
```

Use `configs/dataset_template.yaml` as the template for `dataset.yaml`.

## Install

Use the same Python environment as the backend, then install extra experiment dependencies:

```powershell
cd F:\姣曡\bird-observation-system\backend
.\.venv310\Scripts\activate
pip install -r ..\experiments\requirements.txt
```

## Run

### 1. Train YOLOv8 baseline

```powershell
cd F:\姣曡\bird-observation-system\experiments
python .\scripts\train_yolov8.py --config .\configs\train_yolov8.yaml
```

### 2. Validate the trained model

```powershell
python .\scripts\validate_yolov8.py --data ..\datasets\data.yaml --weights .\results\yolov8_baseline\weights\best.pt
```

### 3. Test on the test split

```powershell
python .\scripts\test_yolov8.py --data ..\datasets\data.yaml --weights .\results\yolov8_baseline\weights\best.pt
```

### 4. Export metrics to CSV

```powershell
python .\scripts\export_metrics_csv.py --run-dir .\results\yolov8_baseline --output .\results\csv\yolov8_baseline_summary.csv
```

### 5. Run comparison experiments

```powershell
python .\scripts\compare_models.py --config .\configs\compare_models_example.yaml
```

### 6. Plot thesis figures

```powershell
python .\scripts\plot_experiments.py --input .\results\csv\comparison_summary.csv --output-dir .\results\figures
```

## Notes For Thesis Writing

- Baseline experiment: train YOLOv8 and report Precision, Recall, mAP50, and mAP50-95.
- Comparison experiment: compare YOLOv8 with YOLOv5 or another baseline by using `compare_models.py`.
- Improvement experiment: modify the configuration or weight path and export the comparison CSV again.
- System performance experiment: use the exported CSV and measured FPS values for the thesis tables and figures.