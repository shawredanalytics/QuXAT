#!/usr/bin/env python3
"""
Force Streamlit Cloud Deployment Script
Makes a small change to trigger a fresh deployment
"""

import os
import subprocess
from datetime import datetime

def force_deployment():
    """Force a new deployment by making a small change"""
    
    print("🚀 Forcing Streamlit Cloud deployment...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Create a deployment trigger file
    trigger_content = f"""# Deployment Trigger
# This file forces Streamlit Cloud to redeploy
# Last updated: {datetime.now().isoformat()}
# Reason: Dental facilities integration deployment
"""
    
    with open(".streamlit_deployment_trigger", "w") as f:
        f.write(trigger_content)
    
    print("✅ Created deployment trigger file")
    
    # Add, commit, and push the trigger file
    try:
        subprocess.run(["git", "add", ".streamlit_deployment_trigger"], check=True)
        print("✅ Added trigger file to git")
        
        commit_msg = f"Force deployment trigger - dental facilities update {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print("✅ Committed trigger file")
        
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Pushed to GitHub - this should trigger Streamlit Cloud deployment")
        
        print("-" * 60)
        print("🎯 Deployment trigger sent!")
        print("📱 Streamlit Cloud should now rebuild the application")
        print("⏱️  This typically takes 2-5 minutes")
        print("🔗 Monitor at: https://share.streamlit.io/")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during git operations: {e}")
        return False

if __name__ == "__main__":
    success = force_deployment()
    if success:
        print("\n✨ Deployment trigger completed successfully!")
    else:
        print("\n❌ Deployment trigger failed!")