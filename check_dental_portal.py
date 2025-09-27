#!/usr/bin/env python3
"""
Check NABH Dental Portal Status and Current Data
"""

import requests
from datetime import datetime
import json

def check_portal_and_data():
    """Check portal accessibility and current data status"""
    
    # Check if we can access the NABH dental portal
    url = 'https://portal.nabh.co/frmViewApplicantDentalFacilities.aspx'
    try:
        print("Checking NABH Dental Portal...")
        response = requests.get(url, timeout=10)
        print(f'Portal Status: {response.status_code}')
        print(f'Portal accessible: {response.status_code == 200}')
        
        # Load current data to check count
        print("\nChecking current dental facilities data...")
        with open('nabh_dental_facilities.json', 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        
        print(f'Current dental facilities in database: {len(current_data)}')
        if current_data:
            print(f'Last extraction date: {current_data[0].get("extracted_date", "Unknown")}')
            
            # Check status distribution
            status_counts = {}
            for facility in current_data:
                status = facility.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f'\nStatus Distribution:')
            for status, count in status_counts.items():
                print(f'  {status}: {count}')
        else:
            print('No dental facilities data found')
            
        # Check integration status
        print("\nChecking integration status...")
        try:
            with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
                unified_data = json.load(f)
            
            dental_facilities = [org for org in unified_data.get('organizations', []) 
                               if org.get('data_source') == 'NABH_Dental']
            
            print(f'Dental facilities in unified database: {len(dental_facilities)}')
            
            if len(dental_facilities) == len(current_data):
                print('✅ All dental facilities are integrated')
            else:
                print(f'⚠️  Integration mismatch: {len(current_data)} extracted vs {len(dental_facilities)} integrated')
                
        except Exception as e:
            print(f'Error checking unified database: {e}')
        
    except Exception as e:
        print(f'Error accessing portal: {e}')

if __name__ == "__main__":
    check_portal_and_data()