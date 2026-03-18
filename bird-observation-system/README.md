# 基于 YOLOv8 的鸟类检测与识别系统

## 1. 项目简介

本项目面向鸟类智能观测场景，基于 YOLOv8 构建了一个集“鸟类检测、类别识别、珍稀预警、记录存储、统计分析、可视化展示”于一体的本科毕业设计系统。

系统目标不是只实现单一检测模型，而是完成一个可运行的闭环平台：

- 前端上传图片、视频或接入摄像头
- 后端调用 YOLOv8 完成目标检测与类别识别
- 系统自动记录检测结果与出现频次
- 针对珍稀鸟类进行分级预警
- 对历史数据进行统计分析与可视化展示

该系统适用于毕业设计答辩展示，也便于后续继续开展模型优化、对比实验和论文实验分析。

## 2. 系统功能

### 2.1 图片检测

- 支持上传单张鸟类图片进行检测
- 返回鸟类类别、置信度、边界框坐标
- 支持保存检测结果图像

### 2.2 视频检测

- 支持上传本地视频文件进行逐帧检测
- 输出检测后的视频结果
- 可统计视频中的鸟类出现情况

### 2.3 摄像头实时检测

- 支持调用本地摄像头进行实时检测
- 实时返回检测结果
- 适合现场答辩演示

### 2.4 鸟类识别

- 基于 YOLOv8 同时完成目标检测与类别识别
- 当前数据集包含 34 类鸟类
- 支持后续替换权重继续扩展类别

### 2.5 珍稀鸟类预警

- 根据鸟类基础信息表判断是否为珍稀鸟类
- 按置信度和保护等级进行分级预警
- 自动写入预警记录表
- 支持前端弹窗展示最近预警

### 2.6 历史记录管理

- 自动保存检测记录
- 支持查询检测历史
- 支持查看单条检测详情与预警详情

### 2.7 数据统计分析

- 统计总检测次数、今日检测次数、预警次数
- 按鸟类类别统计频次
- 按日期统计检测趋势
- 统计珍稀鸟类预警情况
- 提供基础迁徙趋势模拟分析

### 2.8 可视化大屏

- 首页仪表盘展示核心指标
- 使用 ECharts 展示柱状图、折线图、饼图和预警列表
- 适合毕业设计答辩场景展示

## 3. 项目结构

```text
bird-observation-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   ├── outputs/
│   ├── scripts/
│   ├── uploads/
│   ├── weights/
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── router/
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── datasets/
├── experiments/
│   ├── configs/
│   ├── results/
│   ├── scripts/
│   ├── requirements.txt
│   └── README.md
├── docs/
└── README.md
```

## 4. 环境依赖

### 4.1 后端环境

- Python 3.10+
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- Ultralytics YOLOv8
- OpenCV
- MySQL 或 SQLite

### 4.2 前端环境

- Node.js 18+，当前开发环境已验证 `Node.js 24.x`
- npm 9+
- Vue 3
- Element Plus
- Axios
- ECharts
- Vue Router

### 4.3 硬件环境

- CPU 可运行
- GPU 可选，若具备 CUDA 环境可显著提升训练和推理速度

## 5. 快速启动

### 5.1 后端启动

进入后端目录：

```bash
cd backend
```

创建并激活虚拟环境后安装依赖：

```bash
python -m venv .venv310
.\.venv310\Scripts\activate
pip install -r requirements.txt
```

复制环境变量文件：

```bash
copy .env.example .env
```

初始化数据库：

```bash
python scripts/init_db.py
python scripts/seed_data.py
```

启动后端服务：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动后访问：

- 接口文档：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/health`

### 5.2 前端启动

进入前端目录：

```bash
cd frontend
```

安装依赖：

```bash
npm install
```

启动前端：

```bash
npm run dev
```

启动后访问：

- 前端首页：`http://localhost:5173`

### 5.3 前后端联调说明

- 前端通过 Vite 代理访问后端 `/api`
- 默认代理目标为 `http://127.0.0.1:8000`
- 若后端地址变化，可在前端环境配置中调整 API 基地址

## 6. 模型说明

### 6.1 模型选择

