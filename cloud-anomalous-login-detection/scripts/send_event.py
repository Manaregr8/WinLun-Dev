import time
import requests
from datetime import datetime, timezone
from pprint import pprint
from hashlib import sha1

from security.rule_engine import evaluate_login
from security.explainability import explain_result
from security.alerts import send_email_alert

from security.bruteforce_det import (
    record_failed_login,
    should_take_action,
    lock_user,
    get_bruteforce_status,
    unlock_user_if_expired,
)

API_URL = "http://localhost:8000"
POLL_INTERVAL_SECONDS = 3
AUTH_DEMO_PASSWORD = "test123"  # demo password that counts as successful login
LOCK_ON_SCORE_THRESHOLD = 70
SEND_EMAIL_ON_LOCK = True

# -------------------------
# Helpers
# -------------------------
def event_fingerprint(ev: dict) -> str:
    """
    Create a compact fingerprint for an event (used to dedupe).
    Uses user_id|timestamp|ip — adjust if your events have other unique keys.
    """
    key = f"{ev.get('user_id','')}|{ev.get('timestamp','')}|{ev.get('ip','')}"
    return sha1(key.encode()).hexdigest()

def normalize_result_for_explain(r: dict) -> dict:
    """
    Ensure result dict has canonical keys explain_result expects:
    - risk_score (int)
    - reasons (list)
    """
    out = dict(r)  # shallow copy
    # unify risk_score under key 'risk_score'
    out["risk_score"] = out.get("risk_score", out.get("risk", out.get("score", 0)))
    # unify reasons list
    if "reasons" not in out:
        out["reasons"] = out.get("explanations", out.get("reason", [])) or []
    return out

# -------------------------
# Brute-force handling (no direct printing here)
# -------------------------
def handle_failed_login(user_id: str, ip: str):
    """
    Record failure and return a normalized result dict.
    This function DOES NOT print; caller should print exactly once.
    """
    record_failed_login(user_id, ip)
    bf_score, bf_reasons = should_take_action(user_id, ip)

    if bf_score >= LOCK_ON_SCORE_THRESHOLD:
        lock_user(user_id)
        if SEND_EMAIL_ON_LOCK:
            try:
                alert_payload = {
                    "user_id": user_id,
                    "risk_score": bf_score,
                    "reasons": bf_reasons,
                }
                send_email_alert(alert_payload)
            except Exception as e:
                print("Warning: send_email_alert failed:", e)

        status = get_bruteforce_status(user_id, ip)
        expires_at = status.get("lock_expires_at", 0) or 0
        remaining = int(expires_at - time.time()) if expires_at else None
        return {
            "status": "locked_now",
            "user_id": user_id,
            "message": "User temporarily locked due to repeated failed logins",
            "lock_expires_in_seconds": remaining,
            "risk_score": bf_score,
            "reasons": bf_reasons,
        }

    return {
        "status": "failed",
        "user_id": user_id,
        "message": "Invalid credentials",
        "risk_score": bf_score,
        "reasons": bf_reasons,
    }

# -------------------------
# Event processing
# -------------------------
def simulate_auth_using_event(event: dict) -> bool:
    """
    Demo auth check: deterministic. Replace this with real auth call later.
    If frontend includes a password field:
      success if event['password'] == AUTH_DEMO_PASSWORD
    Otherwise, treat as success (or change logic as needed).
    """
    if "password" in event:
        return event.get("password") == AUTH_DEMO_PASSWORD
    # default: treat as success (you can change to False if you want failures)
    return True

def simulate_and_process_event(event: dict):
    """
    Process a single raw event and print exactly one explain_result output.
    """
    user_id = event.get("user_id")
    ip = event.get("ip")

    # 1) auto-unlock expired locks
    unlock_user_if_expired(user_id)

    # 2) check locked status
    status = get_bruteforce_status(user_id, ip)
    if status.get("user_locked"):
        expires_at = status.get("lock_expires_at", 0) or 0
        remaining = int(expires_at - time.time()) if expires_at else None
        raw = {
            "status": "locked",
            "user_id": user_id,
            "message": "Account locked",
            "lock_expires_in_seconds": remaining,
            "risk_score": 100,
            "reasons": ["Account is currently locked due to repeated failed logins"],
            "geo": event.get("geo", {}),
        }
        norm = normalize_result_for_explain(raw)
        print(f"[{datetime.now(timezone.utc).isoformat()}] LOCKED event for user={user_id} ip={ip}")
        print(explain_result(norm))
        return

    # 3) auth check (deterministic for demo)
    auth_success = simulate_auth_using_event(event)

    if not auth_success:
        resp = handle_failed_login(user_id, ip)
        norm = normalize_result_for_explain(resp)
        print(f"[{datetime.now(timezone.utc).isoformat()}] FAILED LOGIN for user={user_id} ip={ip} ->")
        print(explain_result(norm))
        return

    # 4) success path: call evaluate_login and print explanation once
    result = evaluate_login(event)
    # normalize keys so explain_result always has what's expected
    norm = normalize_result_for_explain(result)
    print(f"[{datetime.now(timezone.utc).isoformat()}] SUCCESSFUL LOGIN for user={user_id} ip={ip} ->")
    # optional: show raw for debugging
    # pprint(result)
    print(explain_result(norm))

# -------------------------
# Fetcher + Poller (dedupe + last_index)
# -------------------------
def fetch_events():
    r = requests.get(f"{API_URL}/events")
    r.raise_for_status()
    return r.json().get("events", [])

