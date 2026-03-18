from __future__ import annotations

import threading
import time
from pathlib import Path

import cv2
from ultralytics import YOLO
from ultralytics.engine.results import Results

from app.core.config import get_settings
from app.core.logger import get_logger
from app.schemas.inference import DetectionBox, DetectionResult
from app.utils.media import build_output_path


class BirdDetectionService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = get_logger(self.__class__.__name__)
        self._model: YOLO | None = None
        self._loaded_weight_path: str | None = None
        self._camera_thread: threading.Thread | None = None
        self._camera_stop_event = threading.Event()
        self._camera_lock = threading.Lock()
        self._camera_running = False
        self._latest_camera_result: DetectionResult | None = None

    def _resolve_weight_path(self, weight_path: str | None = None) -> str:
        if weight_path:
            return str(Path(weight_path))
        default_path = self.settings.default_weight_path
        if default_path.exists():
            return str(default_path)
        return self.settings.yolo_default_weight

    def _get_model(self, weight_path: str | None = None) -> YOLO:
        resolved_weight = self._resolve_weight_path(weight_path)
        if self._model is None or self._loaded_weight_path != resolved_weight:
            self.logger.info('Loading YOLOv8 model from %s', resolved_weight)
            self._model = YOLO(resolved_weight)
            self._loaded_weight_path = resolved_weight
        return self._model

    def _standardize_result(
        self,
        result: Results,
        source_type: str,
        source_name: str,
        inference_time_ms: float,
        result_path: Path,
    ) -> DetectionResult:
        names = result.names
        detections: list[DetectionBox] = []
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls.item())
                confidence = round(float(box.conf.item()), 4)
                xyxy = [round(float(value), 2) for value in box.xyxy[0].tolist()]
                detections.append(
                    DetectionBox(
                        class_id=class_id,
                        class_name=str(names.get(class_id, f'class_{class_id}')),
                        confidence=confidence,
                        bbox=xyxy,
                        is_rare=False,
                        alert_level='none',
                    )
                )

        return DetectionResult(
            source_type=source_type,
            source_name=source_name,
            detections=detections,
            inference_time_ms=round(inference_time_ms, 2),
            result_path=str(result_path.as_posix()),
        )

    def detect_image(
        self,
        image_path: str | Path,
        weight_path: str | None = None,
        save_result: bool = True,
        source_name: str | None = None,
    ) -> DetectionResult:
        source_path = Path(image_path)
        resolved_source_name = source_name or source_path.name
        try:
            model = self._get_model(weight_path)
            self.logger.info('Running image detection on %s', source_path)
            results = model.predict(source=str(source_path), verbose=False)
            if not results:
                raise RuntimeError('No inference result returned for image.')
            result = results[0]
            output_path = build_output_path(self.settings.outputs_dir, resolved_source_name, self.settings.image_result_suffix)
            if save_result:
                plotted = result.plot()
                cv2.imwrite(str(output_path), plotted)
            return self._standardize_result(
                result=result,
                source_type='image',
                source_name=resolved_source_name,
                inference_time_ms=float(sum(result.speed.values())),
                result_path=output_path,
            )
        except Exception as exc:
            self.logger.exception('Image detection failed for %s', source_path)
            raise RuntimeError(f'Image detection failed: {exc}') from exc

    def detect_video(
        self,
        video_path: str | Path,
        weight_path: str | None = None,
        save_result: bool = True,
        source_name: str | None = None,
    ) -> DetectionResult:
        source_path = Path(video_path)
        resolved_source_name = source_name or source_path.name
        capture = cv2.VideoCapture(str(source_path))
        if not capture.isOpened():
            raise RuntimeError(f'Unable to open video file: {source_path}')

        writer = None
        frame_count = 0
        total_inference_ms = 0.0
        aggregated: dict[tuple[int, str], DetectionBox] = {}
        output_path = build_output_path(self.settings.outputs_dir, resolved_source_name, self.settings.video_result_suffix)

        try:
            model = self._get_model(weight_path)
            fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

            if save_result:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

            self.logger.info('Running video detection on %s', source_path)
            while True:
                success, frame = capture.read()
                if not success:
                    break

                results = model.predict(source=frame, verbose=False)
                if not results:
                    continue
                result = results[0]
                frame_count += 1
                total_inference_ms += float(sum(result.speed.values()))

                standardized = self._standardize_result(
                    result=result,
                    source_type='video',
                    source_name=resolved_source_name,
                    inference_time_ms=float(sum(result.speed.values())),
                    result_path=output_path,
                )
                for detection in standardized.detections:
                    aggregated[(detection.class_id, detection.class_name)] = detection

                if writer is not None:
                    writer.write(result.plot())

            if frame_count == 0:
                raise RuntimeError('No frames were processed from the video.')

            return DetectionResult(
                source_type='video',
                source_name=resolved_source_name,
                detections=list(aggregated.values()),
                inference_time_ms=round(total_inference_ms / frame_count, 2),
                result_path=str(output_path.as_posix()),
            )
        except Exception as exc:
            self.logger.exception('Video detection failed for %s', source_path)
            raise RuntimeError(f'Video detection failed: {exc}') from exc
        finally:
            capture.release()
            if writer is not None:
                writer.release()

    def start_camera_detection(self, camera_index: int | None = None, weight_path: str | None = None) -> dict[str, object]:
        if self._camera_running:
            return {'running': True, 'message': 'Camera detection is already running.'}

        resolved_index = self.settings.camera_index if camera_index is None else camera_index
        self._camera_stop_event.clear()
        self._camera_thread = threading.Thread(
            target=self._camera_worker,
            args=(resolved_index, weight_path),
            daemon=True,
        )
        self._camera_running = True
        self._camera_thread.start()
        self.logger.info('Camera detection started on index %s', resolved_index)
        return {'running': True, 'camera_index': resolved_index}

    def _camera_worker(self, camera_index: int, weight_path: str | None) -> None:
        capture = cv2.VideoCapture(camera_index)
        if not capture.isOpened():
            self.logger.error('Unable to open camera index %s', camera_index)
            self._camera_running = False
            return

        frame_counter = 0
        try:
            model = self._get_model(weight_path)
            output_path = self.settings.outputs_dir / self.settings.camera_result_name
            while not self._camera_stop_event.is_set():
                success, frame = capture.read()
                if not success:
                    time.sleep(0.1)
                    continue

                frame_counter += 1
                if frame_counter % max(self.settings.camera_frame_interval, 1) != 0:
                    continue

                results = model.predict(source=frame, verbose=False)
                if not results:
                    continue
                result = results[0]
                cv2.imwrite(str(output_path), result.plot())
                standardized = self._standardize_result(
                    result=result,
                    source_type='camera',
                    source_name=f'camera_{camera_index}',
                    inference_time_ms=float(sum(result.speed.values())),
                    result_path=output_path,
                )
                with self._camera_lock:
                    self._latest_camera_result = standardized
        except Exception:
            self.logger.exception('Camera detection thread stopped unexpectedly.')
        finally:
            capture.release()
            self._camera_running = False

    def stop_camera_detection(self) -> dict[str, object]:
        if not self._camera_running:
            return {'running': False, 'message': 'Camera detection is not running.'}

        self._camera_stop_event.set()
        if self._camera_thread is not None:
            self._camera_thread.join(timeout=2)
        self._camera_running = False
        self.logger.info('Camera detection stopped.')
        return {'running': False, 'message': 'Camera detection stopped successfully.'}

    def get_latest_camera_result(self) -> DetectionResult | None:
        with self._camera_lock:
            return self._latest_camera_result

    def get_camera_status(self) -> dict[str, object]:
        return {
            'running': self._camera_running,
            'has_result': self._latest_camera_result is not None,
        }
