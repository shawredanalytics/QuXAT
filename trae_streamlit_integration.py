#!/usr/bin/env python3
"""
Trae AI - Streamlit Cloud Integration
Seamless deployment workflow from Trae AI to Streamlit Cloud
"""

import os
import json
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

class TraeStreamlitIntegration:
    def __init__(self):
        self.project_root = Path.cwd()
        self.config_file = self.project_root / "trae_deployment_config.json"
        self.load_config()
    
    def load_config(self):
        """Load or create deployment configuration"""
        default_config = {
            "app_name": "quxatscore",
            "repository": "shawredanalytics/QuXAT",
            "branch": "main",
            "main_file": "streamlit_app.py",
            "streamlit_cloud_url": "https://share.streamlit.io/",
            "auto_open_browser": True,
            "auto_commit": True,
            "deployment_checks": {
                "validate_files": True,
                "test_app_startup": True,
                "check_git_status": True
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save deployment configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_trae_environment(self):
        """Check if running in Trae AI environment"""
        trae_indicators = [
            os.environ.get('TRAE_AI'),
            os.environ.get('TRAE_WORKSPACE'),
            'trae' in str(self.project_root).lower()
        ]
        return any(trae_indicators)
    
    def validate_project_structure(self):
        """Validate QuXAT project structure for deployment"""
        required_files = {
            'streamlit_app.py': 'Main Streamlit application',
            'requirements.txt': 'Python dependencies',
            'runtime.txt': 'Python runtime version',
            '.streamlit/config.toml': 'Streamlit configuration',
            'unified_healthcare_organizations.json': 'Healthcare organizations data'
        }
        
        validation_results = {}
        all_valid = True
        
        print("🔍 Validating QuXAT project structure...")
        
        for file_path, description in required_files.items():
            file_exists = (self.project_root / file_path).exists()
            validation_results[file_path] = {
                'exists': file_exists,
                'description': description
            }
            
            status = "✅" if file_exists else "❌"
            print(f"{status} {file_path} - {description}")
            
            if not file_exists:
                all_valid = False
        
        return all_valid, validation_results
    
    def prepare_deployment(self):
        """Prepare the project for Streamlit Cloud deployment"""
        print("🚀 Preparing QuXAT for Streamlit Cloud deployment...")
        
        # Validate project structure
        is_valid, validation_results = self.validate_project_structure()
        if not is_valid:
            print("❌ Project validation failed. Please ensure all required files exist.")
            return False
        
        # Check git status
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            has_changes = bool(result.stdout.strip())
            
            if has_changes:
                print("📝 Uncommitted changes detected")
                if self.config['auto_commit']:
                    self.commit_changes()
                else:
                    print("⚠️  Please commit your changes before deployment")
                    return False
            else:
                print("✅ Git status clean")
        
        except subprocess.CalledProcessError:
            print("⚠️  Git not initialized or not available")
        
        return True
    
    def commit_changes(self):
        """Commit and push changes to GitHub"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        commit_message = f"Deploy QuXAT from Trae AI - {timestamp}"
        
        try:
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            subprocess.run(['git', 'push', 'origin', self.config['branch']], check=True)
            print(f"✅ Committed and pushed: {commit_message}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operations failed: {e}")
            return False
    
    def generate_deployment_url(self):
        """Generate Streamlit Cloud deployment URL"""
        base_url = "https://share.streamlit.io/deploy"
        params = {
            'repository': self.config['repository'],
            'branch': self.config['branch'],
            'mainModule': self.config['main_file'],
            'appName': self.config['app_name']
        }
        
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def deploy_to_streamlit_cloud(self):
        """Main deployment function"""
        print("🎯 Trae AI → Streamlit Cloud Deployment")
        print("=" * 50)
        
        # Check if in Trae environment
        if self.check_trae_environment():
            print("✅ Trae AI environment detected")
        else:
            print("ℹ️  Running outside Trae AI environment")
        
        # Prepare deployment
        if not self.prepare_deployment():
            return False
        
        # Generate deployment info
        deployment_info = {
            "timestamp": datetime.now().isoformat(),
            "app_name": self.config['app_name'],
            "repository": self.config['repository'],
            "branch": self.config['branch'],
            "main_file": self.config['main_file'],
            "app_url": f"https://{self.config['app_name']}.streamlit.app/",
            "deployment_url": self.generate_deployment_url(),
            "streamlit_cloud_dashboard": self.config['streamlit_cloud_url']
        }
        
        # Save deployment info
        with open('deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        # Display deployment information
        print("\n🎉 QuXAT Ready for Streamlit Cloud Deployment!")
        print("=" * 50)
        print(f"📱 App Name: {deployment_info['app_name']}")
        print(f"🌐 App URL: {deployment_info['app_url']}")
        print(f"📂 Repository: {deployment_info['repository']}")
        print(f"🌿 Branch: {deployment_info['branch']}")
        print(f"📄 Main File: {deployment_info['main_file']}")
        
        print("\n🚀 Deployment Options:")
        print("1. 🔗 One-click deploy:", deployment_info['deployment_url'])
        print("2. 🎛️  Manual deploy:", deployment_info['streamlit_cloud_dashboard'])
        
        # Open browser if configured
        if self.config['auto_open_browser']:
            print("\n🌐 Opening Streamlit Cloud in browser...")
            webbrowser.open(deployment_info['streamlit_cloud_dashboard'])
        
        print("\n✅ Deployment preparation complete!")
        print("🎯 Your QuXAT Healthcare Quality Grid is ready to go live!")
        
        return True
    
    def status(self):
        """Show current deployment status"""
        print("📊 QuXAT Deployment Status")
        print("=" * 30)
        
        is_valid, validation_results = self.validate_project_structure()
        
        print(f"✅ Project Valid: {is_valid}")
        print(f"📱 App Name: {self.config['app_name']}")
        print(f"🌐 Target URL: https://{self.config['app_name']}.streamlit.app/")
        print(f"📂 Repository: {self.config['repository']}")
        
        return is_valid

def main():
    """Main function"""
    integration = TraeStreamlitIntegration()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'status':
            integration.status()
        elif command == 'deploy':
            integration.deploy_to_streamlit_cloud()
        elif command == 'config':
            print(json.dumps(integration.config, indent=2))
        else:
            print("Usage: python trae_streamlit_integration.py [status|deploy|config]")
    else:
        integration.deploy_to_streamlit_cloud()

if __name__ == "__main__":
    main()