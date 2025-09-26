#!/usr/bin/env python3
"""
GitHub Secrets Configuration for Trae AI Integration
Secure deployment setup with GitHub Secrets management
"""

import os
import json
import base64
import requests
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives.hashes import SHA256

class GitHubSecretsManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.config_file = self.project_root / "github_secrets_config.json"
        self.github_api_base = "https://api.github.com"
        self.load_config()
    
    def load_config(self):
        """Load secrets configuration"""
        default_config = {
            "repository": "shawredanalytics/QuXAT",
            "owner": "shawredanalytics",
            "repo_name": "QuXAT",
            "secrets": {
                "STREAMLIT_CLOUD_TOKEN": {
                    "description": "Streamlit Cloud API token for deployment",
                    "required": False,
                    "value": None
                },
                "DEPLOYMENT_WEBHOOK_SECRET": {
                    "description": "Webhook secret for secure deployment triggers",
                    "required": False,
                    "value": None
                },
                "TRAE_AI_INTEGRATION_KEY": {
                    "description": "Integration key for Trae AI authentication",
                    "required": False,
                    "value": None
                }
            },
            "environment_variables": {
                "STREAMLIT_SERVER_HEADLESS": "true",
                "STREAMLIT_SERVER_PORT": "8501",
                "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
                "PYTHONPATH": "/app"
            }
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
        """Get GitHub token from environment"""
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            print("❌ GITHUB_TOKEN environment variable not set")
            print("💡 Create a personal access token at: https://github.com/settings/tokens")
            print("   Required scopes: repo, workflow, admin:repo_hook")
            return None
        return token
    
    def get_repository_public_key(self):
        """Get repository public key for encrypting secrets"""
        token = self.get_github_token()
        if not token:
            return None
        
        url = f"{self.github_api_base}/repos/{self.config['owner']}/{self.config['repo_name']}/actions/secrets/public-key"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get public key: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
    
    def encrypt_secret(self, secret_value, public_key_data):
        """Encrypt secret using repository public key"""
        try:
            # Decode the public key
            public_key_bytes = base64.b64decode(public_key_data['key'])
            public_key = serialization.load_der_public_key(public_key_bytes)
            
            # Encrypt the secret
            encrypted = public_key.encrypt(
                secret_value.encode('utf-8'),
                OAEP(
                    mgf=MGF1(algorithm=SHA256()),
                    algorithm=SHA256(),
                    label=None
                )
            )
            
            # Return base64 encoded encrypted value
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            print(f"❌ Encryption failed: {e}")
            return None
    
    def create_or_update_secret(self, secret_name, secret_value):
        """Create or update a repository secret"""
        token = self.get_github_token()
        if not token:
            return False
        
        # Get public key
        public_key_data = self.get_repository_public_key()
        if not public_key_data:
            return False
        
        # Encrypt secret
        encrypted_value = self.encrypt_secret(secret_value, public_key_data)
        if not encrypted_value:
            return False
        
        # Create/update secret
        url = f"{self.github_api_base}/repos/{self.config['owner']}/{self.config['repo_name']}/actions/secrets/{secret_name}"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'encrypted_value': encrypted_value,
            'key_id': public_key_data['key_id']
        }
        
        try:
            response = requests.put(url, headers=headers, json=payload)
            if response.status_code in [201, 204]:
                print(f"✅ Secret '{secret_name}' configured successfully")
                return True
            else:
                print(f"❌ Failed to set secret '{secret_name}': {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")
            return False
    
    def list_repository_secrets(self):
        """List all repository secrets"""
        token = self.get_github_token()
        if not token:
            return None
        
        url = f"{self.github_api_base}/repos/{self.config['owner']}/{self.config['repo_name']}/actions/secrets"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()['secrets']
            else:
                print(f"❌ Failed to list secrets: {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
    
    def setup_deployment_secrets(self):
        """Setup all deployment secrets"""
        print("🔐 Setting up GitHub Secrets for Trae AI Integration")
        print("=" * 55)
        
        # Check GitHub token
        if not self.get_github_token():
            return False
        
        # Generate deployment webhook secret
        import secrets
        webhook_secret = secrets.token_urlsafe(32)
        
        # Generate Trae AI integration key
        integration_key = secrets.token_urlsafe(24)
        
        # Update config with generated secrets
        self.config['secrets']['DEPLOYMENT_WEBHOOK_SECRET']['value'] = webhook_secret
        self.config['secrets']['TRAE_AI_INTEGRATION_KEY']['value'] = integration_key
        
        # Setup secrets
        secrets_to_setup = [
            ('DEPLOYMENT_WEBHOOK_SECRET', webhook_secret),
            ('TRAE_AI_INTEGRATION_KEY', integration_key)
        ]
        
        # Add Streamlit Cloud token if provided
        streamlit_token = os.environ.get('STREAMLIT_CLOUD_TOKEN')
        if streamlit_token:
            secrets_to_setup.append(('STREAMLIT_CLOUD_TOKEN', streamlit_token))
            self.config['secrets']['STREAMLIT_CLOUD_TOKEN']['value'] = streamlit_token
        
        success_count = 0
        for secret_name, secret_value in secrets_to_setup:
            if self.create_or_update_secret(secret_name, secret_value):
                success_count += 1
        
        # Save updated config (without actual secret values for security)
        config_to_save = self.config.copy()
        for secret_name in config_to_save['secrets']:
            if config_to_save['secrets'][secret_name]['value']:
                config_to_save['secrets'][secret_name]['value'] = "***CONFIGURED***"
        
        with open(self.config_file, 'w') as f:
            json.dump(config_to_save, f, indent=2)
        
        print(f"\n✅ Successfully configured {success_count}/{len(secrets_to_setup)} secrets")
        
        # Create environment file for local development
        env_file = self.project_root / ".env.local"
        with open(env_file, 'w') as f:
            f.write("# Local development environment variables\n")
            f.write("# DO NOT COMMIT THIS FILE\n\n")
            for key, value in self.config['environment_variables'].items():
                f.write(f"{key}={value}\n")
            f.write(f"\nDEPLOYMENT_WEBHOOK_SECRET={webhook_secret}\n")
            f.write(f"TRAE_AI_INTEGRATION_KEY={integration_key}\n")
        
        print(f"📄 Local environment file created: {env_file}")
        
        return success_count == len(secrets_to_setup)
    
    def validate_secrets(self):
        """Validate that all required secrets are configured"""
        print("🔍 Validating GitHub Secrets Configuration")
        print("=" * 45)
        
        secrets_list = self.list_repository_secrets()
        if not secrets_list:
            return False
        
        configured_secrets = {secret['name'] for secret in secrets_list}
        required_secrets = set(self.config['secrets'].keys())
        
        print("📋 Secret Status:")
        for secret_name in required_secrets:
            is_configured = secret_name in configured_secrets
            status = "✅" if is_configured else "❌"
            required = "Required" if self.config['secrets'][secret_name]['required'] else "Optional"
            print(f"{status} {secret_name} ({required})")
        
        missing_required = {
            name for name, config in self.config['secrets'].items()
            if config['required'] and name not in configured_secrets
        }
        
        if missing_required:
            print(f"\n❌ Missing required secrets: {missing_required}")
            return False
        else:
            print("\n✅ All required secrets are configured")
            return True
    
    def generate_deployment_instructions(self):
        """Generate deployment instructions with secrets"""
        instructions = {
            "github_setup": {
                "step_1": "Go to https://github.com/settings/tokens",
                "step_2": "Create a new personal access token",
                "step_3": "Select scopes: repo, workflow, admin:repo_hook",
                "step_4": "Set GITHUB_TOKEN environment variable"
            },
            "secrets_setup": {
                "command": "python github_secrets_setup.py setup",
                "description": "Automatically configure all deployment secrets"
            },
            "fast_deployment": {
                "command": "python trae_github_fast_deploy.py deploy",
                "description": "Deploy directly from Trae AI to GitHub to Streamlit Cloud"
            },
            "validation": {
                "command": "python github_secrets_setup.py validate",
                "description": "Validate all secrets are properly configured"
            }
        }
        
        with open('github_deployment_instructions.json', 'w') as f:
            json.dump(instructions, f, indent=2)
        
        return instructions
    
    def status(self):
        """Show secrets configuration status"""
        print("📊 GitHub Secrets Status")
        print("=" * 25)
        
        # Check GitHub token
        token_status = "✅" if self.get_github_token() else "❌"
        print(f"{token_status} GitHub Token")
        
        # Check repository access
        public_key = self.get_repository_public_key()
        repo_access = "✅" if public_key else "❌"
        print(f"{repo_access} Repository Access")
        
        # List configured secrets
        secrets_list = self.list_repository_secrets()
        if secrets_list:
            print(f"🔐 Configured Secrets: {len(secrets_list)}")
            for secret in secrets_list:
                print(f"  • {secret['name']} (updated: {secret['updated_at'][:10]})")
        else:
            print("🔐 Configured Secrets: 0")
        
        return True

def main():
    """Main function"""
    secrets_manager = GitHubSecretsManager()
    
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'setup':
            secrets_manager.setup_deployment_secrets()
        elif command == 'validate':
            secrets_manager.validate_secrets()
        elif command == 'status':
            secrets_manager.status()
        elif command == 'list':
            secrets = secrets_manager.list_repository_secrets()
            if secrets:
                print(json.dumps(secrets, indent=2))
        elif command == 'instructions':
            instructions = secrets_manager.generate_deployment_instructions()
            print(json.dumps(instructions, indent=2))
        else:
            print("Usage: python github_secrets_setup.py [setup|validate|status|list|instructions]")
    else:
        secrets_manager.setup_deployment_secrets()

if __name__ == "__main__":
    main()