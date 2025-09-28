#!/usr/bin/env python3
"""
QuXAT Version Manager
Automated version management and fallback system for QuXAT Healthcare Scoring System
"""

import os
import shutil
import subprocess
import json
from datetime import datetime
from pathlib import Path

class QuXATVersionManager:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.versions = {
            'current': 'streamlit_app.py',
            'v1.1_stable': 'streamlit_app_v1.1_stable.py',
            'v1.0_backup': 'streamlit_app_v1.0.py',
            'emergency': 'streamlit_app_backup.py'
        }
        
    def check_file_exists(self, filename):
        """Check if a version file exists"""
        return (self.base_dir / filename).exists()
    
    def create_backup(self, source='current', backup_name=None):
        """Create a backup of the specified version"""
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"streamlit_app_backup_{timestamp}.py"
        
        source_file = self.versions.get(source, source)
        
        if not self.check_file_exists(source_file):
            print(f"❌ Source file {source_file} not found!")
            return False
        
        try:
            shutil.copy2(source_file, backup_name)
            print(f"✅ Backup created: {backup_name}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def fallback_to_version(self, version_key, commit_message=None):
        """Fallback to a specific version"""
        if version_key not in self.versions:
            print(f"❌ Unknown version: {version_key}")
            return False
        
        source_file = self.versions[version_key]
        target_file = self.versions['current']
        
        if not self.check_file_exists(source_file):
            print(f"❌ Version file {source_file} not found!")
            return False
        
        try:
            # Create backup of current version first
            self.create_backup('current', f"streamlit_app_pre_fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
            
            # Copy version file to current
            shutil.copy2(source_file, target_file)
            print(f"✅ Fallback completed: {source_file} → {target_file}")
            
            # Git operations
            if commit_message is None:
                commit_message = f"🔄 Fallback to {version_key} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.git_commit_and_push(target_file, commit_message)
            return True
            
        except Exception as e:
            print(f"❌ Fallback failed: {e}")
            return False
    
    def git_commit_and_push(self, filename, message):
        """Commit and push changes to Git"""
        try:
            subprocess.run(['git', 'add', filename], check=True)
            subprocess.run(['git', 'commit', '-m', message], check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print(f"✅ Git operations completed: {message}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git operation failed: {e}")
    
    def check_deployment_status(self):
        """Check current deployment status"""
        try:
            result = subprocess.run(['python', 'check_deployment_status.py'], 
                                  capture_output=True, text=True, check=True)
            print("📊 Deployment Status:")
            print(result.stdout)
            return "✅" in result.stdout
        except Exception as e:
            print(f"❌ Deployment check failed: {e}")
            return False
    
    def list_versions(self):
        """List all available versions"""
        print("📁 Available Versions:")
        for key, filename in self.versions.items():
            status = "✅" if self.check_file_exists(filename) else "❌"
            print(f"  {status} {key}: {filename}")
    
    def health_check(self):
        """Perform comprehensive health check"""
        print("🔍 QuXAT Health Check")
        print("=" * 50)
        
        # Check version files
        print("\n📁 Version Files:")
        for key, filename in self.versions.items():
            exists = self.check_file_exists(filename)
            status = "✅" if exists else "❌"
            print(f"  {status} {key}: {filename}")
        
        # Check database file
        db_file = "unified_healthcare_organizations.json"
        db_exists = self.check_file_exists(db_file)
        print(f"\n💾 Database: {'✅' if db_exists else '❌'} {db_file}")
        
        # Check deployment
        print("\n🌐 Deployment Status:")
        deployment_ok = self.check_deployment_status()
        
        return all([
            self.check_file_exists(self.versions['current']),
            self.check_file_exists(self.versions['v1.1_stable']),
            db_exists
        ])
    
    def emergency_restore(self):
        """Emergency restore procedure"""
        print("🚨 EMERGENCY RESTORE PROCEDURE")
        print("=" * 50)
        
        # Try fallback sequence
        fallback_sequence = ['v1.1_stable', 'v1.0_backup', 'emergency']
        
        for version in fallback_sequence:
            print(f"\n🔄 Attempting fallback to {version}...")
            if self.fallback_to_version(version, f"🚨 Emergency fallback to {version}"):
                print(f"✅ Emergency restore successful: {version}")
                return True
            else:
                print(f"❌ Fallback to {version} failed")
        
        print("🚨 ALL FALLBACK OPTIONS EXHAUSTED!")
        print("Manual intervention required.")
        return False

def main():
    """Main CLI interface"""
    import sys
    
    manager = QuXATVersionManager()
    
    if len(sys.argv) < 2:
        print("QuXAT Version Manager")
        print("Usage:")
        print("  python version_manager.py health          - Health check")
        print("  python version_manager.py list            - List versions")
        print("  python version_manager.py fallback <ver>  - Fallback to version")
        print("  python version_manager.py backup          - Create backup")
        print("  python version_manager.py emergency       - Emergency restore")
        print("  python version_manager.py deploy-check    - Check deployment")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'health':
        success = manager.health_check()
        print(f"\n🏥 Overall Health: {'✅ HEALTHY' if success else '❌ ISSUES DETECTED'}")
    
    elif command == 'list':
        manager.list_versions()
    
    elif command == 'fallback':
        if len(sys.argv) < 3:
            print("❌ Please specify version key (v1.1_stable, v1.0_backup, emergency)")
            return
        version = sys.argv[2]
        manager.fallback_to_version(version)
    
    elif command == 'backup':
        manager.create_backup()
    
    elif command == 'emergency':
        manager.emergency_restore()
    
    elif command == 'deploy-check':
        manager.check_deployment_status()
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()