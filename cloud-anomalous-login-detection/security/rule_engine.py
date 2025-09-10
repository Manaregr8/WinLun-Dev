from datetime import datetime
from geopy.distance import geodesic
from security.geoip_enrich import ip_to_geo

# In-memory store of last logins
user_last_login = {}

def evaluate_login(event: dict) -> dict:
    """
    Evaluate a login event with anomaly rules.
    event = {
        "user_id": str,
        "timestamp": str (ISO format),
        "ip": str,
        "device_id": str,
        "browser": str
    }
    """
    user_id = event["user_id"]
    reasons = []
    risk = 0

    # Enrich with geo info
    geo = ip_to_geo(event["ip"])
    event["geo"] = geo
    now = datetime.fromisoformat(event["timestamp"])

    last = user_last_login.get(user_id)

    if last:
        # Impossible travel
        try:
            dist = geodesic(
                (last["geo"]["latitude"], last["geo"]["longitude"]),
                (geo["latitude"], geo["longitude"])
            ).km
            time_diff = (now - last["timestamp"]).total_seconds() / 3600.0
            if time_diff > 0 and dist / time_diff > 800:  # ~plane speed
                risk += 50
                reasons.append(f"Impossible travel: {dist:.0f} km in {time_diff:.2f} hr")
        except Exception:
            pass

        # New device
        if event["device_id"] != last["device_id"]:
            risk += 20
            reasons.append("New device detected")

        # New browser
        if event["browser"] != last["browser"]:
            risk += 10
            reasons.append("New browser detected")

    # Odd login hour
    if now.hour < 5 or now.hour > 23:
        risk += 15
        reasons.append("Unusual login time")

    # New country
    if last and geo["country"] != last["geo"]["country"]:
        risk += 30
        reasons.append(f"New country: {geo['country']}")

    # Save last login
    user_last_login[user_id] = {
        "geo": geo,
        "timestamp": now,
        "device_id": event["device_id"],
        "browser": event["browser"],
    }

    return {
        "user_id": user_id,
        "risk_score": min(risk, 100),
        "reasons": reasons or ["No anomalies detected"],
        "geo": geo,
    }
