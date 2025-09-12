import time, json

from security.rule_engine import evaluate_login
from security.explainability import explain_result
from security.alerts import send_email_alert

DATA_FILE = "login_events.json"
processed_count = 0

while True:
    with open(DATA_FILE, "r") as f:
        events = json.load(f)

    # Process only new events
    new_events = events[processed_count:]
    for event in new_events:
        result = evaluate_login(event)
        send_email_alert(result)
        print(explain_result(result))
        processed_count += 1

    time.sleep(2)
