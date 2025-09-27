#!/usr/bin/env python3
"""
Robust Database Analyzer for QuXAT Healthcare Organizations
Handles mixed data types and provides comprehensive integration verification
"""

import json
import os
from datetime import datetime
from collections import defaultdict, Counter

def load_database(file_path):
    """Load the unified healthcare organizations database"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading database: {e}")
        return None

def safe_get_attribute(obj, key, default="Unknown"):
    """Safely get attribute from object, handling both dict and string types"""
    if isinstance(obj, dict):
        return obj.get(key, default)
    elif isinstance(obj, str):
        # If it's a string, we can't extract attributes
        return default
    else:
        return default

def analyze_organization_types(organizations):
    """Analyze the types of objects in the organizations list"""
    type_counts = Counter()
    string_samples = []
    
    for i, org in enumerate(organizations):
        obj_type = type(org).__name__
        type_counts[obj_type] += 1
        
        # Collect samples of string entries for analysis
        if isinstance(org, str) and len(string_samples) < 5:
            string_samples.append(f"Index {i}: {org[:100]}...")
    
    return type_counts, string_samples

def analyze_database_comprehensive(db_data):
    """Comprehensive analysis of the database"""
    if not db_data:
        return None
    
    organizations = db_data.get('organizations', [])
    metadata = db_data.get('metadata', {})
    
    # Analyze object types
    type_counts, string_samples = analyze_organization_types(organizations)
    
    # Initialize counters
    stats = {
        'total_organizations': len(organizations),
        'valid_dict_organizations': 0,
        'string_entries': 0,
        'countries': defaultdict(int),
        'sources': defaultdict(int),
        'nabh_hospitals': 0,
        'updated_nabh_hospitals': 0,
        'jci_hospitals': 0,
        'nabl_labs': 0,
        'cap_labs': 0,
        'certification_counts': defaultdict(int),
        'data_quality_issues': []
    }
    
    # Process only dictionary entries
    for i, org in enumerate(organizations):
        if isinstance(org, dict):
            stats['valid_dict_organizations'] += 1
            
            # Country analysis
            country = safe_get_attribute(org, 'country', 'Unknown')
            stats['countries'][country] += 1
            
            # Source analysis
            source = safe_get_attribute(org, 'source', 'Unknown')
            stats['sources'][source] += 1
            
            # Certification analysis
            certifications = org.get('certifications', [])
            if isinstance(certifications, list):
                for cert in certifications:
                    if isinstance(cert, dict):
                        cert_type = cert.get('type', 'Unknown')
                        stats['certification_counts'][cert_type] += 1
                        
                        # Count specific certification types
                        if 'nabh' in cert_type.lower():
                            stats['nabh_hospitals'] += 1
                            # Check if it's from updated NABH data
                            data_source = safe_get_attribute(org, 'data_source', '')
                            if ('updated_nabh' in source.lower() or 
                                'nabh_entry_level' in source.lower() or
                                'Updated_NABH_Portal' in data_source):
                                stats['updated_nabh_hospitals'] += 1
                        elif 'jci' in cert_type.lower():
                            stats['jci_hospitals'] += 1
                        elif 'nabl' in cert_type.lower():
                            stats['nabl_labs'] += 1
                        elif 'cap' in cert_type.lower():
                            stats['cap_labs'] += 1
        
        elif isinstance(org, str):
            stats['string_entries'] += 1
            stats['data_quality_issues'].append(f"String entry at index {i}: {org[:50]}...")
    
    # Add type analysis to stats
    stats['object_types'] = dict(type_counts)
    stats['string_samples'] = string_samples
    
    # Metadata analysis
    stats['metadata'] = {
        'last_updated': metadata.get('last_updated', 'Unknown'),
        'data_sources': metadata.get('data_sources', []),
        'total_sources': len(metadata.get('data_sources', [])),
        'integration_stats': metadata.get('integration_stats', {})
    }
    
    return stats

def generate_analysis_report(stats, output_file):
    """Generate a comprehensive analysis report"""
    if not stats:
        print("No statistics to report")
        return
    
    report = {
        'analysis_timestamp': datetime.now().isoformat(),
        'database_overview': {
            'total_entries': stats['total_organizations'],
            'valid_organizations': stats['valid_dict_organizations'],
            'corrupted_entries': stats['string_entries'],
            'data_integrity_percentage': round((stats['valid_dict_organizations'] / stats['total_organizations']) * 100, 2) if stats['total_organizations'] > 0 else 0
        },
        'object_type_distribution': stats['object_types'],
        'geographic_distribution': dict(sorted(stats['countries'].items(), key=lambda x: x[1], reverse=True)[:10]),
        'data_source_distribution': dict(sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True)),
        'certification_analysis': {
            'nabh_hospitals': stats['nabh_hospitals'],
            'updated_nabh_hospitals': stats['updated_nabh_hospitals'],
            'jci_hospitals': stats['jci_hospitals'],
            'nabl_laboratories': stats['nabl_labs'],
            'cap_laboratories': stats['cap_labs'],
            'certification_types': dict(sorted(stats['certification_counts'].items(), key=lambda x: x[1], reverse=True))
        },
        'data_quality_assessment': {
            'corrupted_entries_count': len(stats['data_quality_issues']),
            'sample_corrupted_entries': stats['string_samples'][:3],
            'data_integrity_score': 'Good' if stats['valid_dict_organizations'] / stats['total_organizations'] > 0.95 else 'Needs Attention'
        },
        'metadata_info': stats['metadata'],
        'recommendations': []
    }
    
    # Add recommendations based on analysis
    if stats['string_entries'] > 0:
        report['recommendations'].append(f"Clean up {stats['string_entries']} corrupted string entries in the database")
    
    if stats['updated_nabh_hospitals'] > 0:
        report['recommendations'].append(f"Successfully integrated {stats['updated_nabh_hospitals']} updated NABH hospitals")
    
    if report['database_overview']['data_integrity_percentage'] < 95:
        report['recommendations'].append("Database integrity is below 95% - consider data cleanup")
    
    # Save report
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

def print_summary(stats):
    """Print a summary of the analysis"""
    if not stats:
        print("No data to analyze")
        return
    
    print("\n" + "="*60)
    print("DATABASE ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\n📊 OVERVIEW:")
    print(f"   Total Entries: {stats['total_organizations']:,}")
    print(f"   Valid Organizations: {stats['valid_dict_organizations']:,}")
    print(f"   Corrupted Entries: {stats['string_entries']:,}")
    
    if stats['total_organizations'] > 0:
        integrity = (stats['valid_dict_organizations'] / stats['total_organizations']) * 100
        print(f"   Data Integrity: {integrity:.1f}%")
    
    print(f"\n🏥 HEALTHCARE ORGANIZATIONS:")
    print(f"   NABH Hospitals: {stats['nabh_hospitals']:,}")
    print(f"   Updated NABH Hospitals: {stats['updated_nabh_hospitals']:,}")
    print(f"   JCI Hospitals: {stats['jci_hospitals']:,}")
    print(f"   NABL Laboratories: {stats['nabl_labs']:,}")
    print(f"   CAP Laboratories: {stats['cap_labs']:,}")
    
    print(f"\n🌍 TOP COUNTRIES:")
    for country, count in list(stats['countries'].items())[:5]:
        print(f"   {country}: {count:,}")
    
    print(f"\n📋 DATA SOURCES:")
    for source, count in list(stats['sources'].items())[:5]:
        print(f"   {source}: {count:,}")
    
    if stats['string_entries'] > 0:
        print(f"\n⚠️  DATA QUALITY ISSUES:")
        print(f"   Found {stats['string_entries']} corrupted entries")
        print("   Sample corrupted entries:")
        for sample in stats['string_samples'][:3]:
            print(f"   - {sample}")
    
    print("\n" + "="*60)

def main():
    """Main analysis function"""
    database_file = "unified_healthcare_organizations.json"
    
    if not os.path.exists(database_file):
        print(f"Database file {database_file} not found!")
        return
    
    print("Loading database...")
    db_data = load_database(database_file)
    
    if not db_data:
        print("Failed to load database")
        return
    
    print("Analyzing database...")
    stats = analyze_database_comprehensive(db_data)
    
    if not stats:
        print("Failed to analyze database")
        return
    
    # Print summary
    print_summary(stats)
    
    # Generate detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"database_analysis_report_{timestamp}.json"
    
    print(f"\nGenerating detailed report: {report_file}")
    report = generate_analysis_report(stats, report_file)
    
    if report:
        print(f"✅ Analysis complete! Report saved to {report_file}")
        
        # Show integration success
        if stats['updated_nabh_hospitals'] > 0:
            print(f"\n🎉 INTEGRATION SUCCESS:")
            print(f"   Successfully integrated {stats['updated_nabh_hospitals']} updated NABH hospitals!")
            print(f"   Total NABH hospitals in database: {stats['nabh_hospitals']}")
    else:
        print("❌ Failed to generate report")

if __name__ == "__main__":
    main()