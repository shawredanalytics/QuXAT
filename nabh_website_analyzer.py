import requests
import json
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NABHWebsiteAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.base_url = "https://nabh.co"
        self.search_url = "https://nabh.co/find-a-healthcare-organisation/"

    def analyze_main_page(self):
        """Analyze the main search page structure"""
        try:
            logger.info("Analyzing NABH main search page...")
            response = self.session.get(self.search_url)
            
            if response.status_code != 200:
                logger.error(f"Failed to access main page: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'page_title': soup.title.get_text() if soup.title else 'No title',
                'forms': [],
                'search_elements': [],
                'javascript_files': [],
                'ajax_endpoints': [],
                'data_attributes': [],
                'page_structure': {}
            }
            
            # Analyze forms
            forms = soup.find_all('form')
            for i, form in enumerate(forms):
                form_info = {
                    'index': i,
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET'),
                    'inputs': [],
                    'selects': []
                }
                
                # Analyze form inputs
                inputs = form.find_all('input')
                for inp in inputs:
                    form_info['inputs'].append({
                        'name': inp.get('name', ''),
                        'type': inp.get('type', ''),
                        'value': inp.get('value', ''),
                        'placeholder': inp.get('placeholder', ''),
                        'id': inp.get('id', '')
                    })
                
                # Analyze select elements
                selects = form.find_all('select')
                for select in selects:
                    select_info = {
                        'name': select.get('name', ''),
                        'id': select.get('id', ''),
                        'options': []
                    }
                    
                    options = select.find_all('option')
                    for option in options:
                        select_info['options'].append({
                            'value': option.get('value', ''),
                            'text': option.get_text(strip=True)
                        })
                    
                    form_info['selects'].append(select_info)
                
                analysis['forms'].append(form_info)
            
            # Look for search-related elements
            search_elements = soup.find_all(['input', 'button', 'div'], 
                                          attrs={'class': re.compile(r'search|filter|find', re.I)})
            
            for elem in search_elements:
                analysis['search_elements'].append({
                    'tag': elem.name,
                    'class': elem.get('class', []),
                    'id': elem.get('id', ''),
                    'text': elem.get_text(strip=True)[:100]  # First 100 chars
                })
            
            # Look for JavaScript files
            scripts = soup.find_all('script', src=True)
            for script in scripts:
                src = script.get('src')
                if src:
                    analysis['javascript_files'].append(src)
            
            # Look for data attributes that might indicate AJAX endpoints
            elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
            for elem in elements_with_data[:10]:  # Limit to first 10
                data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                if data_attrs:
                    analysis['data_attributes'].append({
                        'tag': elem.name,
                        'data_attributes': data_attrs,
                        'class': elem.get('class', [])
                    })
            
            # Analyze page structure
            main_content = soup.find(['main', 'div'], class_=re.compile(r'content|main|container', re.I))
            if main_content:
                analysis['page_structure']['main_content_classes'] = main_content.get('class', [])
                
                # Look for organization listings
                org_containers = main_content.find_all(['div', 'article', 'section'], 
                                                     class_=re.compile(r'organization|hospital|result|card|listing', re.I))
                analysis['page_structure']['potential_org_containers'] = len(org_containers)
                
                # Look for pagination
                pagination = main_content.find(['nav', 'div'], class_=re.compile(r'pagination|pager', re.I))
                if pagination:
                    analysis['page_structure']['has_pagination'] = True
                    analysis['page_structure']['pagination_classes'] = pagination.get('class', [])
            
            # Save analysis to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nabh_website_analysis_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Website analysis saved to {filename}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing main page: {e}")
            return None

    def test_search_functionality(self):
        """Test different search approaches"""
        try:
            logger.info("Testing search functionality...")
            
            # Test 1: Direct GET request with parameters
            test_params = [
                {'state': 'Maharashtra'},
                {'category': 'Hospital'},
                {'search': 'hospital'},
                {'q': 'mumbai'},
                {'location': 'Delhi'},
                {'type': 'hospital'}
            ]
            
            results = []
            
            for params in test_params:
                try:
                    response = self.session.get(self.search_url, params=params)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for results
                    result_count = len(soup.find_all(['div', 'article'], 
                                                   class_=re.compile(r'result|organization|hospital', re.I)))
                    
                    results.append({
                        'params': params,
                        'status_code': response.status_code,
                        'result_count': result_count,
                        'page_title': soup.title.get_text() if soup.title else 'No title'
                    })
                    
                    logger.info(f"Test with {params}: {response.status_code}, {result_count} results")
                    
                except Exception as e:
                    logger.error(f"Error testing with {params}: {e}")
            
            # Test 2: Check for AJAX endpoints
            logger.info("Looking for AJAX endpoints...")
            
            # Common AJAX endpoint patterns
            ajax_endpoints = [
                '/api/search',
                '/search/ajax',
                '/find-organization/ajax',
                '/api/organizations',
                '/search.php',
                '/ajax/search'
            ]
            
            for endpoint in ajax_endpoints:
                try:
                    url = self.base_url + endpoint
                    response = self.session.get(url)
                    logger.info(f"AJAX test {endpoint}: {response.status_code}")
                    
                    if response.status_code == 200:
                        # Try to parse as JSON
                        try:
                            data = response.json()
                            logger.info(f"Found JSON endpoint: {endpoint}")
                            results.append({
                                'endpoint': endpoint,
                                'type': 'ajax_json',
                                'status': 'success'
                            })
                        except:
                            pass
                            
                except Exception as e:
                    logger.debug(f"AJAX endpoint {endpoint} failed: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error testing search functionality: {e}")
            return []

    def extract_sample_data(self):
        """Try to extract any visible organization data from the main page"""
        try:
            logger.info("Extracting sample data from main page...")
            
            response = self.session.get(self.search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for any organization data that might be displayed
            potential_orgs = []
            
            # Search for common patterns
            patterns = [
                {'class': re.compile(r'hospital|organization|clinic', re.I)},
                {'data-name': True},
                {'data-organization': True}
            ]
            
            for pattern in patterns:
                elements = soup.find_all(['div', 'article', 'section', 'li'], attrs=pattern)
                
                for elem in elements:
                    org_data = {
                        'element_tag': elem.name,
                        'element_class': elem.get('class', []),
                        'element_id': elem.get('id', ''),
                        'text_content': elem.get_text(strip=True)[:200],  # First 200 chars
                        'data_attributes': {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                    }
                    
                    # Look for name patterns
                    name_elem = elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
                    if name_elem:
                        org_data['potential_name'] = name_elem.get_text(strip=True)
                    
                    potential_orgs.append(org_data)
            
            logger.info(f"Found {len(potential_orgs)} potential organization elements")
            return potential_orgs
            
        except Exception as e:
            logger.error(f"Error extracting sample data: {e}")
            return []

    def run_complete_analysis(self):
        """Run complete website analysis"""
        logger.info("Starting complete NABH website analysis...")
        
        try:
            # Analyze main page structure
            main_analysis = self.analyze_main_page()
            
            # Test search functionality
            search_tests = self.test_search_functionality()
            
            # Extract sample data
            sample_data = self.extract_sample_data()
            
            # Compile complete report
            complete_report = {
                'analysis_date': datetime.now().isoformat(),
                'main_page_analysis': main_analysis,
                'search_functionality_tests': search_tests,
                'sample_data_extraction': sample_data,
                'recommendations': []
            }
            
            # Generate recommendations based on analysis
            if main_analysis:
                if main_analysis['forms']:
                    complete_report['recommendations'].append("Forms found - try form-based search")
                
                if main_analysis['javascript_files']:
                    complete_report['recommendations'].append("JavaScript detected - may require browser automation")
                
                if main_analysis['data_attributes']:
                    complete_report['recommendations'].append("Data attributes found - check for AJAX functionality")
            
            if not sample_data:
                complete_report['recommendations'].append("No organization data found on main page - may require search interaction")
            
            # Save complete report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"nabh_complete_analysis_{timestamp}.json"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(complete_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Complete analysis saved to {report_filename}")
            
            # Print summary
            print(f"\nNABH Website Analysis Summary:")
            print(f"================================")
            print(f"Page Title: {main_analysis.get('page_title', 'Unknown') if main_analysis else 'Unknown'}")
            print(f"Forms Found: {len(main_analysis.get('forms', [])) if main_analysis else 0}")
            print(f"Search Elements: {len(main_analysis.get('search_elements', [])) if main_analysis else 0}")
            print(f"JavaScript Files: {len(main_analysis.get('javascript_files', [])) if main_analysis else 0}")
            print(f"Potential Organizations: {len(sample_data)}")
            print(f"Search Tests Performed: {len(search_tests)}")
            
            if complete_report['recommendations']:
                print(f"\nRecommendations:")
                for i, rec in enumerate(complete_report['recommendations'], 1):
                    print(f"{i}. {rec}")
            
            return complete_report
            
        except Exception as e:
            logger.error(f"Complete analysis failed: {e}")
            return None

if __name__ == "__main__":
    analyzer = NABHWebsiteAnalyzer()
    analyzer.run_complete_analysis()