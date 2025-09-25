#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def fix_unicode_in_file():
    """Fix Unicode encoding issues in streamlit_app.py"""
    
    # Read the file with proper encoding
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Simple replacements for the most common issues
        fixes = [
            ('ï¸', '️'),  # Fix variation selector
            ('ðŸ¥', '🏥'),  # Hospital
            ('âš ï¸', '⚠️'),  # Warning
            ('âœ…', '✅'),  # Check mark
            ('âŒ', '❌'),  # X mark
            ('ðŸ"', '🔐'),  # Lock
            ('ðŸ†', '🏆'),  # Trophy
            ('ðŸ'¡', '💡'),  # Light bulb
            ('ðŸ"Š', '📊'),  # Bar chart
            ('ðŸŽ¯', '🎯'),  # Target
            ('ðŸŒŸ', '🌟'),  # Star
            ('ðŸš€', '🚀'),  # Rocket
            ('ðŸ'¥', '👥'),  # People
            ('ðŸ"ˆ', '📈'),  # Chart up
            ('ðŸ"‰', '📉'),  # Chart down
            ('ðŸ"', '🔍'),  # Search
            ('â€¢', '•'),  # Bullet point
        ]
        
        # Apply fixes
        for old, new in fixes:
            content = content.replace(old, new)
        
        # Write back
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Unicode characters fixed successfully!")
        return True
        
    except Exception as e:
        print(f"Error fixing Unicode: {e}")
        return False

if __name__ == "__main__":
    fix_unicode_in_file()