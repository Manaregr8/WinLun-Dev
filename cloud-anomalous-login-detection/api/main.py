from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
import os

from security.rule_engine import evaluate_login  # ✅ import rule engine

app = FastAPI()

# Allow frontend (Streamlit) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "login_events.json"

# Ensure raw events file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


@app.post("/ingest")
async def ingest(request: Request):
    data = await request.json()
    data["timestamp"] = datetime.utcnow().isoformat()

    # ✅ Save raw event
    with open(DATA_FILE, "r+") as f:
        events = json.load(f)
        events.append(data)
        f.seek(0)
        json.dump(events, f, indent=2)

    # ✅ Run anomaly detection (this will also persist to login_results.json)
    result = evaluate_login(data)

    return {"status": "success", "event": data, "evaluation": result}


@app.get("/events")
async def get_events():
    """Fetch stored login events"""
    with open(DATA_FILE, "r") as f:
        events = json.load(f)
    return {"events": events}


@app.get("/results")
async def get_results():
    """Fetch evaluated login results"""
    results_file = "login_results.json"
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            results = json.load(f)
    else:
        results = []
    return {"results": results}
