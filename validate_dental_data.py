"""
NABH Dental Facilities Data Validation Script
Validates the quality and completeness of scraped NABH dental facilities data
"""

import json
from datetime import datetime

def validate_dental_data():
    """Validate the scraped NABH dental facilities data"""
    try:
        # Load the scraped data
        with open('nabh_dental_facilities.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"NABH Dental Facilities Data Validation Report")
        print(f"=" * 60)
        print(f"Total dental facilities: {len(data)}")
        
        # Status breakdown
        status_counts = {}
        for facility in data:
            status = facility.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\nStatus Breakdown:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        # Data quality checks
        with_names = sum(1 for f in data if f.get('name', '').strip())
        with_acc_no = sum(1 for f in data if f.get('accreditation_no', '').strip())
        with_ref_no = sum(1 for f in data if f.get('reference_no', '').strip())
        with_valid_dates = sum(1 for f in data if f.get('valid_from', '').strip() and f.get('valid_upto', '').strip())
        
        print(f"\nData Quality:")
        print(f"  Facilities with names: {with_names} ({with_names/len(data)*100:.1f}%)")
        print(f"  Facilities with accreditation numbers: {with_acc_no} ({with_acc_no/len(data)*100:.1f}%)")
        print(f"  Facilities with reference numbers: {with_ref_no} ({with_ref_no/len(data)*100:.1f}%)")
        print(f"  Facilities with valid dates: {with_valid_dates} ({with_valid_dates/len(data)*100:.1f}%)")
        
        # Sample facilities
        print(f"\nSample Dental Facilities:")
        for i, facility in enumerate(data[:5]):
            name = facility.get('name', 'Unknown')[:50] + "..." if len(facility.get('name', '')) > 50 else facility.get('name', 'Unknown')
            status = facility.get('status', 'Unknown')
            acc_no = facility.get('accreditation_no', 'N/A')
            print(f"  {i+1}. {name} ({status}) - {acc_no}")
        
        # Check for duplicates
        names = [f.get('name', '') for f in data if f.get('name', '')]
        unique_names = set(names)
        duplicates = len(names) - len(unique_names)
        
        print(f"\nDuplicate Analysis:")
        print(f"  Total facility names: {len(names)}")
        print(f"  Unique facility names: {len(unique_names)}")
        print(f"  Duplicate names: {duplicates}")
        
        # Country breakdown
        country_counts = {}
        for facility in data:
            country = facility.get('country', 'Unknown')
            country_counts[country] = country_counts.get(country, 0) + 1
        
        print(f"\nCountry Breakdown:")
        for country, count in country_counts.items():
            print(f"  {country}: {count}")
        
        # Facility type breakdown
        facility_type_counts = {}
        for facility in data:
            facility_type = facility.get('facility_type', 'Unknown')
            facility_type_counts[facility_type] = facility_type_counts.get(facility_type, 0) + 1
        
        print(f"\nFacility Type Breakdown:")
        for facility_type, count in facility_type_counts.items():
            print(f"  {facility_type}: {count}")
        
        # Accreditation type breakdown
        acc_type_counts = {}
        for facility in data:
            acc_type = facility.get('accreditation_type', 'Unknown')
            acc_type_counts[acc_type] = acc_type_counts.get(acc_type, 0) + 1
        
        print(f"\nAccreditation Type Breakdown:")
        for acc_type, count in acc_type_counts.items():
            print(f"  {acc_type}: {count}")
        
        print(f"\n" + "=" * 60)
        print(f"Validation completed successfully!")
        
        return {
            'total_facilities': len(data),
            'status_breakdown': status_counts,
            'data_quality': {
                'with_names': with_names,
                'with_accreditation_numbers': with_acc_no,
                'with_reference_numbers': with_ref_no,
                'with_valid_dates': with_valid_dates
            },
            'duplicates': duplicates,
            'country_breakdown': country_counts,
            'facility_type_breakdown': facility_type_counts,
            'accreditation_type_breakdown': acc_type_counts
        }
        
    except FileNotFoundError:
        print("Error: nabh_dental_facilities.json file not found!")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in nabh_dental_facilities.json!")
        return None
    except Exception as e:
        print(f"Error during validation: {str(e)}")
        return None

if __name__ == "__main__":
    validate_dental_data()