import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NABHEntryLevelAnalyzer:
    def __init__(self):
        self.portal_url = "https://portal.nabh.co/frmViewAccreditedEntryLevelHosp.aspx"
        self.base_url = "https://portal.nabh.co"
        
        # Session for maintaining cookies and state
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def analyze_portal_structure(self):
        """Analyze the NABH entry level portal structure"""
        logger.info("Analyzing NABH Entry Level Hospitals Portal...")
        
        analysis_report = {
            'portal_url': self.portal_url,
            'analysis_date': datetime.now().isoformat(),
            'page_structure': {},
            'forms': [],
            'tables': [],
            'data_elements': [],
            'pagination': {},
            'javascript_elements': [],
            'potential_data_sources': [],
            'errors': []
        }
        
        try:
            # Get initial page
            logger.info(f"Fetching portal page: {self.portal_url}")
            response = self.session.get(self.portal_url, timeout=30)
            
            if response.status_code != 200:
                analysis_report['errors'].append(f"Failed to access portal: HTTP {response.status_code}")
                return analysis_report
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Analyze page structure
            analysis_report['page_structure'] = self.analyze_page_structure(soup)
            
            # Analyze forms
            analysis_report['forms'] = self.analyze_forms(soup)
            
            # Analyze tables
            analysis_report['tables'] = self.analyze_tables(soup)
            
            # Analyze data elements
            analysis_report['data_elements'] = self.analyze_data_elements(soup)
            
            # Analyze pagination
            analysis_report['pagination'] = self.analyze_pagination(soup)
            
            # Analyze JavaScript
            analysis_report['javascript_elements'] = self.analyze_javascript(soup)
            
            # Look for potential data sources
            analysis_report['potential_data_sources'] = self.find_data_sources(soup)
            
            # Save page content for debugging
            with open('nabh_entry_level_page_content.html', 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            
            logger.info("Portal analysis completed successfully")
            
        except Exception as e:
            error_msg = f"Error analyzing portal: {e}"
            logger.error(error_msg)
            analysis_report['errors'].append(error_msg)
        
        return analysis_report

    def analyze_page_structure(self, soup: BeautifulSoup) -> Dict:
        """Analyze the basic page structure"""
        structure = {
            'title': soup.title.string if soup.title else 'No title found',
            'meta_tags': len(soup.find_all('meta')),
            'stylesheets': len(soup.find_all('link', rel='stylesheet')),
            'scripts': len(soup.find_all('script')),
            'divs': len(soup.find_all('div')),
            'spans': len(soup.find_all('span')),
            'inputs': len(soup.find_all('input')),
            'selects': len(soup.find_all('select')),
            'buttons': len(soup.find_all('button')),
            'links': len(soup.find_all('a')),
            'images': len(soup.find_all('img'))
        }
        
        logger.info(f"Page structure: {structure}")
        return structure

    def analyze_forms(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze forms on the page"""
        forms = []
        
        for i, form in enumerate(soup.find_all('form')):
            form_data = {
                'form_index': i,
                'id': form.get('id', ''),
                'name': form.get('name', ''),
                'action': form.get('action', ''),
                'method': form.get('method', 'GET'),
                'inputs': [],
                'selects': [],
                'buttons': []
            }
            
            # Analyze form inputs
            for inp in form.find_all('input'):
                input_data = {
                    'type': inp.get('type', 'text'),
                    'name': inp.get('name', ''),
                    'id': inp.get('id', ''),
                    'value': inp.get('value', ''),
                    'placeholder': inp.get('placeholder', '')
                }
                form_data['inputs'].append(input_data)
            
            # Analyze select elements
            for select in form.find_all('select'):
                select_data = {
                    'name': select.get('name', ''),
                    'id': select.get('id', ''),
                    'options': []
                }
                
                for option in select.find_all('option'):
                    select_data['options'].append({
                        'value': option.get('value', ''),
                        'text': option.get_text(strip=True)
                    })
                
                form_data['selects'].append(select_data)
            
            # Analyze buttons
            for button in form.find_all(['button', 'input']):
                if button.name == 'input' and button.get('type') not in ['submit', 'button']:
                    continue
                
                button_data = {
                    'type': button.get('type', 'button'),
                    'name': button.get('name', ''),
                    'id': button.get('id', ''),
                    'value': button.get('value', ''),
                    'text': button.get_text(strip=True) if button.name == 'button' else ''
                }
                form_data['buttons'].append(button_data)
            
            forms.append(form_data)
        
        logger.info(f"Found {len(forms)} forms")
        return forms

    def analyze_tables(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze tables that might contain hospital data"""
        tables = []
        
        for i, table in enumerate(soup.find_all('table')):
            table_data = {
                'table_index': i,
                'id': table.get('id', ''),
                'class': table.get('class', []),
                'rows': 0,
                'columns': 0,
                'headers': [],
                'sample_data': [],
                'has_hospital_data': False
            }
            
            # Analyze table structure
            rows = table.find_all('tr')
            table_data['rows'] = len(rows)
            
            if rows:
                # Get headers
                header_row = rows[0]
                headers = header_row.find_all(['th', 'td'])
                table_data['headers'] = [h.get_text(strip=True) for h in headers]
                table_data['columns'] = len(headers)
                
                # Get sample data (first few rows)
                for row in rows[1:6]:  # First 5 data rows
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:
                        table_data['sample_data'].append(row_data)
                
                # Check if this looks like hospital data
                table_text = table.get_text().lower()
                hospital_keywords = ['hospital', 'medical', 'clinic', 'healthcare', 'accredited', 'certificate']
                table_data['has_hospital_data'] = any(keyword in table_text for keyword in hospital_keywords)
            
            tables.append(table_data)
        
        logger.info(f"Found {len(tables)} tables")
        return tables

    def analyze_data_elements(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze potential data-containing elements"""
        data_elements = []
        
        # Look for elements that might contain hospital data
        selectors = [
            'div[class*="hospital"]',
            'div[class*="data"]',
            'div[class*="result"]',
            'div[class*="list"]',
            'div[class*="grid"]',
            'span[class*="hospital"]',
            'span[class*="name"]',
            'ul[class*="list"]',
            'li[class*="item"]'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    element_data = {
                        'selector': selector,
                        'count': len(elements),
                        'sample_content': []
                    }
                    
                    # Get sample content
                    for elem in elements[:3]:
                        content = elem.get_text(strip=True)[:200]
                        if content:
                            element_data['sample_content'].append(content)
                    
                    data_elements.append(element_data)
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
        
        return data_elements

    def analyze_pagination(self, soup: BeautifulSoup) -> Dict:
        """Analyze pagination elements"""
        pagination = {
            'has_pagination': False,
            'pagination_elements': [],
            'page_numbers': [],
            'next_prev_buttons': []
        }
        
        # Look for common pagination patterns
        pagination_selectors = [
            'div[class*="pag"]',
            'ul[class*="pag"]',
            'nav[class*="pag"]',
            'div[class*="page"]',
            'a[class*="next"]',
            'a[class*="prev"]',
            'input[name*="page"]'
        ]
        
        for selector in pagination_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    pagination['has_pagination'] = True
                    for elem in elements:
                        pagination['pagination_elements'].append({
                            'selector': selector,
                            'text': elem.get_text(strip=True),
                            'attributes': dict(elem.attrs) if hasattr(elem, 'attrs') else {}
                        })
            except Exception as e:
                logger.debug(f"Pagination selector {selector} failed: {e}")
        
        return pagination

    def analyze_javascript(self, soup: BeautifulSoup) -> List[Dict]:
        """Analyze JavaScript that might handle data loading"""
        js_elements = []
        
        scripts = soup.find_all('script')
        
        for i, script in enumerate(scripts):
            script_data = {
                'script_index': i,
                'src': script.get('src', ''),
                'type': script.get('type', ''),
                'has_ajax': False,
                'has_postback': False,
                'has_data_functions': False
            }
            
            if script.string:
                script_content = script.string.lower()
                
                # Check for AJAX patterns
                ajax_patterns = ['xmlhttprequest', 'fetch(', '$.ajax', '$.get', '$.post']
                script_data['has_ajax'] = any(pattern in script_content for pattern in ajax_patterns)
                
                # Check for ASP.NET postback
                postback_patterns = ['__dopostback', 'postback', 'webform_']
                script_data['has_postback'] = any(pattern in script_content for pattern in postback_patterns)
                
                # Check for data-related functions
                data_patterns = ['loaddata', 'getdata', 'fetchdata', 'hospital', 'search']
                script_data['has_data_functions'] = any(pattern in script_content for pattern in data_patterns)
            
            js_elements.append(script_data)
        
        return js_elements

    def find_data_sources(self, soup: BeautifulSoup) -> List[Dict]:
        """Find potential data sources"""
        data_sources = []
        
        # Look for ViewState (ASP.NET)
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        if viewstate:
            data_sources.append({
                'type': 'ASP.NET ViewState',
                'element': 'input[name="__VIEWSTATE"]',
                'present': True
            })
        
        # Look for hidden form fields
        hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        if hidden_inputs:
            data_sources.append({
                'type': 'Hidden Form Fields',
                'count': len(hidden_inputs),
                'fields': [inp.get('name', '') for inp in hidden_inputs[:10]]
            })
        
        # Look for data attributes
        data_attrs = soup.find_all(attrs=lambda x: x and any(attr.startswith('data-') for attr in x.keys()))
        if data_attrs:
            data_sources.append({
                'type': 'Data Attributes',
                'count': len(data_attrs),
                'sample_attributes': list(set([attr for elem in data_attrs[:5] for attr in elem.attrs.keys() if attr.startswith('data-')]))
            })
        
        return data_sources

    def save_analysis_report(self, analysis_report: Dict):
        """Save the analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nabh_entry_level_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis report saved to {filename}")
        return filename

    def run_analysis(self):
        """Run the complete analysis"""
        logger.info("Starting NABH Entry Level Hospitals Portal Analysis...")
        
        try:
            analysis_report = self.analyze_portal_structure()
            report_file = self.save_analysis_report(analysis_report)
            
            # Print summary
            print(f"\nNABH Entry Level Hospitals Portal Analysis Complete!")
            print(f"Analysis report saved to: {report_file}")
            
            if analysis_report.get('errors'):
                print(f"\nErrors encountered: {len(analysis_report['errors'])}")
                for error in analysis_report['errors']:
                    print(f"- {error}")
            
            # Summary of findings
            print(f"\nKey Findings:")
            print(f"- Page Title: {analysis_report['page_structure'].get('title', 'Unknown')}")
            print(f"- Forms Found: {len(analysis_report['forms'])}")
            print(f"- Tables Found: {len(analysis_report['tables'])}")
            print(f"- Data Elements: {len(analysis_report['data_elements'])}")
            print(f"- Has Pagination: {analysis_report['pagination'].get('has_pagination', False)}")
            
            # Table analysis
            hospital_tables = [t for t in analysis_report['tables'] if t.get('has_hospital_data')]
            if hospital_tables:
                print(f"- Hospital Data Tables: {len(hospital_tables)}")
                for table in hospital_tables:
                    print(f"  * Table {table['table_index']}: {table['rows']} rows, {table['columns']} columns")
                    if table['headers']:
                        print(f"    Headers: {', '.join(table['headers'][:5])}")
            
            return analysis_report
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

if __name__ == "__main__":
    analyzer = NABHEntryLevelAnalyzer()
    analyzer.run_analysis()