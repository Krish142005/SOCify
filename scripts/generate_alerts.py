import requests
import json
import time
import random
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"
INGEST_URL = f"{BACKEND_URL}/ingest"
RULES_URL = f"{BACKEND_URL}/rules"

def get_rules():
    try:
        response = requests.get(RULES_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching rules: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return []

def generate_log_for_rule(rule):
    """
    Generates a log that should trigger the given rule
    """
    timestamp = datetime.utcnow().strftime("%b %d %H:%M:%S")
    host = f"server-{random.randint(1, 5)}"
    src_ip = f"192.168.1.{random.randint(100, 200)}"
    user = random.choice(["admin", "root", "user1", "service_account"])
    
    # Construct a raw log string based on rule requirements
    raw_log = ""
    count = 1
    
    if 'match' in rule:
        match_conditions = rule['match']
        
        # Special handling for common rules
        if "event.action" in match_conditions:
            action = match_conditions["event.action"]
            
            if action == "login_failed":
                raw_log = f"{timestamp} {host} sshd[1234]: Failed password for {user} from {src_ip} port 22 ssh2"
            elif action == "login_success":
                raw_log = f"{timestamp} {host} sshd[1234]: Accepted password for {user} from {src_ip} port 22 ssh2"
            elif action == "sudo_usage":
                raw_log = f"{timestamp} {host} sudo: {user} : TTY=pts/0 ; PWD=/home/{user} ; USER=root ; COMMAND=/bin/bash"
            else:
                # Generic log
                raw_log = f"{timestamp} {host} app: Action {action} performed by {user} from {src_ip}"
        
        elif "process.name" in match_conditions:
            proc = match_conditions["process.name"]
            raw_log = f"{timestamp} {host} kernel: Process {proc} started by user {user}"
            
        else:
            # Fallback generic log
            raw_log = f"{timestamp} {host} system: Event triggered for rule {rule['rule_name']} by {user} from {src_ip}"

        # For threshold rules
        if rule.get('type') == 'threshold':
            count = rule.get('threshold', 1) + 1
            
        return raw_log, count
            
    return None, 0

def main():
    print("🚀 Starting Alert Generator...")
    
    # 1. Fetch Rules
    print("📥 Fetching active rules...")
    rules = get_rules()
    print(f"✅ Found {len(rules)} active rules")
    
    if not rules:
        print("❌ No rules found. Make sure backend is running and rules are loaded.")
        return

    # 2. Generate Alerts
    print("\n⚡ Generating alerts...")
    
    triggered_count = 0
    
    for rule in rules:
        # Force trigger A001 and A002
        if rule['rule_id'] not in ['A001', 'A002']:
            if random.random() > 0.6: 
                continue
            
        raw_log, count = generate_log_for_rule(rule)
        
        if raw_log:
            print(f"Attempting to trigger: {rule['rule_name']} (Sending {count} logs)")
            
            payload = {
                "raw_log": raw_log,
                "source_type": "syslog",
                "metadata": {
                    "hostname": "test-generator",
                    "simulation": "true"
                }
            }
            
            try:
                for i in range(count):
                    # Send log to ingest API
                    response = requests.post(INGEST_URL, json=payload)
                    print(f"Response: {response.status_code} - {response.text}")
                    
                    if response.status_code != 200:
                        print(f"❌ Failed to send log: {response.text}")
                
                if response.status_code == 200:
                    print(f"✅ Sent logs for: {rule['rule_name']}")
                    triggered_count += 1
                
                # Small delay between alerts
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error sending log: {e}")

    print(f"\n🎉 Finished! Generated alerts for {triggered_count} rules.")
    print("👉 Check your dashboard now: http://localhost:3000")

if __name__ == "__main__":
    main()
