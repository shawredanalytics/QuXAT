#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs

def fix_html_display():
    """Fix HTML display issues in streamlit_app.py by replacing malformed Unicode characters."""
    
    try:
        # Read the file with proper encoding
        with open('streamlit_app.py', 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Define replacements using hex codes to avoid syntax errors
        replacements = {
            '\uf0e5': '🏥',  # Hospital
            '\u2713': '✅',  # Check mark
            '\u274c': '❌',  # X mark
            '\u26a0\ufe0f': '⚠️',  # Warning
            '\uf510': '🔐',  # Lock
            '\uf6aa': '🚪',  # Door
            '\uf586': '🏆',  # Trophy
            '\uf4ca': '📊',  # Bar chart
            '\uf3af': '🎯',  # Target
            '\uf31f': '🌟',  # Star
            '\uf680': '🚀',  # Rocket
            '\uf4c8': '📈',  # Chart up
            '\uf4c9': '📉',  # Chart down
            '\uf50d': '🔍',  # Search
            '\uf7e2': '🟢',  # Green circle
            '\uf7e1': '🟡',  # Yellow circle
            '\uf7e0': '🟠',  # Orange circle
            '\uf534': '🔴',  # Red circle
            '\uf4c5': '📅',  # Calendar
            '\uf3e2': '🏢',  # Office building
            '\uf1ee\uf1f3': '🇮🇳',  # India flag
            '\uf947': '🥇',  # Gold medal
            '\uf948': '🥈',  # Silver medal
            '\uf949': '🥉',  # Bronze medal
            '\uf30d': '🌍',  # Globe
            '\uf9fa': '🩺',  # Stethoscope
            '\uf60a': '😊',  # Smiling face
            '\uf91d': '🤝',  # Handshake
            '\u23f3': '⏳',  # Hourglass
            '\u26a1': '⚡',  # High voltage
            '\uf4b3': '💳',  # Credit card
            '\uf4f1': '📱',  # Mobile phone
            '\u2022': '•',   # Bullet point
            '\u27a1\ufe0f': '➡️',  # Right arrow
        }
        
        # Apply replacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Also fix common malformed patterns using string replacement
        malformed_patterns = [
            ('ðŸ¥', '🏥'),
            ('âœ…', '✅'),
            ('âŒ', '❌'),
            ('âš ï¸', '⚠️'),
            ('ðŸ"', '🔐'),
            ('ðŸšª', '🚪'),
            ('ðŸ†', '🏆'),
            ('ðŸ"Š', '📊'),
            ('ðŸŽ¯', '🎯'),
            ('ðŸŒŸ', '🌟'),
            ('ðŸš€', '🚀'),
            ('ðŸ"ˆ', '📈'),
            ('ðŸ"‰', '📉'),
            ('ðŸ"', '🔍'),
            ('ðŸŸ¢', '🟢'),
            ('ðŸŸ¡', '🟡'),
            ('ðŸŸ ', '🟠'),
            ('ðŸ"´', '🔴'),
            ('ðŸ"…', '📅'),
            ('ðŸ¢', '🏢'),
            ('ðŸ‡®ðŸ‡³', '🇮🇳'),
            ('ðŸ¥‡', '🥇'),
            ('ðŸ¥ˆ', '🥈'),
            ('ðŸ¥‰', '🥉'),
            ('ðŸŒ', '🌍'),
            ('ðŸ©º', '🩺'),
            ('ðŸ˜Š', '😊'),
            ('ðŸ¤', '🤝'),
            ('â³', '⏳'),
            ('âš¡', '⚡'),
            ('ðŸ'³', '💳'),
            ('ðŸ"±', '📱'),
            ('â€¢', '•'),
            ('âž¡ï¸', '➡️'),
        ]
        
        # Apply malformed pattern replacements
        for old, new in malformed_patterns:
            if old in content:
                content = content.replace(old, new)
                print(f"Replaced: {old} -> {new}")
        
        # Write back to file
        with open('streamlit_app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print('HTML display issues fixed successfully!')
        
    except Exception as e:
        print(f'Error fixing HTML display: {e}')

if __name__ == '__main__':
    fix_html_display()