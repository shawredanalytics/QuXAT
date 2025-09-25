import codecs
import re

def fix_unicode():
    # Read file with UTF-8 encoding
    with open('streamlit_app.py', 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Replace common malformed patterns
    content = re.sub(r'ðŸ¥', '🏥', content)  # Hospital
    content = re.sub(r'âš ï¸', '⚠️', content)  # Warning
    content = re.sub(r'âœ…', '✅', content)  # Check mark
    content = re.sub(r'âŒ', '❌', content)  # X mark
    content = re.sub(r'ï¸', '️', content)  # Variation selector
    
    # Write back
    with open('streamlit_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Unicode fix completed!")

if __name__ == "__main__":
    fix_unicode()