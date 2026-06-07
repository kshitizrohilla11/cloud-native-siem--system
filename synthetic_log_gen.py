import requests
import random
import time
import uuid
import json
import argparse
from datetime import datetime, UTC

# Your API Gateway endpoint
API_URL = "https://o4dhl0x6p6.execute-api.ap-south-1.amazonaws.com/dev/ingest"

# Sample data pools
EVENT_TYPES = ["login", "file_access", "network", "syslog", "ping"]
SEVERITIES = ["low", "medium", "high", "critical"]
USERS = ["alice", "bob", "charlie", "eve", "test"]
SOURCES = ["auth_service", "vpn_gateway", "firewall", "endpoint", "syslog"]

def generate_log():
    etype = random.choice(EVENT_TYPES)
    severity = random.choice(SEVERITIES)
    user = random.choice(USERS)
    src = random.choice(SOURCES)
    ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
    now = datetime.now(UTC).isoformat()

    return {
        "event_type": etype,
        "severity": severity,
        "message": f"{etype} event from {user} via {src} at {now}",
        "user": user,
        "source_ip": ip,
        "source": src,
        "status": "open",
        "details": {
            "generator_id": str(uuid.uuid4()),
            "generated_at": now
        }
    }

def send_log(log, idx=None):
    try:
        resp = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(log),
            timeout=10   # prevent infinite wait
        )
        prefix = f"#{idx}" if idx is not None else ""
        print(f"[{datetime.now(UTC).isoformat()}] {prefix} Sent: "
              f"{log['event_type']} {log['severity']} -> {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[{datetime.now(UTC).isoformat()}] ERROR sending log: {e}")

def continuous_mode():
    print("🔄 Running in Continuous Mode (Ctrl+C to stop)...")
    while True:
        log = generate_log()
        send_log(log)
        time.sleep(random.uniform(1, 3))  # 1–3 sec delay

def bulk_mode(count):
    print(f"📦 Running in Bulk Mode — sending {count} logs...")
    for i in range(count):
        log = generate_log()
        send_log(log, idx=i+1)
        time.sleep(0.1)  # slight delay to avoid API Gateway throttling

def main():
    parser = argparse.ArgumentParser(description="Synthetic Log Generator for SIEM")
    parser.add_argument("--mode", choices=["continuous", "bulk"], default="continuous",
                        help="Choose mode: continuous (default) or bulk")
    parser.add_argument("--count", type=int, default=50,
                        help="Number of logs to send in bulk mode (default=50)")
    args = parser.parse_args()

    if args.mode == "continuous":
        continuous_mode()
    else:
        bulk_mode(args.count)

if __name__ == "__main__":
    main()
