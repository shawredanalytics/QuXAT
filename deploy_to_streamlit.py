#!/usr/bin/env python3
"""
QuXAT Healthcare Quality Grid - Streamlit Cloud Deployment Script
This script automates the deployment process from Trae AI to Streamlit Cloud
"""

import subprocess
import sys
import os
import json
from datetime import datetime

class StreamlitDeployment:
    def __init__(self):
        self.repo_url = "https://github.com/shawredanalytics/QuXAT.git"
        self.app_name = "quxatscore"
        self.main_file = "streamlit_app.py"
        self.branch = "main"
        
    def check_git_status(self):
        """Check if there are any uncommitted changes"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print("⚠️  Warning: You have uncommitted changes:")
                print(result.stdout)
                return False
            else:
                print("✅ Git status clean - no uncommitted changes")
                return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error checking git status: {e}")
            return False
    
    def commit_and_push_changes(self, commit_message=None):
        """Commit and push any changes to GitHub"""
        if commit_message is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            commit_message = f"Deploy QuXAT to Streamlit Cloud - {timestamp}"
        
        try:
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            print("✅ Added all changes to git")
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            print(f"✅ Committed changes: {commit_message}")
            
            # Push to GitHub
            subprocess.run(['git', 'push', 'origin', self.branch], check=True)
            print("✅ Pushed changes to GitHub")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during git operations: {e}")
            return False
    
    def validate_deployment_files(self):
        """Validate that all required deployment files exist and are properly configured"""
        required_files = {
            'streamlit_app.py': 'Main Streamlit application file',
            'requirements.txt': 'Python dependencies',
            'runtime.txt': 'Python version specification',
            '.streamlit/config.toml': 'Streamlit configuration'
        }
        
        print("🔍 Validating deployment files...")
        all_valid = True
        
        for file_path, description in required_files.items():
            if os.path.exists(file_path):
                print(f"✅ {file_path} - {description}")
            else:
                print(f"❌ {file_path} - {description} (MISSING)")
                all_valid = False
        
        # Check if unified_healthcare_organizations.json exists
        if os.path.exists('unified_healthcare_organizations.json'):
            print("✅ unified_healthcare_organizations.json - Healthcare data")
        else:
            print("❌ unified_healthcare_organizations.json - Healthcare data (MISSING)")
            all_valid = False
        
        return all_valid
    
    def generate_deployment_info(self):
        """Generate deployment information"""
        deployment_info = {
            "app_name": self.app_name,
            "repository": self.repo_url,
            "branch": self.branch,
            "main_file": self.main_file,
            "deployment_url": f"https://{self.app_name}.streamlit.app/",
            "streamlit_cloud_url": "https://share.streamlit.io/",
            "deployment_timestamp": datetime.now().isoformat(),
            "deployment_steps": [
                "1. Go to https://share.streamlit.io/",
                "2. Sign in with GitHub account",
                "3. Click 'New app' or 'Create app'",
                "4. Repository: shawredanalytics/QuXAT",
                "5. Branch: main",
                "6. Main file path: streamlit_app.py",
                "7. App URL: quxatscore",
                "8. Click 'Deploy!'"
            ]
        }
        
        with open('deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print("✅ Generated deployment_info.json")
        return deployment_info
    
    def deploy(self, auto_commit=True, commit_message=None):
        """Main deployment function"""
        print("🚀 Starting QuXAT Streamlit Cloud Deployment Process...")
        print("=" * 60)
        
        # Step 1: Validate deployment files
        if not self.validate_deployment_files():
            print("❌ Deployment validation failed. Please fix missing files.")
            return False
        
        # Step 2: Check git status
        git_clean = self.check_git_status()
        
        # Step 3: Commit and push if needed
        if not git_clean and auto_commit:
            print("\n📤 Committing and pushing changes to GitHub...")
            if not self.commit_and_push_changes(commit_message):
                print("❌ Failed to commit and push changes")
                return False
        elif not git_clean and not auto_commit:
            print("⚠️  You have uncommitted changes. Please commit them manually or use auto_commit=True")
            return False
        
        # Step 4: Generate deployment info
        deployment_info = self.generate_deployment_info()
        
        # Step 5: Display deployment instructions
        print("\n" + "=" * 60)
        print("🎯 DEPLOYMENT READY!")
        print("=" * 60)
        print(f"📱 App Name: {deployment_info['app_name']}")
        print(f"🌐 Deployment URL: {deployment_info['deployment_url']}")
        print(f"📂 Repository: {deployment_info['repository']}")
        print(f"🌿 Branch: {deployment_info['branch']}")
        print(f"📄 Main File: {deployment_info['main_file']}")
        
        print("\n🔗 STREAMLIT CLOUD DEPLOYMENT STEPS:")
        for step in deployment_info['deployment_steps']:
            print(f"   {step}")
        
        print(f"\n✅ Your QuXAT Healthcare Quality Grid is ready for deployment!")
        print(f"🔗 Go to: https://share.streamlit.io/ to deploy now!")
        
        return True

def main():
    """Main function to run the deployment script"""
    deployer = StreamlitDeployment()
    
    # Parse command line arguments
    auto_commit = True
    commit_message = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--no-commit':
            auto_commit = False
        elif sys.argv[1].startswith('--message='):
            commit_message = sys.argv[1].split('=', 1)[1]
    
    # Run deployment
    success = deployer.deploy(auto_commit=auto_commit, commit_message=commit_message)
    
    if success:
        print("\n🎉 Deployment preparation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Deployment preparation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()