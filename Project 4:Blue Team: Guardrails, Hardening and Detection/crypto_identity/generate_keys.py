from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import os

print("=" * 65)
print("PROJECT 4 - CRYPTOGRAPHIC AGENT IDENTITY: KEY GENERATION")
print("=" * 65)

# --- Generate Ed25519 key pair ---
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

os.makedirs("keys", exist_ok=True)

# --- Serialize and save private key ---
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
with open("keys/agent_private_key.pem", "wb") as f:
    f.write(private_bytes)

# --- Serialize and save public key ---
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
with open("keys/agent_public_key.pem", "wb") as f:
    f.write(public_bytes)

print("\n[*] Ed25519 key pair generated successfully.")
print("[*] Private key saved to: keys/agent_private_key.pem")
print("[*] Public key saved to: keys/agent_public_key.pem")

print("\n--- PRIVATE KEY (PEM) ---")
print(private_bytes.decode())

print("--- PUBLIC KEY (PEM) ---")
print(public_bytes.decode())

print("[*] Key generation completed.")