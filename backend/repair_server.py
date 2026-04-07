import os
import re

files = [
    r'c:\Users\Downloads\mvp\backend\app\api\logistics.py',
    r'c:\Users\Downloads\mvp\backend\app\api\group_buying.py',
    r'c:\Users\Downloads\mvp\backend\app\api\preorders.py',
    r'c:\Users\Downloads\mvp\backend\app\api\messages.py'
]

for file_path in files:
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Purge all errant db injections
    content = content.replace(' db = get_db()\n ', '')
    content = content.replace('db = get_db()\n ', '')
    content = content.replace('db = get_db()\n', '')
    content = content.replace('db = get_db()', '')

    # 2. Inject safely. We inject right after `):` when it's part of an async def.
    # Let's find every `async def` and inject after the docstring or signature.
    
    parts = content.split('async def ')
    new_content = parts[0]
    for part in parts[1:]:
        match = re.search(r'\):\s*\n', part)
        if match:
            idx = match.end()
            doc_match = re.match(r'(\s*\"\"\"[\s\S]*?\"\"\"\s*\n)', part[idx:])
            if doc_match:
                idx += doc_match.end()
            
            part = part[:idx] + '    db = get_db()\n' + part[idx:]
        else:
            match2 = re.search(r'\)\s*->[^:]+:\s*\n', part)
            if match2:
                idx = match2.end()
                doc_match = re.match(r'(\s*\"\"\"[\s\S]*?\"\"\"\s*\n)', part[idx:])
                if doc_match:
                    idx += doc_match.end()
                part = part[:idx] + '    db = get_db()\n' + part[idx:]

        new_content += 'async def ' + part

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Fixed {file_path}")
