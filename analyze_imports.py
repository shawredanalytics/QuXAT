import ast
import re

def analyze_unused_imports(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST
        tree = ast.parse(content)
        
        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'name': alias.name,
                        'alias': alias.asname,
                        'type': 'import',
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'name': f'{module}.{alias.name}' if module else alias.name,
                        'alias': alias.asname,
                        'type': 'from_import',
                        'module': module,
                        'imported_name': alias.name,
                        'line': node.lineno
                    })
        
        # Check usage of each import
        unused_imports = []
        for imp in imports:
            name_to_check = imp['alias'] if imp['alias'] else imp.get('imported_name', imp['name'].split('.')[-1])
            
            # Skip checking for certain common patterns
            if name_to_check in ['warnings', 'os', 'sys', 'json', 're', 'time']:
                continue
                
            # Count occurrences in the file (excluding the import line itself)
            lines = content.split('\n')
            usage_count = 0
            for i, line in enumerate(lines, 1):
                if i == imp['line']:  # Skip the import line
                    continue
                if name_to_check in line:
                    # More sophisticated check to avoid false positives
                    if re.search(r'\b' + re.escape(name_to_check) + r'\b', line):
                        usage_count += 1
            
            if usage_count == 0:
                unused_imports.append(imp)
        
        return imports, unused_imports
        
    except Exception as e:
        print(f'Error analyzing {filename}: {e}')
        return [], []

# Analyze streamlit_app.py
print('=== UNUSED IMPORTS ANALYSIS ===')
imports, unused = analyze_unused_imports('streamlit_app.py')

print(f'Total imports in streamlit_app.py: {len(imports)}')
print(f'Potentially unused imports: {len(unused)}')

print('\nAll imports:')
for imp in imports[:20]:  # Show first 20
    name = imp['alias'] if imp['alias'] else imp['name']
    print(f'  Line {imp["line"]}: {name} ({imp["type"]})')

print('\nPotentially unused imports:')
for imp in unused:
    name = imp['alias'] if imp['alias'] else imp['name']
    print(f'  Line {imp["line"]}: {name} - {imp["name"]}')

# Check specific imports that were identified earlier
specific_checks = [
    'BeautifulSoup', 'quote_plus', 'SimpleDocTemplate', 'Paragraph', 
    'Table', 'TableStyle', 'healthcare_validator', 'get_iso_certifications'
]

print('\nSpecific import usage check:')
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

for check in specific_checks:
    count = len(re.findall(r'\b' + re.escape(check) + r'\b', content))
    status = 'USED' if count > 1 else 'UNUSED' if count == 1 else 'NOT FOUND'
    print(f'  {check}: {count} occurrences - {status}')