#!/usr/bin/env python3
"""
End-to-End Workflow Test for QuXAT GitHub-Streamlit Integration
Tests the complete workflow from code change to live deployment
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

class EndToEndWorkflowTest:
    def __init__(self):
        self.project_root = Path.cwd()
        self.app_url = "https://quxatscore.streamlit.app/"
        self.repo_name = "shawredanalytics/QuXAT"
        self.test_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n🚀 {title}")
        print("=" * (len(title) + 4))
        
    def run_command(self, cmd, capture_output=True):
        """Run shell command and return result"""
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
            else:
                result = subprocess.run(cmd, shell=True)
                return result.returncode == 0, "", ""
        except Exception as e:
            return False, "", str(e)
    
    def check_app_accessibility(self):
        """Check if the Streamlit app is accessible"""
        try:
            response = requests.get(self.app_url, timeout=10)
            return response.status_code == 200, response.elapsed.total_seconds()
        except Exception as e:
            return False, 0
    
    def make_test_change(self):
        """Make a test change to the application"""
        self.print_header("Making Test Change")
        
        # Read current streamlit_app.py
        app_file = self.project_root / "streamlit_app.py"
        if not app_file.exists():
            print("❌ streamlit_app.py not found")
            return False
            
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add a test comment with timestamp
        test_comment = f"# Test deployment {self.test_timestamp}\n"
        
        # Insert test comment at the beginning
        modified_content = test_comment + content
        
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✅ Test comment added to streamlit_app.py")
        return True
    
    def commit_and_push_changes(self):
        """Commit and push changes to GitHub"""
        self.print_header("Committing and Pushing Changes")
        
        # Add changes
        success, stdout, stderr = self.run_command("git add .")
        if not success:
            print(f"❌ Failed to add changes: {stderr}")
            return False
        
        # Commit changes
        commit_msg = f"Test deployment workflow {self.test_timestamp}"
        success, stdout, stderr = self.run_command(f'git commit -m "{commit_msg}"')
        if not success:
            print(f"❌ Failed to commit changes: {stderr}")
            return False
        
        print(f"✅ Changes committed: {commit_msg}")
        
        # Push changes
        success, stdout, stderr = self.run_command("git push origin main")
        if not success:
            print(f"❌ Failed to push changes: {stderr}")
            return False
        
        print("✅ Changes pushed to GitHub")
        return True
    
    def monitor_deployment(self, max_wait_minutes=10):
        """Monitor deployment progress"""
        self.print_header(f"Monitoring Deployment (max {max_wait_minutes} minutes)")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        # Initial accessibility check
        initial_accessible, initial_time = self.check_app_accessibility()
        print(f"🔍 Initial app status: {'✅ Accessible' if initial_accessible else '❌ Not accessible'}")
        
        deployment_detected = False
        deployment_start_time = None
        
        while time.time() - start_time < max_wait_seconds:
            elapsed = int(time.time() - start_time)
            
            accessible, response_time = self.check_app_accessibility()
            
            if accessible:
                if not deployment_detected:
                    deployment_detected = True
                    deployment_start_time = time.time()
                    print(f"🎯 Deployment detected at {elapsed}s")
                
                # Check if deployment is complete (stable response)
                if deployment_detected and time.time() - deployment_start_time > 5:
                    deployment_time = int(time.time() - start_time)
                    print(f"🎉 Deployment completed in {deployment_time}s ({deployment_time/60:.1f} minutes)")
                    return True, deployment_time
            
            print(f"🔍 Checking deployment status... ({elapsed}s elapsed)")
            time.sleep(10)  # Check every 10 seconds
        
        print(f"⏰ Deployment monitoring timeout after {max_wait_minutes} minutes")
        return False, max_wait_seconds
    
    def cleanup_test_changes(self):
        """Remove test changes"""
        self.print_header("Cleaning Up Test Changes")
        
        # Read current streamlit_app.py
        app_file = self.project_root / "streamlit_app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove test comment
        lines = content.split('\n')
        if lines[0].startswith(f"# Test deployment {self.test_timestamp}"):
            lines = lines[1:]  # Remove first line
            
            with open(app_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print("✅ Test comment removed from streamlit_app.py")
            
            # Commit cleanup
            self.run_command("git add .")
            commit_msg = f"Cleanup: Remove test comment {self.test_timestamp}"
            self.run_command(f'git commit -m "{commit_msg}"')
            self.run_command("git push origin main")
            print("✅ Cleanup changes committed and pushed")
            return True
        
        print("⚠️ No test comment found to remove")
        return False
    
    def generate_report(self, results):
        """Generate test report"""
        report = {
            "timestamp": self.test_timestamp,
            "test_type": "end_to_end_workflow",
            "app_url": self.app_url,
            "repository": self.repo_name,
            "results": results,
            "summary": {
                "total_time_seconds": results.get("total_time", 0),
                "deployment_time_seconds": results.get("deployment_time", 0),
                "success": results.get("workflow_success", False)
            }
        }
        
        report_file = self.project_root / f"end_to_end_test_report_{self.test_timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Full report saved: {report_file}")
        return report
    
    def run_full_test(self):
        """Run complete end-to-end workflow test"""
        print("🚀 QuXAT End-to-End Workflow Test")
        print("=" * 40)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 App URL: {self.app_url}")
        print(f"📦 Repository: {self.repo_name}")
        
        start_time = time.time()
        results = {}
        
        # Step 1: Check initial app status
        initial_accessible, initial_time = self.check_app_accessibility()
        results["initial_app_accessible"] = initial_accessible
        results["initial_response_time"] = initial_time
        
        if not initial_accessible:
            print("❌ App not initially accessible - cannot proceed with test")
            return self.generate_report(results)
        
        # Step 2: Make test change
        if not self.make_test_change():
            results["test_change_made"] = False
            return self.generate_report(results)
        results["test_change_made"] = True
        
        # Step 3: Commit and push
        if not self.commit_and_push_changes():
            results["changes_pushed"] = False
            return self.generate_report(results)
        results["changes_pushed"] = True
        
        # Step 4: Monitor deployment
        deployment_success, deployment_time = self.monitor_deployment()
        results["deployment_successful"] = deployment_success
        results["deployment_time"] = deployment_time
        
        # Step 5: Cleanup
        cleanup_success = self.cleanup_test_changes()
        results["cleanup_successful"] = cleanup_success
        
        # Calculate total time
        total_time = int(time.time() - start_time)
        results["total_time"] = total_time
        
        # Determine overall success
        workflow_success = all([
            results["initial_app_accessible"],
            results["test_change_made"],
            results["changes_pushed"],
            results["deployment_successful"]
        ])
        results["workflow_success"] = workflow_success
        
        # Print summary
        self.print_header("Test Results Summary")
        print(f"✅ Initial App Accessible: {results['initial_app_accessible']}")
        print(f"✅ Test Change Made: {results['test_change_made']}")
        print(f"✅ Changes Pushed: {results['changes_pushed']}")
        print(f"✅ Deployment Successful: {results['deployment_successful']}")
        print(f"✅ Cleanup Successful: {results['cleanup_successful']}")
        print(f"⏱️ Total Test Time: {total_time}s ({total_time/60:.1f} minutes)")
        print(f"⏱️ Deployment Time: {deployment_time}s ({deployment_time/60:.1f} minutes)")
        
        status_icon = "✅" if workflow_success else "❌"
        print(f"\n🔗 End-to-End Workflow: {status_icon} {'SUCCESS' if workflow_success else 'FAILED'}")
        
        if workflow_success:
            print(f"🎉 GitHub to Streamlit integration is working perfectly!")
            print(f"💡 Code changes are deployed live in ~{deployment_time//60} minutes")
        
        return self.generate_report(results)

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        tester = EndToEndWorkflowTest()
        
        if command == "quick":
            # Quick accessibility test
            accessible, response_time = tester.check_app_accessibility()
            print(f"🌐 App Status: {'✅ Live' if accessible else '❌ Down'}")
            if accessible:
                print(f"📊 Response time: {response_time:.2f}s")
        
        elif command == "full":
            # Full end-to-end test
            tester.run_full_test()
        
        else:
            print("Usage: python end_to_end_workflow_test.py [quick|full]")
            print("  quick - Test app accessibility only")
            print("  full  - Complete end-to-end workflow test")
    
    else:
        # Default to full test
        tester = EndToEndWorkflowTest()
        tester.run_full_test()

if __name__ == "__main__":
    main()