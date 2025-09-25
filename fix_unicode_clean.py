#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Unicode Fix Script
Fixes malformed Unicode characters in streamlit_app.py
"""

import re

def fix_unicode_characters():
    """Fix malformed Unicode characters in streamlit_app.py"""
    
    # Read the file with error handling
    try:
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define replacements for malformed Unicode patterns
    # Using raw strings to avoid syntax errors
    unicode_fixes = [
        # Hospital and medical icons
        (r'ðŸ¥', '🏥'),  # Hospital
        (r'ðŸ©º', '🩺'),  # Stethoscope
        
        # Status icons
        (r'âœ…', '✅'),  # Check mark
        (r'âŒ', '❌'),   # X mark
        (r'âš ï¸', '⚠️'),  # Warning
        (r'â³', '⏳'),   # Hourglass
        
        # Achievement icons
        (r'ðŸ†', '🏆'),  # Trophy
        (r'ðŸ¥‡', '🥇'),  # Gold medal
        (r'ðŸ¥ˆ', '🥈'),  # Silver medal
        (r'ðŸ¥‰', '🥉'),  # Bronze medal
        (r'ðŸŽ–ï¸', '🎖️'),  # Military medal
        
        # Charts and data
        (r'ðŸ"Š', '📊'),  # Bar chart
        (r'ðŸ"ˆ', '📈'),  # Chart up
        (r'ðŸ"‰', '📉'),  # Chart down
        (r'ðŸŽ¯', '🎯'),  # Target
        
        # Colors and indicators
        (r'ðŸŸ¢', '🟢'),  # Green circle
        (r'ðŸŸ¡', '🟡'),  # Yellow circle
        (r'ðŸŸ ', '🟠'),  # Orange circle
        (r'ðŸ"´', '🔴'),  # Red circle
        
        # Buildings and locations
        (r'ðŸ¢', '🏢'),  # Office building
        (r'ðŸŒ', '🌍'),  # Globe
        (r'ðŸ‡®ðŸ‡³', '🇮🇳'),  # India flag
        
        # Tools and objects
        (r'ðŸ"', '🔍'),  # Search
        (r'ðŸ"', '🔐'),  # Lock
        (r'ðŸšª', '🚪'),  # Door
        (r'ðŸ"…', '📅'),  # Calendar
        
        # Emotions and gestures
        (r'ðŸ˜Š', '😊'),  # Smiling face
        (r'ðŸ¤', '🤝'),  # Handshake
        
        # Symbols
        (r'âš¡', '⚡'),   # Lightning
        (r'â€¢', '•'),    # Bullet point
        (r'âž¡ï¸', '➡️'),  # Right arrow
        (r'ðŸŒŸ', '🌟'),  # Star
        (r'ðŸš€', '🚀'),  # Rocket
    ]
    
    # Apply fixes
    original_content = content
    for pattern, replacement in unicode_fixes:
        content = re.sub(pattern, replacement, content)
    
    # Check if any changes were made
    if content == original_content:
        print("No malformed Unicode characters found.")
        return True
    
    # Write the fixed content back
    try:
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Unicode characters fixed successfully!")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    fix_unicode_characters()