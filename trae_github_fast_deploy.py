#!/usr/bin/env python3
"""
Trae AI → GitHub Fast Deployment Integration
Ultra-fast deployment pipeline from Trae AI to GitHub to Streamlit Cloud
"""

import os
import json
import subprocess
import requests
import webbrowser
from datetime import datetime
from pathlib import Path
import time

class TraeGitHubFastDeploy:
    def __init__(self):
        self.project_root = Path.cwd()
        self.config_file = self.project_root / "trae_github_config.json"
        self.load_config()
        self.github_api_base = "https://api.github.com"
    
    def load_config(self):
        """Load fast deployment configuration"""
        default_config = {
            "repository": "shawredanalytics/QuXAT",
            "owner": "shawredanalytics",
            "repo_name": "QuXAT",
            "branch": "main",
            "app_name": "quxatscore",
            "streamlit_url": "https://quxatscore.streamlit.app/",
            "github_token": None,  # Will be loaded from environment
            "fast_deploy": {
                "skip_tests": False,
                "auto_commit": True,
                "auto_push": True,
                "trigger_workflow": True,
                "open_browser": True
            },
            "deployment_message_template": "🚀 Fast deploy from Trae AI - {timestamp}",
            "workflow_file": ".github/workflows/deploy.yml"
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_github_token(self):
        """Get GitHub token from environment or config"""
        token = os.environ.get('GITHUB_TOKEN') or self.config.get('github_token')
        if not token:
            print("⚠️  GitHub token not found. Set GITHUB_TOKEN environment variable or configure in trae_github_config.json")
            return None
        return token
    
    def check_git_status(self):
        """Check git repository status"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True, check=True)
            
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            has_changes = bool(result.stdout.strip())
            
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            
            return {
                'has_changes': has_changes,
                'current_branch': current_branch,
                'is_git_repo': True
            }
        
        except subprocess.CalledProcessError:
            return {
                'has_changes': False,
                'current_branch': None,
                'is_git_repo': False
            }
    
    def fast_commit_and_push(self):
        """Fast commit and push changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        commit_message = self.config['deployment_message_template'].format(timestamp=timestamp)
        
        try:
            print("⚡ Fast commit and push...")
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit with timestamp
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push to remote
            subprocess.run(['git', 'push', 'origin', self.config['branch']], check=True)
            
            print(f"✅ Committed and pushed: {commit_message}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operations failed: {e}")
            return False
    
    def trigger_github_workflow(self):
        """Trigger GitHub Actions workflow via API"""
        token = self.get_github_token()
        if not token:
            return False
        
        url = f"{self.github_api_base}/repos/{self.config['owner']}/{self.config['repo_name']}/actions/workflows/deploy.yml/dispatches"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'ref': self.config['branch'],
            'inputs': {
                'deploy_environment': 'production',
                'force_deploy': 'false'
            }
        }
        
        try:
            print("🚀 Triggering GitHub Actions workflow...")
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 204:
                print("✅ GitHub Actions workflow triggered successfully!")
                return True
            else:
                print(f"❌ Failed to trigger workflow: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")
            return False
    
    def get_workflow_status(self):
        """Get the status of recent workflow runs"""
        token = self.get_github_token()
        if not token:
            return None
        
        url = f"{self.github_api_base}/repos/{self.config['owner']}/{self.config['repo_name']}/actions/runs"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                runs = response.json()['workflow_runs']
                if runs:
                    latest_run = runs[0]
                    return {
                        'id': latest_run['id'],
                        'status': latest_run['status'],
                        'conclusion': latest_run['conclusion'],
                        'html_url': latest_run['html_url'],
                        'created_at': latest_run['created_at']
                    }
            return None
        except requests.RequestException:
            return None
    
    def validate_project_fast(self):
        """Fast project validation"""
        required_files = [
            'streamlit_app.py',
            'requirements.txt',
            'runtime.txt',
            '.streamlit/config.toml'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        print("✅ Fast validation passed")
        return True
    
    def fast_deploy(self):
        """Execute fast deployment pipeline"""
        print("⚡ Trae AI → GitHub Fast Deploy Pipeline")
        print("=" * 50)
        
        # Fast validation
        if not self.validate_project_fast():
            return False
        
        # Check git status
        git_status = self.check_git_status()
        if not git_status['is_git_repo']:
            print("❌ Not a git repository")
            return False
        
        print(f"📂 Current branch: {git_status['current_branch']}")
        
        # Handle uncommitted changes
        if git_status['has_changes']:
            if self.config['fast_deploy']['auto_commit']:
                if not self.fast_commit_and_push():
                    return False
            else:
                print("⚠️  Uncommitted changes detected. Enable auto_commit or commit manually.")
                return False
        else:
            print("✅ No uncommitted changes")
        
        # Trigger GitHub Actions workflow
        if self.config['fast_deploy']['trigger_workflow']:
            if not self.trigger_github_workflow():
                print("⚠️  Workflow trigger failed, but code is pushed to GitHub")
        
        # Generate deployment info
        deployment_info = {
            "timestamp": datetime.now().isoformat(),
            "deployment_type": "fast_deploy",
            "repository": self.config['repository'],
            "branch": self.config['branch'],
            "app_url": self.config['streamlit_url'],
            "github_actions_url": f"https://github.com/{self.config['repository']}/actions",
            "streamlit_deploy_url": f"https://share.streamlit.io/deploy?repository={self.config['repository']}&branch={self.config['branch']}&mainModule=streamlit_app.py&appName={self.config['app_name']}"
        }
        
        # Save deployment info
        with open('fast_deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        # Display results
        print("\n🎉 Fast Deployment Complete!")
        print("=" * 30)
        print(f"🌐 App URL: {deployment_info['app_url']}")
        print(f"⚙️  GitHub Actions: {deployment_info['github_actions_url']}")
        print(f"🚀 Deploy URL: {deployment_info['streamlit_deploy_url']}")
        
        # Open browser if configured
        if self.config['fast_deploy']['open_browser']:
            print("\n🌐 Opening GitHub Actions in browser...")
            webbrowser.open(deployment_info['github_actions_url'])
        
        # Monitor workflow status
        print("\n📊 Monitoring deployment...")
        for i in range(5):  # Check 5 times
            time.sleep(2)
            status = self.get_workflow_status()
            if status:
                print(f"🔄 Workflow status: {status['status']} ({status.get('conclusion', 'running')})")
                if status['status'] == 'completed':
                    if status['conclusion'] == 'success':
                        print("✅ Deployment successful!")
                    else:
                        print(f"❌ Deployment failed: {status['conclusion']}")
                    break
            else:
                print("📡 Checking workflow status...")
        
        return True
    
    def status(self):
        """Show deployment status"""
        print("📊 Trae AI → GitHub Fast Deploy Status")
        print("=" * 40)
        
        git_status = self.check_git_status()
        print(f"📂 Repository: {self.config['repository']}")
        print(f"🌿 Branch: {git_status.get('current_branch', 'unknown')}")
        print(f"📝 Has changes: {git_status.get('has_changes', False)}")
        print(f"🌐 App URL: {self.config['streamlit_url']}")
        
        # Check workflow status
        workflow_status = self.get_workflow_status()
        if workflow_status:
            print(f"⚙️  Last workflow: {workflow_status['status']} ({workflow_status.get('conclusion', 'running')})")
        else:
            print("⚙️  Workflow status: Unknown")
        
        return True
    
    def configure(self):
        """Interactive configuration"""
        print("⚙️  Trae AI → GitHub Fast Deploy Configuration")
        print("=" * 50)
        
        # GitHub token setup
        token = self.get_github_token()
        if token:
            print("✅ GitHub token configured")
        else:
            print("❌ GitHub token not configured")
            print("💡 Set GITHUB_TOKEN environment variable or add to config")
        
        # Repository info
        print(f"📂 Repository: {self.config['repository']}")
        print(f"🌿 Branch: {self.config['branch']}")
        print(f"📱 App: {self.config['app_name']}")
        
        # Fast deploy settings
        print("\n⚡ Fast Deploy Settings:")
        for key, value in self.config['fast_deploy'].items():
            print(f"  {key}: {value}")
        
        return True

def main():
    """Main function"""
    fast_deploy = TraeGitHubFastDeploy()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'deploy':
            fast_deploy.fast_deploy()
        elif command == 'status':
            fast_deploy.status()
        elif command == 'configure':
            fast_deploy.configure()
        elif command == 'workflow':
            status = fast_deploy.get_workflow_status()
            if status:
                print(json.dumps(status, indent=2))
            else:
                print("No workflow status available")
        elif command == 'validate':
            if fast_deploy.validate_project_fast():
                print("✅ Project validation successful - ready for deployment")
            else:
                print("❌ Project validation failed - check requirements")
        else:
            print("Usage: python trae_github_fast_deploy.py [deploy|status|configure|workflow|validate]")
    else:
        fast_deploy.fast_deploy()

if __name__ == "__main__":
    main()