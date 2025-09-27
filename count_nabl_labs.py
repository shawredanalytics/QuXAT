#!/usr/bin/env python3
"""
Count NABL Laboratories in Database
Provides accurate count of NABL laboratories in the unified healthcare organizations database
"""

import json
from pathlib import Path
from datetime import datetime

def count_nabl_labs():
    """Count NABL laboratories in the unified database"""
    
    # File paths
    unified_db_file = "unified_healthcare_organizations.json"
    
    try:
        # Load unified database
        print("📊 Counting NABL Laboratories in Database")
        print("=" * 50)
        
        with open(unified_db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        organizations = data.get('organizations', [])
        total_orgs = len(organizations)
        
        # Count NABL organizations
        nabl_count = 0
        nabl_only_count = 0
        nabl_with_other_certs = 0
        
        # Count by data source
        data_source_counts = {}
        
        for org in organizations:
            data_source = org.get('data_source', 'Unknown')
            data_source_counts[data_source] = data_source_counts.get(data_source, 0) + 1
            
            # Check if organization has NABL as data source
            if data_source == 'NABL':
                nabl_count += 1
                nabl_only_count += 1
            elif 'NABL' in data_source:
                nabl_count += 1
                nabl_with_other_certs += 1
        
        # Display results
        print(f"🏥 Total Organizations in Database: {total_orgs:,}")
        print(f"🧪 NABL Laboratories: {nabl_count:,}")
        print(f"   • NABL Only: {nabl_only_count:,}")
        print(f"   • NABL + Other Certifications: {nabl_with_other_certs:,}")
        
        print(f"\n📈 NABL Percentage: {(nabl_count/total_orgs)*100:.1f}% of total database")
        
        print(f"\n📋 Data Source Breakdown:")
        for source, count in sorted(data_source_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count/total_orgs)*100
            print(f"   • {source}: {count:,} ({percentage:.1f}%)")
        
        # Sample NABL organizations
        print(f"\n🔬 Sample NABL Laboratories:")
        nabl_orgs = [org for org in organizations if 'NABL' in org.get('data_source', '')]
        for i, org in enumerate(nabl_orgs[:5]):
            name = org.get('name', 'Unknown')
            location = org.get('location', 'Unknown')
            print(f"   {i+1}. {name} - {location}")
        
        if len(nabl_orgs) > 5:
            print(f"   ... and {len(nabl_orgs)-5:,} more NABL laboratories")
        
        # Summary
        print(f"\n" + "=" * 50)
        print(f"✅ NABL Laboratory Count: {nabl_count:,}")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            'total_organizations': total_orgs,
            'nabl_laboratories': nabl_count,
            'nabl_only': nabl_only_count,
            'nabl_with_others': nabl_with_other_certs,
            'percentage': (nabl_count/total_orgs)*100,
            'data_source_breakdown': data_source_counts
        }
        
    except FileNotFoundError:
        print(f"❌ Error: {unified_db_file} not found")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {unified_db_file}")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    count_nabl_labs()