
import re

file_path = r'c:\Users\ADMIN\grav_pyramyd\mvp\frontend\src\App.js'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")
    
    found = False
    for i, line in enumerate(lines):
        if 'showAuthModal' in line or 'AuthModal' in line:
            print(f"Line {i+1}: {line.strip()[:100]}")
            found = True
            
    if not found:
        print("Not found!")

except Exception as e:
    print(f"Error: {e}")
