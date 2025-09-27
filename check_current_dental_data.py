#!/usr/bin/env python3
"""
Check Current Dental Facilities Data Status
"""

import json
from datetime import datetime

def check_current_data():
    """Check current dental facilities data status"""
    
    print("=== NABH Dental Facilities Data Status ===\n")
    
    # Load current dental data
    try:
        print("Checking current dental facilities data...")
        with open('nabh_dental_facilities.json', 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        
        print(f'✅ Current dental facilities extracted: {len(current_data)}')
        if current_data:
            print(f'📅 Last extraction date: {current_data[0].get("extracted_date", "Unknown")}')
            
            # Check status distribution
            status_counts = {}
            for facility in current_data:
                status = facility.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f'\n📊 Status Distribution:')
            for status, count in status_counts.items():
                print(f'   {status}: {count}')
                
            # Sample facilities
            print(f'\n📋 Sample Facilities:')
            for i, facility in enumerate(current_data[:3]):
                print(f'   {i+1}. {facility.get("name", "Unknown")} - {facility.get("status", "Unknown")}')
        else:
            print('❌ No dental facilities data found')
            return False
            
    except FileNotFoundError:
        print('❌ nabh_dental_facilities.json not found')
        return False
    except Exception as e:
        print(f'❌ Error loading dental data: {e}')
        return False
        
    # Check integration status
    print("\n=== Integration Status ===")
    try:
        with open('unified_healthcare_organizations.json', 'r', encoding='utf-8') as f:
            unified_data = json.load(f)
        
        dental_facilities = [org for org in unified_data.get('organizations', []) 
                           if org.get('data_source') == 'NABH_Dental']
        
        print(f'✅ Dental facilities in unified database: {len(dental_facilities)}')
        
        if len(dental_facilities) == len(current_data):
            print('✅ All dental facilities are integrated')
            integration_status = True
        else:
            print(f'⚠️  Integration mismatch: {len(current_data)} extracted vs {len(dental_facilities)} integrated')
            integration_status = False
            
        # Check metadata
        metadata = unified_data.get('metadata', {})
        data_sources = metadata.get('data_sources', [])
        if 'NABH_Dental' in data_sources:
            print('✅ NABH_Dental is listed in data sources')
        else:
            print('⚠️  NABH_Dental not found in data sources')
            
        print(f'📊 Total organizations in database: {metadata.get("total_count", len(unified_data.get("organizations", [])))}')
        print(f'📅 Database last updated: {metadata.get("last_updated", "Unknown")}')
        
        return integration_status
            
    except FileNotFoundError:
        print('❌ unified_healthcare_organizations.json not found')
        return False
    except Exception as e:
        print(f'❌ Error checking unified database: {e}')
        return False

def check_streamlit_stats():
    """Check if Streamlit stats reflect dental integration"""
    print("\n=== Streamlit Application Status ===")
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for dental-related content
        if 'dental' in content.lower():
            print('✅ Dental references found in Streamlit app')
        else:
            print('⚠️  No dental references found in Streamlit app')
            
        # Look for updated statistics
        if '7,067' in content:
            print('✅ Updated total organizations count (7,067) found')
        else:
            print('⚠️  Updated total organizations count not found')
            
        if '4,561' in content:
            print('✅ Updated NABH facilities count (4,561) found')
        else:
            print('⚠️  Updated NABH facilities count not found')
            
    except Exception as e:
        print(f'❌ Error checking Streamlit app: {e}')

if __name__ == "__main__":
    integration_ok = check_current_data()
    check_streamlit_stats()
    
    print(f"\n=== Summary ===")
    if integration_ok:
        print("✅ Dental facilities are properly integrated")
        print("🎯 Ready to proceed with any additional updates")
    else:
        print("⚠️  Integration issues detected")
        print("🔧 May need to re-run integration process")