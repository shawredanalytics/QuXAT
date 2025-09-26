#!/usr/bin/env python3
import time
import requests
import json
from datetime import datetime

def monitor_deployment():
    app_url = "https://quxatscore.streamlit.app/"
    max_checks = 20
    check_interval = 15
    
    print(f"🔍 Monitoring deployment at {app_url}")
    
    for i in range(max_checks):
        try:
            response = requests.get(app_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Deployment successful! ({i * check_interval}s)")
                return True
            else:
                print(f"⏳ Status {response.status_code}, checking again...")
        except Exception as e:
            print(f"⏳ Connection failed, checking again... ({e})")
        
        if i < max_checks - 1:
            time.sleep(check_interval)
    
    print("❌ Deployment monitoring timeout")
    return False

if __name__ == "__main__":
    monitor_deployment()
