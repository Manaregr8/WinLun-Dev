# Cloud Anomalous Login Detection

## Overview
This project is designed to detect anomalous login activities in cloud-based applications by leveraging a combination of rules, machine learning, and deep learning models. The system ingests login events, processes them through a scoring pipeline, and assigns risk levels that determine whether the login should be allowed, challenged (MFA), or blocked.

The detection system uses:
- Rule-based checks (impossible travel, unusual login times, device changes).
- Isolation Forest for unsupervised anomaly detection.
- PyTorch Autoencoder for reconstruction-based anomaly detection.
- Ensemble scoring for final risk classification.

---

## System Architecture
---
cloud-anomalous-login-detection/
├─ api/ # FastAPI service
│ └─ main.py
├─ worker/ # Feature extraction & scoring engine
│ ├─ features.py
│ ├─ train_if.py
│ ├─ train_ae_pytorch.py
│ ├─ ensemble.py
│ ├─ eval.py
│ └─ worker.py
├─ data/
│ └─ generate_synthetic.py
├─ models/ # Trained artifacts (created after training)
│ ├─ isolation_forest.joblib
│ ├─ autoencoder.pth
│ ├─ scaler.pkl
│ ├─ if_stats.json
│ └─ ae_stats.json
├─ scripts/
│ └─ send_event.py # Replay synthetic events
├─ reports/ # Evaluation charts
├─ requirements.txt
└─ README.md
---


---

## Tech Stack

- **Backend:** FastAPI, Redis, Docker/Docker Compose  
- **ML/DL:** Scikit-learn (Isolation Forest), PyTorch (Autoencoder)  
- **Data:** Synthetic dataset generator  
- **Visualization:** Matplotlib for reports, optional Streamlit dashboard  
- **Packaging:** Joblib, Torch `.pth` models, JSON statistics  

---

## Setup and Installation

Clone the repository:
```bash
git clone https://github.com/<your-org>/cloud-anomalous-login-detection.git
cd cloud-anomalous-login-detection

python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell


