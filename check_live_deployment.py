#!/usr/bin/env python3
"""
Live Deployment Verification Script
Checks if the Streamlit Cloud deployment has the latest updates
"""

import requests
import time
import json
from datetime import datetime

def check_deployment_status():
    """Check if the live deployment has the updated statistics"""
    
    url = "https://quxatscore.streamlit.app/"
    
    print(f"🔍 Checking live deployment at: {url}")
    print(f"⏰ Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    try:
        # Make request to live site
        response = requests.get(url, timeout=30)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for updated statistics
            has_7067 = "7,067" in content or "7067" in content
            has_4561 = "4,561" in content or "4561" in content
            has_dental = "dental" in content.lower()
            
            print(f"📊 Contains 7,067 organizations: {'✅ YES' if has_7067 else '❌ NO'}")
            print(f"🏥 Contains 4,561 NABH facilities: {'✅ YES' if has_4561 else '❌ NO'}")
            print(f"🦷 Contains dental references: {'✅ YES' if has_dental else '❌ NO'}")
            
            # Check for old statistics (should not be present)
            has_old_6535 = "6,535" in content or "6535" in content
            has_old_4029 = "4,029" in content or "4029" in content
            
            print(f"🔍 Still contains old 6,535: {'⚠️ YES' if has_old_6535 else '✅ NO'}")
            print(f"🔍 Still contains old 4,029: {'⚠️ YES' if has_old_4029 else '✅ NO'}")
            
            # Overall deployment status
            is_updated = has_7067 and has_4561 and not has_old_6535 and not has_old_4029
            
            print("-" * 60)
            if is_updated:
                print("🎉 DEPLOYMENT SUCCESSFUL: Live site has updated statistics!")
            else:
                print("⏳ DEPLOYMENT PENDING: Live site may still be updating...")
                print("   This is normal - Streamlit Cloud can take a few minutes to deploy.")
            
            return {
                "status_code": response.status_code,
                "has_updated_stats": is_updated,
                "has_7067": has_7067,
                "has_4561": has_4561,
                "has_dental": has_dental,
                "has_old_stats": has_old_6535 or has_old_4029,
                "check_time": datetime.now().isoformat()
            }
            
        else:
            print(f"❌ Error: Received status code {response.status_code}")
            return {"status_code": response.status_code, "error": "Non-200 status code"}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to live site: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    result = check_deployment_status()
    
    # Save result to file
    with open("live_deployment_check_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Results saved to: live_deployment_check_result.json")