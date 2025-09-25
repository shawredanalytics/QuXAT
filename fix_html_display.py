#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def fix_html_display():
    """Fix HTML display issues in streamlit_app.py by replacing malformed Unicode characters."""
    
    try:
        # Read the file with proper encoding
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Define replacements for common malformed Unicode patterns
        replacements = [
            # Basic emojis
            ('ðŸ¥', '🏥'),  # Hospital
            ('âœ…', '✅'),  # Check mark
            ('âŒ', '❌'),   # X mark
            ('âš ï¸', '⚠️'),  # Warning
            ('ðŸ"', '🔐'),  # Lock
            ('ðŸšª', '🚪'),  # Door
            ('ðŸ†', '🏆'),  # Trophy
            ('ðŸ"Š', '📊'),  # Bar chart
            ('ðŸŽ¯', '🎯'),  # Target
            ('ðŸŒŸ', '🌟'),  # Star
            ('ðŸš€', '🚀'),  # Rocket
            ('ðŸ"ˆ', '📈'),  # Chart up
            ('ðŸ"‰', '📉'),  # Chart down
            ('ðŸ"', '🔍'),  # Search
            ('ðŸŸ¢', '🟢'),  # Green circle
            ('ðŸŸ¡', '🟡'),  # Yellow circle
            ('ðŸŸ ', '🟠'),  # Orange circle
            ('ðŸ"´', '🔴'),  # Red circle
            ('ðŸ"…', '📅'),  # Calendar
            ('ðŸ¢', '🏢'),  # Office building
            ('ðŸ‡®ðŸ‡³', '🇮🇳'),  # India flag
            ('ðŸ¥‡', '🥇'),  # Gold medal
            ('ðŸ¥ˆ', '🥈'),  # Silver medal
            ('ðŸ¥‰', '🥉'),  # Bronze medal
            ('ðŸŒ', '🌍'),  # Globe
            ('ðŸ©º', '🩺'),  # Stethoscope
            ('ðŸ˜Š', '😊'),  # Smiling face
            ('ðŸ¤', '🤝'),  # Handshake
            ('â³', '⏳'),   # Hourglass
            ('âš¡', '⚡'),   # High voltage
            ('ðŸ'³', '💳'),  # Credit card
            ('ðŸ"±', '📱'),  # Mobile phone
            ('â€¢', '•'),    # Bullet point
            ('âž¡ï¸', '➡️'),  # Right arrow
        ]
        
        # Apply replacements
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Write back to file
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print('HTML display issues fixed successfully!')
        print(f'Applied {len(replacements)} Unicode character replacements.')
        
    except Exception as e:
        print(f'Error fixing HTML display: {e}')

if __name__ == '__main__':
    fix_html_display()