def run_polling_loop(poll_interval=POLL_INTERVAL_SECONDS):
    print("Starting event poller. Polling", API_URL + "/events")
    last_index = 0
    seen = set()
    try:
        while True:
            events = fetch_events()
            if not isinstance(events, list):
                print("Unexpected /events payload:", type(events))
                time.sleep(poll_interval)
                continue

            new_events = events[last_index:]
            if new_events:
                print(f"[{datetime.now(timezone.utc).isoformat()}] Found {len(new_events)} new event(s). Processing...")
            for ev in new_events:
                fp = event_fingerprint(ev)
                if fp in seen:
                    # already processed this exact event — skip
                    continue
                try:
                    simulate_and_process_event(ev)
                except Exception as e:
                    print("Error processing event:", e)
                seen.add(fp)
                time.sleep(0.5)

            last_index = len(events)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("Poller stopped by user.")

if __name__ == "__main__":
    run_polling_loop()


# some part of the code below is for simulated logins that i have shown in the readme file, the above one is for bruteforcing.



# import time
# import random
# from security.rule_engine import evaluate_login
# from security.explainability import explain_result
# from security.alerts import send_email_alert
# from datetime import datetime, timezone
# import requests

# from security.bruteforce_det import (
#     record_failed_login,
#     should_take_action,
#     lock_user,
#     get_bruteforce_status,
#     unlock_user_if_expired,
# )

# test_ips = ["106.219.231.25", "8.8.8.8", "1.1.1.1"]
# devices = ["dev1", "dev2"]
# browsers = ["Chrome", "firefox"]

# API_URL = "http://localhost:8000"

# FAIL_PROBABILITY = 0.8  # probability each generated login is an authentication FAILURE (for demo)
# LOCK_ON_SCORE_THRESHOLD = 70
# SEND_EMAIL_ON_LOCK = False  # sends email if set as true

# def generate_event(user_id = "u1"):
#     return{
#         "user_id": user_id,
#         "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
#         "ip": random.choice(test_ips),
#         "device_id": random.choice(devices),
#         "browser": random.choice(browsers)
#     }

# def simulate_auth(user_id: str) -> bool:    # this will be replaced with the auth logic that i get from frontend after thats done.
#     return random.random() > FAIL_PROBABILITY

# def handle_failed_login(user_id: str, ip: str):
    
#     record_failed_login(user_id, ip)
#     bf_score, bf_reasons = should_take_action(user_id, ip)

#     if bf_score > LOCK_ON_SCORE_THRESHOLD:
#         lock_user(user_id)

#         if SEND_EMAIL_ON_LOCK:
#             try:
#                 # send_email_alert expects a result dict; we build a simple one
#                 alert_payload = {
#                     "user_id": user_id,
#                     "risk_score": bf_score,
#                     "reasons": bf_reasons,
#                 }
#                 send_email_alert(alert_payload)
#             except Exception as e:
#                 # ignore email errors for demo purpose, will handle them in prod
#                 print("Warning: send_email_alert failed:", e)

#         status = get_bruteforce_status(user_id, ip)
#         expires_at = status.get("lock_expires_at", 0) or 0
#         remaining = int(expires_at - time.time()) if expires_at else None
#         result = {
#             "status": "locked_now",
#             "message": "User temporarily locked due to repeated failed logins",
#             "lock_expires_in_seconds": remaining,
#             "risk_score": bf_score,
#             "reasons": bf_reasons,
#         }
#         # print(explain_result(result))
#         return result
    
#     result = {
#         "status": "failed", 
#         "message": "Invalid credentials", 
#         "risk_score": bf_score, 
#         "reasons": bf_reasons
#     }

#     # print(explain_result(result))
#     return result

# def simulate_and_process_event(event: dict):
#     """
#     FLOW:
#       - unlock expired locks
#       - check lock status
#       - simulate auth
#       - record failures / lock if needed
#       - on success: run evaluate_login(), print explanation
#     """
#     user_id = event["user_id"]
#     ip = event["ip"]

#     # auto-unlock expired locks (time-based)
#     unlock_user_if_expired(user_id)

#     # check lock
#     status = get_bruteforce_status(user_id, ip)
#     if status.get("user_locked"):
#         expires_at = status.get("lock_expires_at", 0) or 0
#         remaining = int(expires_at - time.time()) if expires_at else None
#         result = {
#             "status": "locked",
#             "user_id": user_id,
#             "message": "Account locked",
#             "lock_expires_in_seconds": remaining,
#             "risk_score": 100,  # force high score for clarity
#             "reasons": ["Account is currently locked due to repeated failed logins"],
#         }
#         return result

#     # simulate authentication (demo)
#     auth_success = simulate_auth(user_id)

#     if not auth_success:
#         resp = handle_failed_login(user_id, ip)
#         try:
#             print(f"[{datetime.now(timezone.utc).isoformat()}] FAILED LOGIN for user={user_id} ip={ip} ->")
#             print(explain_result(resp))
#         except Exception:
#             # fallback to raw print if explain_result fails for any reason
#             print(f"[{datetime.now(timezone.utc).isoformat()}] FAILED LOGIN for user={user_id} ip={ip} ->", resp)
#         return

#     result = evaluate_login(event)
#     print(f"[{datetime.now(timezone.utc).isoformat()}] SUCCESSFUL LOGIN for user={user_id} ip={ip} ->")
#     try:
#         print(explain_result(result))
#     except Exception:
#         print(result)