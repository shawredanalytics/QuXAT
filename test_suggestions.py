#!/usr/bin/env python3
"""
Test Mayo Clinic suggestions generation
"""

import os
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'ERROR'

from streamlit_app import HealthcareOrgAnalyzer

def test_suggestions():
    """Test Mayo Clinic suggestions generation"""
    
    print("Testing Mayo Clinic suggestions generation...")
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test various inputs
    test_inputs = ['mayo', 'Mayo', 'mayo clinic', 'Mayo clinic', 'Mayo Clinic']
    
    for test_input in test_inputs:
        print(f'\n--- Testing input: "{test_input}" ---')
        suggestions = analyzer.generate_organization_suggestions(test_input)
        
        if suggestions:
            print(f'Found {len(suggestions)} suggestions:')
            for i, suggestion in enumerate(suggestions[:5]):
                print(f'{i+1}. {suggestion["display_name"]} - {suggestion.get("location", "No location")}')
        else:
            print('No suggestions found')
            
        # Check if Mayo Clinic is in the suggestions
        mayo_found = False
        for suggestion in suggestions:
            if 'mayo' in suggestion['display_name'].lower():
                mayo_found = True
                break
        
        if mayo_found:
            print('✅ Mayo Clinic found in suggestions')
        else:
            print('❌ Mayo Clinic NOT found in suggestions')
    
    # Test the database directly
    print('\n--- Direct database check ---')
    if analyzer.unified_database:
        mayo_orgs = []
        for org in analyzer.unified_database:
            if isinstance(org, dict):
                org_name = org.get('name', '').lower()
                if 'mayo' in org_name:
                    mayo_orgs.append(org.get('name', 'Unknown'))
        
        if mayo_orgs:
            print(f'Found {len(mayo_orgs)} Mayo organizations in database:')
            for org in mayo_orgs:
                print(f'- {org}')
        else:
            print('No Mayo organizations found in database')
    else:
        print('Database not loaded')

if __name__ == "__main__":
    test_suggestions()