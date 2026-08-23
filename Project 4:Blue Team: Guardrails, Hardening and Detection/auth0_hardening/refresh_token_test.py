import requests
import json
from datetime import datetime

print("=" * 65)
print("PROJECT 4 - AUTH0 REFRESH TOKEN ROTATION TEST")
print("=" * 65)

DOMAIN = "dev-5xje8qnp14disgar.us.auth0.com"          # replace
CLIENT_ID = "WCo7fzaZQkrHLNHBz69NlGmBLP5LylCH"                  # replace
CLIENT_SECRET = "ZvjceYdmuiH0VXFwdMfeXkY7Yb8muzLXgC-C1YiSIcdnRHzQLOQ0TYtSTxFvdAst"          # replace
AUDIENCE = "https://Project4-Agent-API"              # replace, e.g. https://project4-agent-api
USERNAME = "project4screenshot@gmail.com"               # replace
PASSWORD = "project4screenshot"                     # replace

token_url = f"https://{DOMAIN}/oauth/token"

log_path = "logs/refresh_token_test.txt"
import os
os.makedirs("logs", exist_ok=True)

def log(entry):
    with open(log_path, "a") as f:
        f.write(entry + "\n")

# --- Step 1: Get initial access + refresh token via Password grant ---
print("\n[*] Requesting initial tokens (Password grant)...")
resp1 = requests.post(token_url, json={
    "grant_type": "http://auth0.com/oauth/grant-type/password-realm",
    "username": USERNAME,
    "password": PASSWORD,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "audience": AUDIENCE,
    "scope": "offline_access",
    "realm": "Username-Password-Authentication"
})
data1 = resp1.json()
print(f"[*] Status: {resp1.status_code}")
log(f"Timestamp: {datetime.now().isoformat()}")
log(f"Initial token request status: {resp1.status_code}")

if "refresh_token" not in data1:
    print("[ERROR] No refresh_token returned. Check that 'offline_access' scope and Refresh Token grant are enabled.")
    print(json.dumps(data1, indent=2))
    log(f"ERROR: {json.dumps(data1)}")
    exit()

old_refresh_token = data1["refresh_token"]
print(f"[*] Refresh token obtained (first 20 chars): {old_refresh_token[:20]}...")

# --- Step 2: Use the refresh token ONCE (should succeed, and rotate) ---
print("\n[*] Using refresh token to get a new access token (1st use)...")
resp2 = requests.post(token_url, json={
    "grant_type": "refresh_token",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": old_refresh_token
})
data2 = resp2.json()
print(f"[*] Status: {resp2.status_code}")
log(f"1st refresh use status: {resp2.status_code}")

if "refresh_token" in data2:
    new_refresh_token = data2["refresh_token"]
    print(f"[*] NEW refresh token issued (rotation confirmed): {new_refresh_token[:20]}...")
    log("Rotation confirmed: new refresh token issued.")
else:
    print("[WARNING] No new refresh token returned - check rotation settings.")
    log(f"WARNING: no new refresh token: {json.dumps(data2)}")

# --- Step 3: Try to REUSE the OLD refresh token (should FAIL) ---
print("\n[*] Attempting to REUSE the OLD refresh token (replay attack simulation)...")
resp3 = requests.post(token_url, json={
    "grant_type": "refresh_token",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": old_refresh_token
})
data3 = resp3.json()
print(f"[*] Status: {resp3.status_code}")
print(f"[*] Response: {json.dumps(data3, indent=2)}")

log(f"Old token replay attempt status: {resp3.status_code}")
log(f"Response: {json.dumps(data3)}")

if resp3.status_code != 200:
    print(f"\n[RESULT] ATTACK BLOCKED - Old refresh token correctly REJECTED after rotation.")
    log("Result: ATTACK BLOCKED - old refresh token rejected.")
else:
    print(f"\n[RESULT] WARNING - Old refresh token was still accepted. Check rotation config.")
    log("Result: WARNING - old refresh token still accepted.")

print(f"\n[LOGGED] Results saved to {log_path}")
print("\n[*] Test completed")