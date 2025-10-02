#!/usr/bin/env python3
"""
QuXAT Accreditation Validation Report Generator
==============================================

This script generates a comprehensive validation report showing the accuracy and 
integration status of all accreditation data before QuXAT scoring.

Author: QuXAT Development Team
Date: September 29, 2025
Version: 1.0
"""

import json
import logging
from datetime import datetime
from collections import defaultdict, Counter
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AccreditationValidationReporter:
    """Generate comprehensive validation reports for accreditation data"""
    
    def __init__(self, database_path="unified_healthcare_organizations.json"):
        self.database_path = database_path
        self.organizations = []
        self.validation_results = {}
        self.load_database()
    
    def load_database(self):
        """Load the unified healthcare organizations database"""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                self.organizations = json.load(f)
            logger.info(f"Loaded {len(self.organizations)} organizations from database")
        except FileNotFoundError:
            logger.error(f"Database file not found: {self.database_path}")
            self.organizations = []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON database: {e}")
            self.organizations = []
    
    def validate_accreditation_data(self):
        """Validate all accreditation data in the database"""
        logger.info("Starting comprehensive accreditation validation...")
        
        # Initialize validation counters
        validation_stats = {
            'total_organizations': len(self.organizations),
            'organizations_with_certifications': 0,
            'organizations_without_certifications': 0,
            'total_certifications': 0,
            'certification_types': defaultdict(int),
            'certification_status_distribution': defaultdict(int),
            'countries_with_accreditations': set(),
            'accreditation_by_country': defaultdict(lambda: defaultdict(int)),
            'validation_issues': [],
            'data_quality_metrics': {
                'complete_certification_data': 0,
                'missing_certification_names': 0,
                'missing_certification_status': 0,
                'missing_certification_types': 0,
                'invalid_dates': 0
            }
        }
        
        # Validate each organization
        for i, org in enumerate(self.organizations):
            org_name = org.get('name', f'Organization_{i}')
            country = org.get('country', 'Unknown')
            certifications = org.get('certifications', [])
            
            if certifications and len(certifications) > 0:
                validation_stats['organizations_with_certifications'] += 1
                validation_stats['countries_with_accreditations'].add(country)
                
                # Validate each certification
                for cert in certifications:
                    validation_stats['total_certifications'] += 1
                    
                    # Check certification completeness
                    cert_name = cert.get('name', '')
                    cert_type = cert.get('type', '')
                    cert_status = cert.get('status', '')
                    
                    if cert_name and cert_type and cert_status:
                        validation_stats['data_quality_metrics']['complete_certification_data'] += 1
                    
                    if not cert_name:
                        validation_stats['data_quality_metrics']['missing_certification_names'] += 1
                        validation_stats['validation_issues'].append({
                            'organization': org_name,
                            'issue': 'Missing certification name',
                            'certification': cert
                        })
                    
                    if not cert_status:
                        validation_stats['data_quality_metrics']['missing_certification_status'] += 1
                        validation_stats['validation_issues'].append({
                            'organization': org_name,
                            'issue': 'Missing certification status',
                            'certification': cert
                        })
                    
                    if not cert_type:
                        validation_stats['data_quality_metrics']['missing_certification_types'] += 1
                        validation_stats['validation_issues'].append({
                            'organization': org_name,
                            'issue': 'Missing certification type',
                            'certification': cert
                        })
                    
                    # Count certification types and statuses
                    if cert_type:
                        validation_stats['certification_types'][cert_type] += 1
                        validation_stats['accreditation_by_country'][country][cert_type] += 1
                    
                    if cert_status:
                        validation_stats['certification_status_distribution'][cert_status] += 1
                    
                    # Validate dates if present
                    for date_field in ['accreditation_date', 'expiry_date']:
                        if date_field in cert and cert[date_field]:
                            try:
                                # Try to parse the date
                                datetime.strptime(cert[date_field], '%Y-%m-%d')
                            except (ValueError, TypeError):
                                validation_stats['data_quality_metrics']['invalid_dates'] += 1
                                validation_stats['validation_issues'].append({
                                    'organization': org_name,
                                    'issue': f'Invalid date format in {date_field}',
                                    'certification': cert
                                })
            else:
                validation_stats['organizations_without_certifications'] += 1
        
        # Convert sets to lists for JSON serialization
        validation_stats['countries_with_accreditations'] = list(validation_stats['countries_with_accreditations'])
        
        self.validation_results = validation_stats
        logger.info("Accreditation validation completed")
        
        return validation_stats
    
    def analyze_accreditation_coverage(self):
        """Analyze accreditation coverage by type and region"""
        logger.info("Analyzing accreditation coverage...")
        
        coverage_analysis = {
            'jci_accreditation': {
                'total_count': 0,
                'organizations': [],
                'countries': set()
            },
            'nabh_accreditation': {
                'total_count': 0,
                'organizations': [],
                'countries': set()
            },
            'nabl_accreditation': {
                'total_count': 0,
                'organizations': [],
                'countries': set()
            },
            'cap_accreditation': {
                'total_count': 0,
                'organizations': [],
                'countries': set()
            },
            'iso_certifications': {
                'total_count': 0,
                'organizations': [],
                'countries': set(),
                'iso_types': defaultdict(int)
            }
        }
        
        # Analyze each organization
        for org in self.organizations:
            org_name = org.get('name', 'Unknown')
            country = org.get('country', 'Unknown')
            certifications = org.get('certifications', [])
            
            for cert in certifications:
                cert_name = cert.get('name', '').upper()
                cert_type = cert.get('type', '').upper()
                
                # Check for JCI accreditation
                if 'JCI' in cert_name or 'JOINT COMMISSION' in cert_name or 'JCI ACCREDITATION' in cert_type:
                    coverage_analysis['jci_accreditation']['total_count'] += 1
                    coverage_analysis['jci_accreditation']['organizations'].append({
                        'name': org_name,
                        'country': country,
                        'certification': cert
                    })
                    coverage_analysis['jci_accreditation']['countries'].add(country)
                
                # Check for NABH accreditation
                if 'NABH' in cert_name or 'NATIONAL ACCREDITATION BOARD' in cert_name:
                    coverage_analysis['nabh_accreditation']['total_count'] += 1
                    coverage_analysis['nabh_accreditation']['organizations'].append({
                        'name': org_name,
                        'country': country,
                        'certification': cert
                    })
                    coverage_analysis['nabh_accreditation']['countries'].add(country)
                
                # Check for NABL accreditation
                if 'NABL' in cert_name or 'NATIONAL ACCREDITATION BOARD FOR TESTING AND CALIBRATION LABORATORIES' in cert_name:
                    coverage_analysis['nabl_accreditation']['total_count'] += 1
                    coverage_analysis['nabl_accreditation']['organizations'].append({
                        'name': org_name,
                        'country': country,
                        'certification': cert
                    })
                    coverage_analysis['nabl_accreditation']['countries'].add(country)
                
                # Check for CAP accreditation
                if 'CAP' in cert_name or 'COLLEGE OF AMERICAN PATHOLOGISTS' in cert_name:
                    coverage_analysis['cap_accreditation']['total_count'] += 1
                    coverage_analysis['cap_accreditation']['organizations'].append({
                        'name': org_name,
                        'country': country,
                        'certification': cert
                    })
                    coverage_analysis['cap_accreditation']['countries'].add(country)
                
                # Check for ISO certifications
                if 'ISO' in cert_name:
                    coverage_analysis['iso_certifications']['total_count'] += 1
                    coverage_analysis['iso_certifications']['organizations'].append({
                        'name': org_name,
                        'country': country,
                        'certification': cert
                    })
                    coverage_analysis['iso_certifications']['countries'].add(country)
                    
                    # Extract ISO standard number
                    import re
                    iso_match = re.search(r'ISO\s*(\d+)', cert_name)
                    if iso_match:
                        iso_standard = f"ISO {iso_match.group(1)}"
                        coverage_analysis['iso_certifications']['iso_types'][iso_standard] += 1
        
        # Convert sets to lists for JSON serialization
        for accred_type in coverage_analysis:
            if 'countries' in coverage_analysis[accred_type]:
                coverage_analysis[accred_type]['countries'] = list(coverage_analysis[accred_type]['countries'])
        
        return coverage_analysis
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        logger.info("Generating comprehensive validation report...")
        
        # Run validation and analysis
        validation_stats = self.validate_accreditation_data()
        coverage_analysis = self.analyze_accreditation_coverage()
        
        # Create comprehensive report
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'database_file': self.database_path,
                'report_version': '1.0',
                'total_organizations_analyzed': len(self.organizations)
            },
            'validation_summary': {
                'total_organizations': validation_stats['total_organizations'],
                'organizations_with_certifications': validation_stats['organizations_with_certifications'],
                'organizations_without_certifications': validation_stats['organizations_without_certifications'],
                'certification_coverage_percentage': round(
                    (validation_stats['organizations_with_certifications'] / validation_stats['total_organizations'] * 100), 2
                ) if validation_stats['total_organizations'] > 0 else 0,
                'total_certifications': validation_stats['total_certifications'],
                'average_certifications_per_organization': round(
                    validation_stats['total_certifications'] / validation_stats['organizations_with_certifications'], 2
                ) if validation_stats['organizations_with_certifications'] > 0 else 0
            },
            'data_quality_assessment': {
                'completeness_score': round(
                    (validation_stats['data_quality_metrics']['complete_certification_data'] / 
                     validation_stats['total_certifications'] * 100), 2
                ) if validation_stats['total_certifications'] > 0 else 0,
                'data_quality_metrics': validation_stats['data_quality_metrics'],
                'validation_issues_count': len(validation_stats['validation_issues']),
                'critical_issues': [issue for issue in validation_stats['validation_issues'] 
                                  if 'Missing certification' in issue['issue']][:10]  # Top 10 critical issues
            },
            'accreditation_distribution': {
                'certification_types': dict(validation_stats['certification_types']),
                'certification_status_distribution': dict(validation_stats['certification_status_distribution']),
                'countries_with_accreditations': validation_stats['countries_with_accreditations'],
                'accreditation_by_country': {k: dict(v) for k, v in validation_stats['accreditation_by_country'].items()}
            },
            'accreditation_coverage_analysis': coverage_analysis,
            'key_findings': self._generate_key_findings(validation_stats, coverage_analysis),
            'recommendations': self._generate_recommendations(validation_stats, coverage_analysis)
        }
        
        return report
    
    def _generate_key_findings(self, validation_stats, coverage_analysis):
        """Generate key findings from the validation analysis"""
        findings = []
        
        # Coverage findings
        cert_coverage = (validation_stats['organizations_with_certifications'] / 
                        validation_stats['total_organizations'] * 100)
        findings.append(f"Certification Coverage: {cert_coverage:.1f}% of organizations have accreditation data")
        
        # JCI findings
        jci_count = coverage_analysis['jci_accreditation']['total_count']
        findings.append(f"JCI Accreditation: {jci_count} organizations are JCI accredited")
        
        # NABH findings
        nabh_count = coverage_analysis['nabh_accreditation']['total_count']
        findings.append(f"NABH Accreditation: {nabh_count} organizations are NABH accredited")
        
        # NABL findings
        nabl_count = coverage_analysis['nabl_accreditation']['total_count']
        findings.append(f"NABL Accreditation: {nabl_count} organizations are NABL accredited")
        
        # Data quality findings
        completeness = (validation_stats['data_quality_metrics']['complete_certification_data'] / 
                       validation_stats['total_certifications'] * 100) if validation_stats['total_certifications'] > 0 else 0
        findings.append(f"Data Quality: {completeness:.1f}% of certifications have complete data")
        
        # Issues findings
        issues_count = len(validation_stats['validation_issues'])
        findings.append(f"Validation Issues: {issues_count} data quality issues identified")
        
        return findings
    
    def _generate_recommendations(self, validation_stats, coverage_analysis):
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Data quality recommendations
        if validation_stats['data_quality_metrics']['missing_certification_names'] > 0:
            recommendations.append("Address missing certification names to improve data completeness")
        
        if validation_stats['data_quality_metrics']['missing_certification_status'] > 0:
            recommendations.append("Update certification status information for better accuracy")
        
        if validation_stats['data_quality_metrics']['invalid_dates'] > 0:
            recommendations.append("Standardize date formats for certification dates")
        
        # Coverage recommendations
        if validation_stats['organizations_without_certifications'] > 100:
            recommendations.append("Expand accreditation data collection for organizations without certifications")
        
        # Specific accreditation recommendations
        if coverage_analysis['cap_accreditation']['total_count'] == 0:
            recommendations.append("Consider adding CAP accreditation data for laboratory services")
        
        if coverage_analysis['iso_certifications']['total_count'] < 50:
            recommendations.append("Enhance ISO certification data collection for quality standards")
        
        return recommendations
    
    def save_report(self, report, filename="accreditation_validation_report.json"):
        """Save the validation report to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Validation report saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return False
    
    def print_summary(self, report):
        """Print a summary of the validation report"""
        print("\n" + "="*80)
        print("QUIXAT ACCREDITATION VALIDATION REPORT SUMMARY")
        print("="*80)
        
        print(f"\n📊 VALIDATION OVERVIEW:")
        print(f"   Total Organizations: {report['validation_summary']['total_organizations']:,}")
        print(f"   Organizations with Certifications: {report['validation_summary']['organizations_with_certifications']:,}")
        print(f"   Certification Coverage: {report['validation_summary']['certification_coverage_percentage']:.1f}%")
        print(f"   Total Certifications: {report['validation_summary']['total_certifications']:,}")
        
        print(f"\n🎯 ACCREDITATION COVERAGE:")
        coverage = report['accreditation_coverage_analysis']
        print(f"   JCI Accredited: {coverage['jci_accreditation']['total_count']} organizations")
        print(f"   NABH Accredited: {coverage['nabh_accreditation']['total_count']} organizations")
        print(f"   NABL Accredited: {coverage['nabl_accreditation']['total_count']} organizations")
        print(f"   CAP Accredited: {coverage['cap_accreditation']['total_count']} organizations")
        print(f"   ISO Certified: {coverage['iso_certifications']['total_count']} organizations")
        
        print(f"\n📈 DATA QUALITY:")
        print(f"   Completeness Score: {report['data_quality_assessment']['completeness_score']:.1f}%")
        print(f"   Validation Issues: {report['data_quality_assessment']['validation_issues_count']}")
        
        print(f"\n🔍 KEY FINDINGS:")
        for finding in report['key_findings']:
            print(f"   • {finding}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for recommendation in report['recommendations']:
            print(f"   • {recommendation}")
        
        print("\n" + "="*80)

def main():
    """Main function to generate and save the validation report"""
    print("Starting QuXAT Accreditation Validation Report Generation...")
    
    # Initialize reporter
    reporter = AccreditationValidationReporter()
    
    # Generate comprehensive report
    report = reporter.generate_validation_report()
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"accreditation_validation_report_{timestamp}.json"
    reporter.save_report(report, filename)
    
    # Print summary
    reporter.print_summary(report)
    
    print(f"\n✅ Validation report generated successfully!")
    print(f"📄 Full report saved as: {filename}")

if __name__ == "__main__":
    main()