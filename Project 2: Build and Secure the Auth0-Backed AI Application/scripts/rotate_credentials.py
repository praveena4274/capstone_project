"""
Credential rotation evidence script.

1. Requests an M2M access token via client_credentials (make sure the API's
   'Token Expiration (For Access Tokens)' is set to 60 seconds in the Auth0
   dashboard so this actually expires).
2. Calls GET /chat with it -> expect 200 OK.
3. Sleeps past the 60s TTL.
4. Replays the SAME token -> expect 401 Unauthorized.

All output is timestamped and also written to rotation_log.txt so you have
a file you can screenshot / attach as evidence.
"""
import os
import sys
import time
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUDIENCE = os.environ["AUTH0_AUDIENCE"]
M2M_CLIENT_ID = os.environ["M2M_CLIENT_ID"]
M2M_CLIENT_SECRET = os.environ["M2M_CLIENT_SECRET"]
CHAT_URL = f"http://localhost:{os.environ.get('API_PORT', 5000)}/chat"

LOG_FILE = "rotation_log.txt"


def log(msg):
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_m2m_token():
    resp = requests.post(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        json={
            "grant_type": "client_credentials",
            "client_id": M2M_CLIENT_ID,
            "client_secret": M2M_CLIENT_SECRET,
            "audience": AUDIENCE,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    log(f"Obtained M2M token. expires_in={data.get('expires_in')}s")
    return data["access_token"]


def call_chat(token):
    resp = requests.get(CHAT_URL, headers={"Authorization": f"Bearer {token}"})
    log(f"GET /chat -> {resp.status_code} {resp.text}")
    return resp.status_code


def main():
    open(LOG_FILE, "a").close()
    log("=== Credential rotation test start ===")

    token = get_m2m_token()

    log("Calling /chat with FRESH token...")
    status1 = call_chat(token)
    assert status1 == 200, f"Expected 200 on first call, got {status1}"

    wait_seconds = 65  # a few seconds beyond the 60s TTL to be safe
    log(f"Sleeping {wait_seconds}s to let the token expire...")
    time.sleep(wait_seconds)

    log("Replaying the SAME (now expired) token...")
    status2 = call_chat(token)
    assert status2 == 401, f"Expected 401 on replay, got {status2}"

    log("=== Result: fresh token -> 200 OK, expired replay -> 401 Unauthorized. PASS ===")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        log(f"TEST FAILED: {e}")
        sys.exit(1)