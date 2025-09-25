#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unicode Character Fixer for Streamlit App
Fixes malformed Unicode characters in the streamlit_app.py file
"""

import re

def fix_unicode_characters():
    """Fix malformed Unicode characters in streamlit_app.py"""
    
    # Unicode character mappings
    unicode_fixes = {
        'ðŸ¥': '🏥',
        'ðŸ"': '🔐',
        'âœ…': '✅',
        'âŒ': '❌',
        'ðŸšª': '🚪',
        'âš ï¸': '⚠️',
        'ðŸ†': '🏆',
        'ðŸ'¡': '💡',
        'ðŸ"‹': '📋',
        'ðŸ"Š': '📊',
        'ðŸŽ¯': '🎯',
        'ðŸŸ¢': '🟢',
        'ðŸŸ¡': '🟡',
        'ðŸŸ ': '🟠',
        'ðŸ"´': '🔴',
        'ðŸ''': '👑',
        'ðŸ'Œ': '👌',
        'ðŸ"„': '🔄',
        'ðŸ"ˆ': '📈',
        'ðŸ"‰': '📉',
        'âž¡ï¸': '➡️',
        'ðŸ"…': '📅',
        'ðŸ"': '🔍',
        'ðŸš€': '🚀',
        'ðŸ'¥': '👥',
        'ðŸŒŸ': '🌟',
        'ðŸ"œ': '📜',
        'ðŸŽ‰': '🎉',
        'ðŸ"°': '📰',
        'ðŸ¢': '🏢',
        'ðŸ›ï¸': '🏛️',
        'ðŸ'©â€âš•ï¸': '👩‍⚕️',
        'ðŸ'"': '💼',
        'ðŸŽ–ï¸': '🎖️',
        'ðŸ‡®ðŸ‡³': '🇮🇳',
        'ðŸ¥‡': '🥇',
        'ðŸ¥ˆ': '🥈',
        'ðŸ¥‰': '🥉',
        'ðŸ"¬': '🔬',
        'ðŸŒ': '🌍',
        'ðŸ©º': '🩺',
        'ðŸ›¡ï¸': '🛡️',
        'ðŸ˜Š': '😊',
        'ðŸ¤': '🤝',
        'â³': '⏳',
        'âš¡': '⚡',
        'ðŸ'³': '💳',
        'ðŸ"±': '📱'
    }
    
    try:
        # Read the file
        with open('streamlit_app.py', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Apply fixes
        for malformed, correct in unicode_fixes.items():
            content = content.replace(malformed, correct)
        
        # Write back to file
        with open('streamlit_app.py', 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("✅ Unicode characters fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing Unicode characters: {e}")
        return False

if __name__ == "__main__":
    fix_unicode_characters()