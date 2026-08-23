import time
from datetime import datetime
import os

print("=" * 65)
print("PROJECT 4 - ANOMALY DETECTION")
print("=" * 65)

os.makedirs("logs", exist_ok=True)
log_path = "logs/anomaly_alerts.txt"

def log_alert(event_type, identity, details):
    timestamp = datetime.now().isoformat()
    alert_line = f"[ALERT] timestamp={timestamp} | identity={identity} | event_type={event_type} | details={details}"
    print(alert_line)
    with open(log_path, "a") as f:
        f.write(alert_line + "\n")

# =========================================================
# DETECTOR 1: API Call Volume Spike (>20 requests in 60s)
# =========================================================
class VolumeDetector:
    def __init__(self, threshold=20, window_seconds=60):
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.timestamps = []

    def record_request(self, identity):
        now = time.time()
        self.timestamps.append(now)
        # keep only timestamps within the window
        self.timestamps = [t for t in self.timestamps if now - t <= self.window_seconds]
        if len(self.timestamps) > self.threshold:
            log_alert(
                "API_VOLUME_SPIKE",
                identity,
                f"{len(self.timestamps)} requests within {self.window_seconds}s window (threshold: {self.threshold})"
            )
            return True
        return False

# =========================================================
# DETECTOR 2: Scope Change Between Consecutive Requests
# =========================================================
class ScopeChangeDetector:
    def __init__(self):
        self.last_scope = {}  # identity -> last known scope

    def record_request(self, identity, scope):
        if identity in self.last_scope and self.last_scope[identity] != scope:
            log_alert(
                "SCOPE_CHANGE",
                identity,
                f"scope changed from '{self.last_scope[identity]}' to '{scope}' between consecutive requests"
            )
            self.last_scope[identity] = scope
            return True
        self.last_scope[identity] = scope
        return False

# =========================================================
# DETECTOR 3: Token Reuse After Expiry
# =========================================================
class TokenReuseDetector:
    def __init__(self):
        self.expired_tokens = set()

    def mark_expired(self, token_id):
        self.expired_tokens.add(token_id)

    def record_token_use(self, identity, token_id):
        if token_id in self.expired_tokens:
            log_alert(
                "TOKEN_REUSE_AFTER_EXPIRY",
                identity,
                f"expired token '{token_id}' was used again"
            )
            return True
        return False

# =========================================================
# REPLAY PROJECT 3 ATTACKS AGAINST DETECTORS
# =========================================================

volume_detector = VolumeDetector()
scope_detector = ScopeChangeDetector()
token_detector = TokenReuseDetector()

print("\n--- SCENARIO 1: Replaying Volume Spike (simulating rapid injection attempts) ---")
for i in range(25):  # 25 requests simulate an attacker hammering the agent
    volume_detector.record_request(identity="attacker_session_001")

print("\n--- SCENARIO 2: Replaying Scope Change (simulating Agent Spoofing attack) ---")
scope_detector.record_request(identity="agent_B", scope="read:tickets")
scope_detector.record_request(identity="agent_B", scope="read:tickets")
scope_detector.record_request(identity="agent_B", scope="delete:users")  # spoofed escalation

print("\n--- SCENARIO 3: Replaying Token Reuse After Expiry (simulating refresh token replay) ---")
token_detector.mark_expired("old_refresh_token_v1")
token_detector.record_token_use(identity="agent_A", token_id="old_refresh_token_v1")

print(f"\n[LOGGED] All alerts saved to {log_path}")
print("\n[*] Anomaly detection test completed")