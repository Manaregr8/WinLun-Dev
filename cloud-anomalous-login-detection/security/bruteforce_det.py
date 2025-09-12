import time
import threading 
from collections import defaultdict, deque

#configurations
USER_FAIL_TTL = 60 * 60        # 1 hour window for user fails
IP_FAIL_TTL = 60 * 60
USER_IP_TTL = 30 * 60
LOCK_TTL = 15 * 60
USER_FAIL_THRESHOLD = 2
IP_FAIL_THRESHOLD = 50
CREDENTIAL_STUFFING_THRESHOLD = 20 

# In-memory stores , these will be replaced by redis in prod 
_user_failures = defaultdict(deque)   # user_id -> deque of timestamps
_ip_failures = defaultdict(deque)     # ip -> deque of timestamps
_user_ip_failures = defaultdict(deque) # (user,ip) -> deque
_user_locks = {}                       # user_id -> lock_expiry_ts
_ip_user_set = defaultdict(set)        # ip -> set(users seen) for stuffing detection

_lock = threading.Lock()

def trim_deque(dq, win_sec):
    current_time = time.time()
    while dq and (current_time - dq[0]) > win_sec:
        dq.popleft()

def record_failed_login(user_id: str, ip: str):
    now = time.time()
    key_ui = (user_id, ip)
    with _lock:
        _user_failures[user_id].append(now)
        _ip_failures[ip].append(now)
        _user_ip_failures[key_ui].append(now)
        _ip_user_set[ip].add(user_id)

        # Trim
        trim_deque(_user_failures[user_id], USER_FAIL_TTL)
        trim_deque(_ip_failures[ip], IP_FAIL_TTL)
        trim_deque(_user_ip_failures[key_ui], USER_IP_TTL)

def get_bruteforce_status(user_id: str, ip: str):
    now = time.time()
    with _lock:
        # Remove aged entries
        trim_deque(_user_failures[user_id], USER_FAIL_TTL)
        trim_deque(_ip_failures[ip], IP_FAIL_TTL)

        ucount = len(_user_failures[user_id])
        icount = len(_ip_failures[ip])
        distinct_users = len(_ip_user_set[ip])

        locked_until = _user_locks.get(user_id, 0)
        locked = locked_until > now

    return {
        "user_fail_count": ucount,
        "ip_fail_count": icount,
        "distinct_users_from_ip": distinct_users,
        "user_locked": locked,
        "lock_expires_at": locked_until if locked else None
    }


def lock_user(user_id: str, duration: int = LOCK_TTL):
    with _lock:
        _user_locks[user_id] = time.time() + duration

def unlock_user_if_expired(user_id: str):
    with _lock:
        if user_id in _user_locks and _user_locks[user_id] <= time.time():
            del _user_locks[user_id]

def should_take_action(user_id: str, ip: str):
    status = get_bruteforce_status(user_id, ip)
    reasons = []
    score = 0
    if status["user_locked"]:
        reasons.append("User temporarily locked")
        score += 90
    if status["user_fail_count"] >= USER_FAIL_THRESHOLD:
        reasons.append(f"Multiple failed login attempts for user ({status['user_fail_count']})")
        score += 80
    if status["ip_fail_count"] >= IP_FAIL_THRESHOLD:
        reasons.append(f"High number of failed attempts from IP ({status['ip_fail_count']})")
        score += 60
    if status["distinct_users_from_ip"] >= CREDENTIAL_STUFFING_THRESHOLD:
        reasons.append("IP attempting many different users (credential stuffing)")
        score += 70
    return score, reasons

