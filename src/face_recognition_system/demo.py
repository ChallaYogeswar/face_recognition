from __future__ import annotations

import argparse

import cv2
import numpy as np

from .config import RecognitionConfig
from .identity_store import IdentityStore
from .pipeline import FaceRecognitionPipeline


def build_demo_identity_store() -> IdentityStore:
    rng = np.random.default_rng(42)
    store = IdentityStore()
    store.add_identity("Alice", rng.normal(0.0, 1.0, size=(128,)))
    store.add_identity("Bob", rng.normal(0.0, 1.0, size=(128,)))
    return store


def run_image_demo(image_path: str) -> None:
    config = RecognitionConfig(threshold=0.5)
    pipeline = FaceRecognitionPipeline(config=config)
    store = build_demo_identity_store()
    for name, emb in store.as_dict().items():
        pipeline.add_identity(name, emb)

    frame = cv2.imread(image_path)
    if frame is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    detections = pipeline.process_frame(frame)
    for detection in detections:
        x, y, w, h = detection.bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        label = f"{detection.identity} {detection.confidence:.2f}"
        cv2.putText(frame, label, (x, max(y - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Face recognition demo", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def run_camera_demo(camera_id: int = 0) -> None:
    config = RecognitionConfig(threshold=0.5)
    pipeline = FaceRecognitionPipeline(config=config)
    store = build_demo_identity_store()
    for name, emb in store.as_dict().items():
        pipeline.add_identity(name, emb)

    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open camera {camera_id}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        detections = pipeline.process_frame(frame)
        for detection in detections:
            x, y, w, h = detection.bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"{detection.identity} {detection.confidence:.2f}"
            cv2.putText(frame, label, (x, max(y - 10, 0)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Face recognition demo", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser(description="Face recognition demo")
    parser.add_argument("--image", type=str, default=None, help="Path to image file for a one-shot demo")
    parser.add_argument("--camera", type=int, default=None, help="Camera index for live webcam demo")
    args = parser.parse_args()

    if args.image:
        run_image_demo(args.image)
    elif args.camera is not None:
        run_camera_demo(args.camera)
    else:
        print("No input selected. Use --image or --camera.")


if __name__ == "__main__":
    main()