- 本项目使用 Ultralytics YOLOv8 作为核心目标检测模型
- 同时支持图片、视频和摄像头三种输入源

### 6.2 数据集说明

- 当前数据集包含 34 类鸟类
- 图片规模约 1 万张
- 数据采用 YOLO 标注格式
- 已完成 `train / valid / test` 划分

### 6.3 重新训练

训练配置位于：

- `experiments/configs/train_yolov8.yaml`

示例训练命令：

```bash
cd experiments
python .\scripts\train_yolov8.py --config .\configs\train_yolov8.yaml
```

验证命令：

```bash
python .\scripts\validate_yolov8.py --data ..\datasets\data.yaml --weights .\results\yolov8_baseline\weights\best.pt
```

测试命令：

```bash
python .\scripts\test_yolov8.py --data ..\datasets\data.yaml --weights .\results\yolov8_baseline\weights\best.pt
```

## 7. API 说明

核心接口如下：

### 7.1 检测接口

- `POST /api/detect/image`：图片检测
- `POST /api/detect/video`：视频检测
- `GET /api/detect/camera/start`：启动摄像头检测
- `GET /api/detect/camera/stop`：停止摄像头检测
- `GET /api/detect/camera/stream`：获取实时检测结果

### 7.2 记录与预警接口

- `GET /api/records`：获取检测记录列表
- `GET /api/records/{id}`：获取检测记录详情
- `GET /api/alerts`：获取预警记录列表
- `GET /api/alerts/latest`：获取最近预警

### 7.3 统计接口

- `GET /api/stats/overview`：概览统计
- `GET /api/stats/species-frequency`：鸟类频次统计
- `GET /api/stats/daily-trend`：日期趋势统计
- `GET /api/stats/rare-birds`：珍稀鸟类统计
- `GET /api/stats/migration-trend`：迁徙趋势基础统计

## 8. 系统演示说明

### 8.1 图片检测演示

1. 启动前后端服务
2. 打开后端 Swagger 文档 `http://localhost:8000/docs`
3. 选择 `POST /api/detect/image`
4. 上传一张鸟类图片
5. 查看检测结果 JSON 与结果图保存路径

### 8.2 视频检测演示

1. 打开 `POST /api/detect/video`
2. 上传本地测试视频
3. 查看视频检测结果与输出文件路径

### 8.3 珍稀预警演示

1. 使用包含珍稀鸟类的测试图片或视频
2. 触发检测接口
3. 系统根据 `bird_species` 表和置信度规则生成预警
4. 在 `/api/alerts/latest` 或首页最近预警区域查看结果

## 9. 实验与性能

本项目支持以下实验内容：

- YOLOv8 基线实验
- YOLOv8 与 YOLOv5 / Faster R-CNN 对比实验
- 指标导出与论文图表绘制

重点指标包括：

- Precision
- Recall
- mAP@0.5
- mAP@0.5:0.95
- FPS

相关脚本位于：

- `experiments/scripts/export_metrics_csv.py`
- `experiments/scripts/compare_models.py`
- `experiments/scripts/plot_experiments.py`

## 10. 项目亮点

- 基于 YOLOv8 实现鸟类检测与识别，具备实时目标检测能力
- 同时支持图片、视频、摄像头三种输入源，适合实际展示与扩展
- 引入珍稀鸟类分级预警机制，实现检测与业务逻辑联动
- 集成记录管理、统计分析和可视化展示，形成完整闭环系统
- 前后端分离、结构清晰、部署简单，适合作为本科毕业设计项目

## 11. 后续改进方向

- 增加更细粒度的鸟类类别与亚种识别
- 针对小目标和复杂背景进一步优化模型
- 引入类别重加权或重采样策略改善长尾类别识别效果
- 尝试轻量化模型部署，提高边缘设备实时性
- 支持多摄像头接入与更丰富的空间分布分析

## 补充说明

- 本项目优先强调系统完整性、可运行性和答辩展示效果
- 数据集、训练权重和运行日志默认保留在本地，不纳入 Git 仓库
- 若用于论文撰写，可直接基于 `experiments/` 模块开展实验记录、指标统计与图表生成