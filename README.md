# AI for Detecting Anomalous Logins in Cloud Environments

## Overview
With the rise of remote work and cloud services, attackers increasingly use stolen credentials to log in from unusual locations, devices, or times. Traditional security systems often fail to detect such subtle anomalies.  
This project provides an **AI/ML-powered anomaly detection system** that analyzes login patterns (geo-location, device fingerprinting, login time, and behavioral features) to detect, flag, and alert suspicious logins in real-time.

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
                        |   Redis Queue  |
                        | (in-memory     |
                        | store for demo)|               
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
```

### Features
- User and Entity Behavioral Analytics (UEBA): Tracks user logins, devices, IP addresses, and activity rates over time to profile typical behavior.
- Anomaly Detection Engine: Flags logins deviating from established baselines, e.g., impossible travel, risky IPs, multiple failed attempts, and unusual device/location access.
- Machine Learning Support: Implements and benchmarks algorithms like Logistic Regression, Random Forest, SVMs, and Neural Networks for login risk prediction.
- Customizable Alerts: Triggers security notifications for anomalous login events based on configurable thresholds.
- Scalable Architecture: Designed for cloud environments with support for integration into major cloud security platforms.
- Sample Dataset & Notebooks: Includes datasets simulating real login scenarios and Jupyter notebooks for model analysis.

### Dataset Structure
#### Each login record should contain:
- User ID
- Timestamp
- Login Status (success/failure)
- IP Address
- Device Type
- Location
- Session Duration
- Failed Attempts
- Behavioral Score

### FLOW
 - user tries to log in (in a malicious way)
 - Problem 1 -> they try to bruteforce and  to bypass the rate limitations.
 - Solution -> bruteforce is detected by the AI and the rule engine, the score is averaged and an accurate call is made to lock the user out, now even if they enter the correct password in their 100th attempt (for example), they cant log in
 - problem 2 -> they randomly try to attempt a login from there device and a foreign location or maybe they have a vpn enabled so that they dont get caught. 
 - Solution -> The rule engine and the AI detects this in 3 ways currently (will be scaled and strengthened to add more mechanisms)
      - 1> impossible travel : legit user logs in from New Delhi,india but the malicious one tries to log in from a very diff location like chicago or maybe from somewhere in meghalaya.
      - 2> Different Device: User logs in daily from his cute little samsung but the hacker tries to log in with the big bold IPhone suddenly
      - 3> Unusual Time: User sleeps at night because no one wants to log in at nights to work on the cloud but someone leverages this and tries to get in around this time

    In all these cases, the user gets an email which flags this malicious intent (everything is shown in the video as POC).



