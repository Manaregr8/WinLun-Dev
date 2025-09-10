import time
import random
from security.rule_engine import evaluate_login

test_ips = ["106.219.231.25", "8.8.8.8", "1.1.1.1"]
devices = ["dev1", "dev2"]
browsers = ["Chrome", "firefox"]

def generate_event(user_id = "u1"):
    return{
        "user_id": user_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "ip": random.choice(test_ips),
        "device_id": random.choice(devices),
        "browser": random.choice(browsers)
    }

if __name__ == "__main__":
    for i in range(5):
        event = generate_event()
        result = evaluate_login(event)
        print(result)
        time.sleep(2)