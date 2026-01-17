
import os

file_path = r"c:\Users\ADMIN\grav_pyramyd\mvp\frontend\src\App.js"
line_limit = 10314

print(f"Targeting: {file_path}")
if not os.path.exists(file_path):
    print("File does not exist!")
    exit(1)

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Current lines: {len(lines)}")
    
    if len(lines) > line_limit:
        print(f"Truncating to {line_limit} lines...")
        new_content = lines[:line_limit]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
        print("Truncation successful.")
    else:
        print("File is already shorter than limit.")

except Exception as e:
    print(f"Error: {e}")
