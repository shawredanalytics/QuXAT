#!/usr/bin/env python3
"""
Force Streamlit Cloud Deployment - Revert Version
This script triggers a deployment by creating a trigger file and pushing to GitHub.
"""

import os
import subprocess
import datetime

def run_command(command, description):
    """Run a shell command and return the result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def main():
    print("🚀 Force Streamlit Cloud Deployment - Revert Version")
    print("=" * 60)
    
    # Create timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create deployment trigger file
    trigger_content = f"""# Deployment Trigger - Revert Version
# Generated: {timestamp}
# Purpose: Force Streamlit Cloud to rebuild with reverted version (7,067 organizations)
# This file triggers automatic deployment when pushed to GitHub

DEPLOYMENT_TRIGGER=revert_to_working_version_{timestamp}
"""
    
    trigger_file = ".streamlit_deployment_trigger_revert"
    
    try:
        with open(trigger_file, 'w') as f:
            f.write(trigger_content)
        print(f"✅ Created trigger file: {trigger_file}")
    except Exception as e:
        print(f"❌ Failed to create trigger file: {str(e)}")
        return False
    
    # Git operations
    commands = [
        (f"git add {trigger_file}", "Adding trigger file to Git"),
        (f'git commit -m "Force deployment trigger - revert to working version {timestamp}"', "Committing trigger file"),
        ("git push origin main", "Pushing to GitHub (triggers Streamlit Cloud deployment)")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    print("\n🎉 Deployment trigger completed successfully!")
    print("📡 Streamlit Cloud should now rebuild the application with the reverted version.")
    print("⏰ Deployment typically takes 2-5 minutes to complete.")
    print("🔗 Monitor at: https://quxatscore.streamlit.app/")
    
    return True

if __name__ == "__main__":
    main()