from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from datetime import datetime
import os

print("=" * 65)
print("PROJECT 4 - CRYPTOGRAPHIC AGENT IDENTITY: SIGN & VERIFY")
print("=" * 65)

# --- Load keys from disk ---
with open("keys/agent_private_key.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

with open("keys/agent_public_key.pem", "rb") as f:
    public_key = serialization.load_pem_public_key(f.read())

os.makedirs("logs", exist_ok=True)
log_path = "logs/sign_verify.txt"

def log(entry):
    with open(log_path, "a") as f:
        f.write(entry + "\n")

def verify_message(message_bytes, signature, label):
    print(f"\n--- VERIFYING: {label} ---")
    print(f"Message: {message_bytes}")
    log("=" * 65)
    log(f"Timestamp: {datetime.now().isoformat()}")
    log(f"Scenario: {label}")
    log(f"Message: {message_bytes}")
    try:
        public_key.verify(signature, message_bytes)
        print("[VERIFICATION] SUCCESS - Signature is valid. Message accepted.")
        log("Result: SUCCESS - Signature valid, message accepted.")
    except InvalidSignature:
        print("[VERIFICATION] FAILED - Invalid signature. Message REJECTED.")
        print("[ERROR] SecurityError: signature does not match message content. Possible tampering detected.")
        log("Result: FAILED - Invalid signature. Message REJECTED.")
        log("Error: SecurityError - signature does not match message content. Possible tampering detected.")
    log("=" * 65 + "\n")

# --- Original message from Agent A to Agent B ---
original_message = b"[ORCHESTRATOR] Approve refund for user_8842, amount=500.00"
signature = private_key.sign(original_message)

print(f"\n[*] Original message signed by Agent A (private key).")
print(f"[*] Signature (hex): {signature.hex()[:40]}...")

# --- Scenario 1: legitimate, unmodified message ---
verify_message(original_message, signature, "Legitimate message (unmodified)")

# --- Scenario 2: tampered message (one character changed) ---
tampered_message = b"[ORCHESTRATOR] Approve refund for user_8842, amount=900.00"  # amount changed
verify_message(tampered_message, signature, "Tampered message (amount changed 500->900)")

print(f"\n[LOGGED] Results saved to {log_path}")
print("\n[*] Test completed")