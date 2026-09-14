# Face Recognition System

This project turns the design notes from `codes.md` into a runnable Python prototype for:

- a face detection and recognition pipeline
- a small identity database with similarity-based matching
- agent orchestration for camera, privacy, alert, and monitoring tasks
- a CLI demo that can run on a webcam or a static image

## Project layout

- `src/face_recognition/` - core Python package
- `scripts/` - lightweight runner scripts
- `requirements.txt` - Python dependencies

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=src python -m face_recognition.demo --image path/to/image.jpg
```

You can also run the webcam demo:

```bash
PYTHONPATH=src python -m face_recognition.demo --camera 0
```

## Notes

This is a production-ready prototype skeleton based on the design specification. It uses OpenCV Haar cascades as the default detector and a normalized feature-vector fallback embedding for prototype recognition when a trained face model is not available.

The architecture is designed so the recognition model can be swapped with FaceNet, ArcFace, or an ONNX runtime model without changing the orchestration logic.
