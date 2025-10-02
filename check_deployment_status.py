import requests
import time
from datetime import datetime

def check_deployment_status():
    """Check if the live deployment has the updated content"""
    url = "https://quxatscore.streamlit.app/"
    
    try:
        print(f"🔍 Checking deployment status at: {url}")
        print(f"⏰ Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        response = requests.get(url, timeout=30)
        content = response.text.lower()
        
        # Check for indicators of the new version
        indicators = {
            "1599 organizations": "1599" in content,
            "Apollo hospitals": "apollo" in content,
            "Working search": "search" in content and "organization" in content,
            "Quality score": "quality" in content and "score" in content
        }
        
        print(f"✅ Status Code: {response.status_code}")
        
        for indicator, found in indicators.items():
            status = "✅ YES" if found else "❌ NO"
            print(f"🔍 {indicator}: {status}")
        
        # Overall assessment
        if all(indicators.values()):
            print("\n🎉 DEPLOYMENT SUCCESSFUL: All indicators found!")
            return True
        else:
            print("\n⏳ DEPLOYMENT PENDING: Still updating...")
            return False
            
    except Exception as e:
        print(f"❌ Error checking deployment: {e}")
        return False

if __name__ == "__main__":
    success = check_deployment_status()
    if success:
        print("✨ Deployment verification completed successfully!")
    else:
        print("⏱️ Deployment may still be in progress. Check again in a few minutes.")