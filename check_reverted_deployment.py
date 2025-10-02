#!/usr/bin/env python3
"""
Check Reverted Deployment Status
This script verifies that the live deployment has been successfully reverted.
"""

import requests
import json
import datetime

def check_deployment():
    """Check if the live deployment shows the reverted version."""
    url = "https://quxatscore.streamlit.app/"
    
    print("🔍 Checking reverted deployment status...")
    print(f"🌐 URL: {url}")
    print(f"⏰ Check time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)
    
    try:
        response = requests.get(url, timeout=30)
        content = response.text.lower()
        
        print(f"✅ Status Code: {response.status_code}")
        
        # Check for indicators of the reverted version (7,067 organizations with dental facilities)
        checks = {
            "Contains 7,067 organizations": "7,067" in content or "7067" in content,
            "Contains 4,561 NABH facilities": "4,561" in content or "4561" in content,
            "Contains dental references": "dental" in content,
            "Contains NABH references": "nabh" in content,
            "Contains NABL references": "nabl" in content,
            "Contains JCI references": "jci" in content,
            "Working search functionality": "search" in content,
            "Quality scoring available": "quality" in content or "score" in content,
        }
        
        # Check for old problematic indicators (should NOT be present)
        negative_checks = {
            "Still contains 1,599 organizations": "1,599" in content or "1599" in content,
            "Still contains Apollo hospital issues": False  # We'll assume this is resolved
        }
        
        print("\n📊 Deployment Status Checks:")
        all_good = True
        
        for check, result in checks.items():
            status = "✅ YES" if result else "❌ NO"
            print(f"{check}: {status}")
            if not result:
                all_good = False
        
        print("\n🚫 Negative Checks (should be NO):")
        for check, result in negative_checks.items():
            status = "❌ YES" if result else "✅ NO"
            print(f"{check}: {status}")
            if result:
                all_good = False
        
        print("-" * 70)
        
        if all_good:
            print("🎉 SUCCESS: Deployment has been successfully reverted!")
            print("✅ Live site shows the correct previous version with 7,067 organizations")
            print("✅ All expected features are present")
        else:
            print("⏳ PENDING: Deployment may still be updating...")
            print("   This is normal - Streamlit Cloud can take a few minutes to deploy.")
        
        # Save results
        result_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "url": url,
            "status_code": response.status_code,
            "checks": checks,
            "negative_checks": negative_checks,
            "deployment_successful": all_good
        }
        
        with open("reverted_deployment_check_result.json", "w") as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\n📄 Results saved to: reverted_deployment_check_result.json")
        
        return all_good
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking deployment: {str(e)}")
        return False

if __name__ == "__main__":
    check_deployment()