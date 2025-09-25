import codecs

# Read the file with error handling
with open('streamlit_app.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Simple replacements for common malformed characters
content = content.replace('ðŸ¥', '🏥')  # Hospital
content = content.replace('ðŸ"', '🔐')  # Lock
content = content.replace('âœ…', '✅')  # Check mark
content = content.replace('âŒ', '❌')  # Cross mark
content = content.replace('ðŸšª', '🚪')  # Door
content = content.replace('âš ï¸', '⚠️')  # Warning
content = content.replace('ðŸ†', '🏆')  # Trophy
content = content.replace('ðŸ'¡', '💡')  # Light bulb
content = content.replace('ðŸ"‹', '📋')  # Clipboard
content = content.replace('ðŸ"Š', '📊')  # Bar chart
content = content.replace('ðŸŽ¯', '🎯')  # Target
content = content.replace('ðŸŸ¢', '🟢')  # Green circle
content = content.replace('ðŸŸ¡', '🟡')  # Yellow circle
content = content.replace('ðŸŸ ', '🟠')  # Orange circle
content = content.replace('ðŸ"´', '🔴')  # Red circle
content = content.replace('ðŸ"', '🔍')  # Magnifying glass
content = content.replace('ðŸš€', '🚀')  # Rocket
content = content.replace('ðŸ'¥', '👥')  # People
content = content.replace('ðŸŒŸ', '🌟')  # Star
content = content.replace('ðŸ"ˆ', '📈')  # Chart up
content = content.replace('ðŸ"‰', '📉')  # Chart down
content = content.replace('ðŸ"…', '📅')  # Calendar
content = content.replace('ðŸ¢', '🏢')  # Office building
content = content.replace('ðŸ‡®ðŸ‡³', '🇮🇳')  # India flag
content = content.replace('ðŸ¥‡', '🥇')  # Gold medal
content = content.replace('ðŸ¥ˆ', '🥈')  # Silver medal
content = content.replace('ðŸ¥‰', '🥉')  # Bronze medal
content = content.replace('ðŸŒ', '🌍')  # Globe
content = content.replace('ðŸ©º', '🩺')  # Stethoscope
content = content.replace('ðŸ˜Š', '😊')  # Smiling face
content = content.replace('ðŸ¤', '🤝')  # Handshake
content = content.replace('â³', '⏳')  # Hourglass
content = content.replace('âš¡', '⚡')  # Lightning
content = content.replace('ðŸ'³', '💳')  # Credit card
content = content.replace('ðŸ"±', '📱')  # Mobile phone

# Write back to file
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Unicode characters fixed successfully!')