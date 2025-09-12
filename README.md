# AI for Detecting Anomalous Logins in Cloud Environments

## Overview
With the rise of remote work and cloud services, attackers increasingly use stolen credentials to log in from unusual locations, devices, or times. Traditional security systems often fail to detect such subtle anomalies.  
This project provides an **AI/ML-powered anomaly detection system** that analyzes login patterns (geo-location, device fingerprinting, login time, and behavioral features) to detect, flag, and alert suspicious logins in real-time.

Built during a hackathon, the solution is designed for **fast prototyping**, **hackathon demo readiness**, and **practical real-world extension**.

---

## Problem Statement
- Detect anomalous logins in cloud environments where attackers use stolen credentials.
- Analyze login events for unusual behavior such as:
  - Impossible travel (geo-location anomalies).
  - Suspicious device fingerprints.
  - Odd login times.
  - Behavior deviating from user baseline.
- Flag anomalies without disrupting legitimate users.

---

## Solution
Our system combines **synthetic data generation, ML-based anomaly detection, and real-time alerting**:

1. **Synthetic Dataset Generator** – creates realistic login events (IP, geo-location, device, login time, user activity).
2. **Feature Engineering** – converts raw login logs into numerical features.
3. **ML Models**  
   - Isolation Forest (scikit-learn)  
   - Autoencoder (PyTorch)  
   - Ensemble scoring for robustness
4. **Real-Time Processing** – login events pushed via API → queued → scored by worker.
5. **Dashboard & Alerts** – anomalies visualized, alerts triggered for suspicious logins.

---

## System Architecture

```text
                      +----------------------+
                      |  Cloud Applications  |
                      +----------+-----------+
                                 |
                                 v
                      +----------------------+
                      |      API (FastAPI)   |
                      +----------+-----------+
                                 |
                                 v
                        +----------------+
                        |   Redis Queue   |
                        +--------+--------+
                                 |
                                 v
                +---------------------------------------+
                |        Worker (Scoring Engine)        |
                |---------------------------------------|
                |  - Feature extraction                 |
                |  - Rule-based checks                  |
                |  - Isolation Forest model             |
                |  - Autoencoder (PyTorch)              |
                |  - Ensemble scoring (final risk)      |
                +----------------+----------------------+
                                 |
               +-----------------+-------------------+
               |                                     |
               v                                     v
     +---------------------+              +----------------------+
     | Alerts & Dashboard  |              |    Audit Logs        |
     +---------------------+              +----------------------+


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



