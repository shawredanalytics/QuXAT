#!/usr/bin/env python3
"""
Quick test to verify database loading for Streamlit app
"""

import json
import os

def test_database_loading():
    """Test that the database loads correctly"""
    
    # Check if database file exists
    db_file = 'unified_healthcare_organizations.json'
    if not os.path.exists(db_file):
        print(f"❌ Database file {db_file} not found!")
        return False
    
    try:
        # Load the database
        with open(db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)
        
        # Check structure
        if 'organizations' not in db:
            print("❌ Database missing 'organizations' key!")
            return False
            
        if 'metadata' not in db:
            print("❌ Database missing 'metadata' key!")
            return False
        
        # Get counts
        org_count = len(db['organizations'])
        metadata_total = db['metadata'].get('total_organizations', 0)
        
        print(f"✅ Database loaded successfully!")
        print(f"   Organizations in list: {org_count:,}")
        print(f"   Metadata total: {metadata_total:,}")
        
        # Check for NABH hospitals
        nabh_count = 0
        updated_nabh_count = 0
        
        for org in db['organizations']:
            if isinstance(org, dict):
                # Check for NABH certification
                certifications = org.get('certifications', [])
                if isinstance(certifications, list):
                    for cert in certifications:
                        if isinstance(cert, dict) and cert.get('type') == 'NABH':
                            nabh_count += 1
                            break
                
                # Check for updated NABH source
                data_source = org.get('data_source', '')
                if 'Updated_NABH_Portal' in data_source:
                    updated_nabh_count += 1
        
        print(f"   NABH certified hospitals: {nabh_count:,}")
        print(f"   Updated NABH hospitals: {updated_nabh_count:,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return False

if __name__ == "__main__":
    test_database_loading()