#!/usr/bin/env python3
"""
Test NABL Database Integration
Verifies the NABL database integration and tests it with the QuXAT scoring system
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add the current directory to Python path for imports
sys.path.append(str(Path.cwd()))

class NABLIntegrationTester:
    def __init__(self, unified_db_file: str = "unified_healthcare_organizations.json"):
        self.unified_db_file = unified_db_file
        self.project_root = Path.cwd()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Test results
        self.test_results = {
            'database_tests': {},
            'integration_tests': {},
            'scoring_tests': {},
            'overall_status': 'PENDING'
        }
    
    def load_unified_database(self) -> Dict[str, Any]:
        """Load the unified healthcare database"""
        try:
            with open(self.unified_db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded unified database with {len(data.get('organizations', []))} organizations")
            return data
        except Exception as e:
            self.logger.error(f"Error loading unified database: {e}")
            return {}
    
    def test_database_structure(self, db_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test the database structure and integrity"""
        results = {
            'metadata_present': False,
            'organizations_present': False,
            'total_organizations': 0,
            'nabl_organizations': 0,
            'data_sources': [],
            'structure_valid': False
        }
        
        try:
            # Check metadata
            if 'metadata' in db_data:
                results['metadata_present'] = True
                metadata = db_data['metadata']
                self.logger.info(f"Database version: {metadata.get('version', 'Unknown')}")
                self.logger.info(f"Last updated: {metadata.get('integration_timestamp', 'Unknown')}")
            
            # Check organizations
            if 'organizations' in db_data:
                results['organizations_present'] = True
                organizations = db_data['organizations']
                results['total_organizations'] = len(organizations)
                
                # Count NABL organizations
                nabl_count = 0
                data_sources = set()
                
                for org in organizations:
                    data_source = org.get('data_source', 'Unknown')
                    data_sources.add(data_source)
                    
                    # Check for NABL accreditation
                    quality_indicators = org.get('quality_indicators', {})
                    if quality_indicators.get('nabl_accredited', False):
                        nabl_count += 1
                
                results['nabl_organizations'] = nabl_count
                results['data_sources'] = list(data_sources)
                
                # Structure validation
                if results['total_organizations'] > 0 and results['nabl_organizations'] > 0:
                    results['structure_valid'] = True
            
        except Exception as e:
            self.logger.error(f"Error testing database structure: {e}")
        
        return results
    
    def test_nabl_data_quality(self, db_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test the quality of NABL data integration"""
        results = {
            'organizations_with_nabl_certs': 0,
            'organizations_with_nabl_data': 0,
            'average_confidence_score': 0.0,
            'high_confidence_orgs': 0,
            'data_quality_valid': False
        }
        
        try:
            organizations = db_data.get('organizations', [])
            nabl_cert_count = 0
            nabl_data_count = 0
            confidence_scores = []
            high_confidence_count = 0
            
            for org in organizations:
                # Check for NABL certifications
                certifications = org.get('certifications', [])
                has_nabl_cert = any(cert.get('type') == 'NABL Accreditation' for cert in certifications)
                
                if has_nabl_cert:
                    nabl_cert_count += 1
                
                # Check for NABL-specific data
                if 'nabl_data' in org:
                    nabl_data_count += 1
                    
                    # Get confidence score
                    nabl_data = org['nabl_data']
                    data_quality = nabl_data.get('data_quality', {})
                    confidence_score = data_quality.get('confidence_score', 0)
                    
                    if confidence_score > 0:
                        confidence_scores.append(confidence_score)
                        
                        if confidence_score >= 70:
                            high_confidence_count += 1
            
            results['organizations_with_nabl_certs'] = nabl_cert_count
            results['organizations_with_nabl_data'] = nabl_data_count
            
            if confidence_scores:
                results['average_confidence_score'] = sum(confidence_scores) / len(confidence_scores)
                results['high_confidence_orgs'] = high_confidence_count
                results['data_quality_valid'] = results['average_confidence_score'] >= 50
            
        except Exception as e:
            self.logger.error(f"Error testing NABL data quality: {e}")
        
        return results
    
    def test_scoring_system_integration(self, db_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test integration with the QuXAT scoring system"""
        results = {
            'sample_organizations_tested': 0,
            'nabl_scoring_working': False,
            'sample_scores': [],
            'integration_functional': False
        }
        
        try:
            # Import the scoring system
            try:
                from streamlit_app import HealthcareOrgAnalyzer
                analyzer = HealthcareOrgAnalyzer()
                scoring_available = True
            except ImportError as e:
                self.logger.warning(f"Could not import scoring system: {e}")
                scoring_available = False
            
            if scoring_available:
                organizations = db_data.get('organizations', [])
                
                # Test with a few NABL organizations
                nabl_orgs = [org for org in organizations if org.get('quality_indicators', {}).get('nabl_accredited', False)]
                test_orgs = nabl_orgs[:5]  # Test first 5 NABL organizations
                
                for org in test_orgs:
                    try:
                        # Prepare test data for scoring
                        certifications = org.get('certifications', [])
                        quality_initiatives = []
                        patient_feedback = []
                        org_name = org.get('name', '')
                        
                        # Calculate score with correct parameters
                        score_result = analyzer.calculate_quality_score(
                            certifications=certifications,
                            initiatives=quality_initiatives,
                            org_name=org_name,
                            branch_info=None,
                            patient_feedback_data=patient_feedback
                        )
                        
                        if score_result and 'total_score' in score_result:
                            results['sample_scores'].append({
                                'organization': org['name'],
                                'total_score': score_result['total_score'],
                                'nabl_score': score_result.get('nabl_accreditation_score', 0),
                                'has_nabl_certification': score_result.get('nabl_accreditation_score', 0) > 0
                            })
                            results['sample_organizations_tested'] += 1
                    
                    except Exception as e:
                        self.logger.warning(f"Error testing organization {org['name']}: {e}")
                        continue
                
                # Check if NABL scoring is working
                nabl_scores = [score['nabl_score'] for score in results['sample_scores'] if score['nabl_score'] > 0]
                results['nabl_scoring_working'] = len(nabl_scores) > 0
                results['integration_functional'] = results['sample_organizations_tested'] > 0 and results['nabl_scoring_working']
            
        except Exception as e:
            self.logger.error(f"Error testing scoring system integration: {e}")
        
        return results
    
    def test_search_functionality(self, db_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test search functionality with NABL organizations"""
        results = {
            'search_keywords_present': 0,
            'searchable_nabl_orgs': 0,
            'search_functional': False
        }
        
        try:
            organizations = db_data.get('organizations', [])
            nabl_orgs = [org for org in organizations if org.get('quality_indicators', {}).get('nabl_accredited', False)]
            
            keyword_count = 0
            searchable_count = 0
            
            for org in nabl_orgs:
                search_keywords = org.get('search_keywords', [])
                if search_keywords:
                    keyword_count += len(search_keywords)
                    searchable_count += 1
            
            results['search_keywords_present'] = keyword_count
            results['searchable_nabl_orgs'] = searchable_count
            results['search_functional'] = searchable_count > 0 and keyword_count > 0
            
        except Exception as e:
            self.logger.error(f"Error testing search functionality: {e}")
        
        return results
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        self.logger.info("Starting comprehensive NABL integration tests")
        
        # Load database
        db_data = self.load_unified_database()
        if not db_data:
            self.test_results['overall_status'] = 'FAILED'
            return self.test_results
        
        # Run tests
        self.test_results['database_tests'] = self.test_database_structure(db_data)
        self.test_results['integration_tests'] = self.test_nabl_data_quality(db_data)
        self.test_results['scoring_tests'] = self.test_scoring_system_integration(db_data)
        self.test_results['search_tests'] = self.test_search_functionality(db_data)
        
        # Determine overall status
        db_valid = self.test_results['database_tests'].get('structure_valid', False)
        quality_valid = self.test_results['integration_tests'].get('data_quality_valid', False)
        scoring_functional = self.test_results['scoring_tests'].get('integration_functional', False)
        search_functional = self.test_results['search_tests'].get('search_functional', False)
        
        if db_valid and quality_valid:
            if scoring_functional and search_functional:
                self.test_results['overall_status'] = 'PASSED'
            else:
                self.test_results['overall_status'] = 'PARTIAL'
        else:
            self.test_results['overall_status'] = 'FAILED'
        
        return self.test_results
    
    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"nabl_integration_test_report_{timestamp}.json"
        
        # Add metadata to test results
        report_data = {
            'test_metadata': {
                'test_timestamp': datetime.now().isoformat(),
                'database_file': self.unified_db_file,
                'test_version': '1.0',
                'tester': 'NABLIntegrationTester'
            },
            'test_results': self.test_results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Test report saved to: {report_file}")
        return report_file

def main():
    import sys
    
    # Get database file from command line or use default
    db_file = sys.argv[1] if len(sys.argv) > 1 else "unified_healthcare_organizations.json"
    
    tester = NABLIntegrationTester(db_file)
    
    print("🧪 NABL Integration Testing Started")
    print("=" * 50)
    
    # Run tests
    results = tester.run_comprehensive_tests()
    
    # Generate report
    report_file = tester.generate_test_report()
    
    # Display results
    print(f"✅ Testing completed!")
    print(f"\n📊 Test Results Summary:")
    print(f"   • Overall Status: {results['overall_status']}")
    
    # Database tests
    db_tests = results.get('database_tests', {})
    print(f"\n🗄️ Database Tests:")
    print(f"   • Total Organizations: {db_tests.get('total_organizations', 0)}")
    print(f"   • NABL Organizations: {db_tests.get('nabl_organizations', 0)}")
    print(f"   • Data Sources: {', '.join(db_tests.get('data_sources', []))}")
    print(f"   • Structure Valid: {'✅' if db_tests.get('structure_valid', False) else '❌'}")
    
    # Integration tests
    int_tests = results.get('integration_tests', {})
    print(f"\n🔗 Integration Tests:")
    print(f"   • Organizations with NABL Certs: {int_tests.get('organizations_with_nabl_certs', 0)}")
    print(f"   • Average Confidence Score: {int_tests.get('average_confidence_score', 0):.1f}%")
    print(f"   • High Confidence Organizations: {int_tests.get('high_confidence_orgs', 0)}")
    print(f"   • Data Quality Valid: {'✅' if int_tests.get('data_quality_valid', False) else '❌'}")
    
    # Scoring tests
    score_tests = results.get('scoring_tests', {})
    print(f"\n🎯 Scoring System Tests:")
    print(f"   • Sample Organizations Tested: {score_tests.get('sample_organizations_tested', 0)}")
    print(f"   • NABL Scoring Working: {'✅' if score_tests.get('nabl_scoring_working', False) else '❌'}")
    print(f"   • Integration Functional: {'✅' if score_tests.get('integration_functional', False) else '❌'}")
    
    # Search tests
    search_tests = results.get('search_tests', {})
    print(f"\n🔍 Search Tests:")
    print(f"   • Searchable NABL Organizations: {search_tests.get('searchable_nabl_orgs', 0)}")
    print(f"   • Search Keywords Present: {search_tests.get('search_keywords_present', 0)}")
    print(f"   • Search Functional: {'✅' if search_tests.get('search_functional', False) else '❌'}")
    
    # Sample scores
    sample_scores = score_tests.get('sample_scores', [])
    if sample_scores:
        print(f"\n📈 Sample Scoring Results:")
        for i, score in enumerate(sample_scores[:3], 1):
            print(f"   {i}. {score['organization'][:50]}...")
            print(f"      Total Score: {score['total_score']:.1f}, NABL Score: {score['nabl_score']:.1f}")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    print("\n" + "=" * 50)
    
    if results['overall_status'] == 'PASSED':
        print("🎉 All tests PASSED! NABL integration is fully functional.")
    elif results['overall_status'] == 'PARTIAL':
        print("⚠️ Tests PARTIALLY passed. Core integration works but some features need attention.")
    else:
        print("❌ Tests FAILED. Please check the integration and fix issues.")

if __name__ == "__main__":
    main()