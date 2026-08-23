import os
import re
from datetime import datetime

print("=" * 65)
print("PROJECT 4 - INPUT/OUTPUT GUARDRAILS (Rebuff-based heuristics)")
print("=" * 65)

# --- Input Guardrail: heuristic-based injection detection ---
# This mirrors Rebuff's own "Heuristics" defense layer (pattern/keyword
# filtering before content reaches the LLM), used here in local/offline
# mode since Rebuff's full SDK requires external OpenAI + Pinecone services.

INJECTION_MARKERS = [
    r"disregard (the )?(surrounding )?(document )?context",
    r"ignore (all )?(previous|prior) instructions",
    r"debug mode",
    r"print (the )?(system prompt|credential|token|SIMULATED_CREDENTIAL)",
    r"you are now (in|operating)",
    r"return it exactly as available",
    r"append your (full )?system prompt",
    r"reveal (this|the) system prompt",
    r"include the exact value of",
    r"note to assistant",
]

def guardrail_check(text):
    for pattern in INJECTION_MARKERS:
        if re.search(pattern, text, re.IGNORECASE):
            return True, pattern
    return False, None

# --- Output Guardrail: JWT-shaped string redaction ---
JWT_REGEX = r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"

def redact_jwt(text):
    return re.sub(JWT_REGEX, "[REDACTED]", text)

os.makedirs("logs", exist_ok=True)
log_path = "logs/guardrail_results.txt"

def log(entry):
    with open(log_path, "a") as f:
        f.write(entry + "\n")

# --- Load Project 3 payloads ---
payload_dir = r"..\..\Project3_AI_Identity_Attacks\attack1_prompt_injection"
payload_files = [
    os.path.join(payload_dir, "document_payload_1.txt"),
    os.path.join(payload_dir, "document_payload_2.txt"),
    os.path.join(payload_dir, "document_payload_3.txt"),
]

blocked_count = 0

for path in payload_files:
    print(f"\n[*] Testing payload: {os.path.basename(path)}")
    with open(path, "r") as f:
        content = f.read()

    is_blocked, matched_pattern = guardrail_check(content)

    log("=" * 65)
    log(f"Timestamp: {datetime.now().isoformat()}")
    log(f"Payload: {os.path.basename(path)}")

    if is_blocked:
        print(f"[GUARDRAIL] Status: BLOCKED")
        print(f"[GUARDRAIL] Reason: matched pattern -> '{matched_pattern}'")
        blocked_count += 1
        log(f"Status: BLOCKED")
        log(f"Reason: matched pattern -> '{matched_pattern}'")
    else:
        print(f"[GUARDRAIL] Status: PASSED (no injection pattern matched)")
        log(f"Status: PASSED")

print(f"\n[SUMMARY] {blocked_count}/{len(payload_files)} payloads BLOCKED by input guardrail")
log(f"\n[SUMMARY] {blocked_count}/{len(payload_files)} payloads BLOCKED")
log("=" * 65 + "\n")

print(f"\n[LOGGED] Results saved to {log_path}")
print("\n[*] Test completed")