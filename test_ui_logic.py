#!/usr/bin/env python3
"""
Test UI logic for Mayo Clinic suggestions
"""

import os
os.environ['STREAMLIT_LOGGER_LEVEL'] = 'ERROR'

from streamlit_app import HealthcareOrgAnalyzer

def test_ui_logic():
    """Test the exact UI logic that determines suggestions vs validation warning"""
    
    print("Testing UI logic for Mayo Clinic...")
    
    # Initialize analyzer
    analyzer = HealthcareOrgAnalyzer()
    
    # Test the exact search input that causes the issue
    search_input = "Mayo clinic"
    
    print(f'Testing search input: "{search_input}"')
    
    # Step 1: Check if suggestions are generated
    analyzer_suggestions = analyzer.generate_organization_suggestions(search_input, max_suggestions=8)
    
    print(f'Suggestions generated: {len(analyzer_suggestions) if analyzer_suggestions else 0}')
    
    if analyzer_suggestions:
        print('✅ Suggestions found - should show suggestion dropdown')
        for i, suggestion in enumerate(analyzer_suggestions):
            display_text = analyzer.format_suggestion_display(suggestion)
            print(f'{i+1}. {display_text}')
    else:
        print('❌ No suggestions found - will show validation warning')
        
        # Step 2: Test validation result (this is what triggers the warning)
        validation_result = analyzer.search_organization_info(search_input)
        
        if validation_result and isinstance(validation_result, dict):
            print('⚠️  Validation result found - will show validation warning')
            print(f'Validation result name: {validation_result.get("name", "Unknown")}')
        else:
            print('ℹ️  No validation result - will show contact message')
    
    # Test boolean evaluation
    print(f'\nBoolean evaluation:')
    print(f'analyzer_suggestions: {analyzer_suggestions}')
    print(f'bool(analyzer_suggestions): {bool(analyzer_suggestions)}')
    print(f'len(analyzer_suggestions): {len(analyzer_suggestions) if analyzer_suggestions else "N/A"}')

if __name__ == "__main__":
    test_ui_logic()