import time
import random
from security.rule_engine import evaluate_login
from security.explainability import explain_result
from security.alerts import send_email_alert
from datetime import datetime, timezone

from security.bruteforce_det import (
    record_failed_login,
    should_take_action,
    lock_user,
    get_bruteforce_status,
    unlock_user_if_expired,
)

test_ips = ["106.219.231.25", "8.8.8.8", "1.1.1.1"]
devices = ["dev1", "dev2"]
browsers = ["Chrome", "firefox"]

FAIL_PROBABILITY = 0.9  # probability each generated login is an authentication FAILURE (for demo)
LOCK_ON_SCORE_THRESHOLD = 70
SEND_EMAIL_ON_LOCK = True  # sends email if set as true

def generate_event(user_id = "u1"):
    return{
        "user_id": user_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ip": random.choice(test_ips),
        "device_id": random.choice(devices),
        "browser": random.choice(browsers)
    }

def simulate_auth(user_id: str) -> bool:    # this will be replaced with the auth logic that i get from frontend after thats done.
    return random.random() > FAIL_PROBABILITY

def handle_failed_login(user_id: str, ip: str):
    
    record_failed_login(user_id, ip)
    bf_score, bf_reasons = should_take_action(user_id, ip)

    if bf_score > LOCK_ON_SCORE_THRESHOLD:
        lock_user(user_id)

        if SEND_EMAIL_ON_LOCK:
            try:
                # send_email_alert expects a result dict; we build a simple one
                alert_payload = {
                    "user_id": user_id,
                    "risk_score": bf_score,
                    "reasons": bf_reasons,
                }
                send_email_alert(alert_payload)
            except Exception as e:
                # ignore email errors for demo purpose, will handle them in prod
                print("Warning: send_email_alert failed:", e)

        status = get_bruteforce_status(user_id, ip)
        expires_at = status.get("lock_expires_at", 0) or 0
        remaining = int(expires_at - time.time()) if expires_at else None
        result = {
            "status": "locked_now",
            "message": "User temporarily locked due to repeated failed logins",
            "lock_expires_in_seconds": remaining,
            "risk_score": bf_score,
            "reasons": bf_reasons,
        }
        print(explain_result(result))
        return result
    
    result = {
        "status": "failed", 
        "message": "Invalid credentials", 
        "risk_score": bf_score, 
        "reasons": bf_reasons
    }

    print(explain_result(result))
    return result

def simulate_and_process_event(event: dict):
    """
    FLOW:
      - unlock expired locks
      - check lock status
      - simulate auth
      - record failures / lock if needed
      - on success: run evaluate_login(), print explanation
    """
    user_id = event["user_id"]
    ip = event["ip"]

    # auto-unlock expired locks (time-based)
    unlock_user_if_expired(user_id)

    # check lock
    status = get_bruteforce_status(user_id, ip)
    if status.get("user_locked"):
        expires_at = status.get("lock_expires_at", 0) or 0
        remaining = int(expires_at - time.time()) if expires_at else None
        result = {
            "status": "locked",
            "user_id": user_id,
            "message": "Account locked",
            "lock_expires_in_seconds": remaining,
            "risk_score": 100,  # force high score for clarity
            "reasons": ["Account is currently locked due to repeated failed logins"],
        }
        print(explain_result(result))
        return

    # simulate authentication (demo)
    auth_success = simulate_auth(user_id)

    if not auth_success:
        resp = handle_failed_login(user_id, ip)
        try:
            print(f"[{datetime.now(timezone.utc).isoformat()}] FAILED LOGIN for user={user_id} ip={ip} ->")
            print(explain_result(resp))
        except Exception:
            # fallback to raw print if explain_result fails for any reason
            print(f"[{datetime.now(timezone.utc).isoformat()}] FAILED LOGIN for user={user_id} ip={ip} ->", resp)
        return

    result = evaluate_login(event)
    print(f"[{datetime.now(timezone.utc).isoformat()}] SUCCESSFUL LOGIN for user={user_id} ip={ip} ->")
    try:
        print(explain_result(result))
    except Exception:
        print(result)

if __name__ == "__main__":
    for i in range(5):
        event = generate_event()
        simulate_and_process_event(event)
        # result = evaluate_login(event)
        # send_email_alert(result)
        # print(explain_result(result))
        time.sleep(2)