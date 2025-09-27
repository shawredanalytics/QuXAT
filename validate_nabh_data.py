"""
NABH Data Validation Script
Validates the quality and completeness of scraped NABH hospital data
"""

import json
from datetime import datetime

def validate_nabh_data():
    """Validate the scraped NABH hospital data"""
    try:
        # Load the scraped data
        with open('nabh_hospitals.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"NABH Data Validation Report")
        print(f"=" * 50)
        print(f"Total hospitals: {len(data)}")
        
        # Status breakdown
        status_counts = {}
        for hospital in data:
            status = hospital.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nStatus Breakdown:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Data quality checks
        with_names = sum(1 for h in data if h.get('name', '').strip())
        with_acc_no = sum(1 for h in data if h.get('accreditation_no', '').strip())
        with_ref_no = sum(1 for h in data if h.get('reference_no', '').strip())
        with_valid_dates = sum(1 for h in data if h.get('valid_from', '').strip() and h.get('valid_upto', '').strip())
        
        print(f"\nData Quality:")
        print(f"  Hospitals with names: {with_names} ({with_names/len(data)*100:.1f}%)")
        print(f"  Hospitals with accreditation numbers: {with_acc_no} ({with_acc_no/len(data)*100:.1f}%)")
        print(f"  Hospitals with reference numbers: {with_ref_no} ({with_ref_no/len(data)*100:.1f}%)")
        print(f"  Hospitals with valid dates: {with_valid_dates} ({with_valid_dates/len(data)*100:.1f}%)")
        
        # Sample hospitals
        print(f"\nSample Hospitals:")
        for i, hospital in enumerate(data[:5]):
            print(f"  {i+1}. {hospital.get('name', 'Unknown')} - {hospital.get('status', 'Unknown')}")
        
        # Check for duplicates
        names = [h.get('name', '') for h in data]
        unique_names = set(names)
        duplicates = len(names) - len(unique_names)
        
        print(f"\nDuplicate Check:")
        print(f"  Total names: {len(names)}")
        print(f"  Unique names: {len(unique_names)}")
        print(f"  Duplicates: {duplicates}")
        
        return True
        
    except Exception as e:
        print(f"Error validating data: {e}")
        return False

if __name__ == "__main__":
    validate_nabh_data()