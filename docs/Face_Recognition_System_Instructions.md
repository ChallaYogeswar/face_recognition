Perfect — I’ve read through both uploaded design specification files. Let’s start by drafting **clear instructions for AI and AI agents** based on the Face Recognition System design. These will serve as the foundation before we move into implementation or code generation.

---

## 🧠 AI Instructions (Core Intelligence Layer)
These define how the **AI model** itself should behave:
- **Recognition Pipeline**
  - Preprocess input frames (resize, normalize, enhance).
  - Detect faces using CNN-based detector (multi-scale, multi-camera).
  - Extract embeddings with a trained deep learning model (e.g., FaceNet, ArcFace).
  - Compare embeddings against secure database using cosine similarity.
- **Privacy & Security**
  - Encrypt embeddings before storage.
  - Apply anonymization when logging events.
  - Respect configurable retention policies.
- **Performance**
  - Optimize inference for edge devices (quantization, pruning).
  - Support real-time recognition (<200ms latency per frame).
- **Adaptability**
  - Allow retraining with new datasets.
  - Support incremental learning for new identities.

---

## 🤖 AI Agent Instructions (System Orchestration Layer)
These define how **agents** coordinate tasks across cameras, edge devices, and backend:
- **Camera Agents**
  - Capture streams from multiple cameras.
  - Perform local preprocessing to reduce bandwidth.
  - Forward frames to recognition AI or edge inference module.
- **Edge Agents**
  - Run lightweight recognition models locally.
  - Sync results with central server periodically.
  - Handle offline mode with local caching.
- **Privacy Agents**
  - Enforce GDPR/Indian IT Act compliance.
  - Manage consent and audit logs.
  - Mask faces when required by policy.
- **Alert Agents**
  - Trigger notifications when unknown or blacklisted faces are detected.
  - Integrate with external systems (SMS, email, IoT alarms).
- **Database Agents**
  - Manage secure storage of embeddings and metadata.
  - Handle replication and backups.
- **Monitoring Agents**
  - Track system health (latency, accuracy, uptime).
  - Auto-scale resources when demand spikes.

---
