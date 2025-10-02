#!/usr/bin/env python3
"""
Check database contents and search functionality
"""

import json

def check_database():
    """Check the unified database contents"""
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Database Structure Analysis")
        print("=" * 40)
        
        # Check if it's the new format with metadata and organizations
        if 'organizations' in data:
            orgs = data['organizations']
            print(f"Total organizations: {len(orgs)}")
            
            print("\nFirst 5 organizations:")
            for i, org in enumerate(orgs[:5]):
                print(f"{i+1}. {org.get('name', 'Unknown')}")
            
            # Search for Apollo organizations
            apollo_orgs = [org for org in orgs if 'apollo' in org.get('name', '').lower()]
            print(f"\nFound {len(apollo_orgs)} Apollo organizations:")
            for org in apollo_orgs[:5]:
                print(f"- {org.get('name', 'Unknown')}")
                
        else:
            # Old format - direct list
            print(f"Total organizations (old format): {len(data)}")
            
            print("\nFirst 5 organizations:")
            for i, org in enumerate(data[:5]):
                print(f"{i+1}. {org.get('name', 'Unknown')}")
            
            # Search for Apollo organizations
            apollo_orgs = [org for org in data if 'apollo' in org.get('name', '').lower()]
            print(f"\nFound {len(apollo_orgs)} Apollo organizations:")
            for org in apollo_orgs[:5]:
                print(f"- {org.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    check_database()