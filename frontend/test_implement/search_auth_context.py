
file_path = r'c:\Users\ADMIN\grav_pyramyd\mvp\frontend\src\App.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'showAuthModal' in line and ('&&' in line or '?' in line):
        print(f"Line {i+1}:")
        for j in range(max(0, i-2), min(len(lines), i+3)):
            print(f"{j+1}: {lines[j].rstrip()}")
        print("-" * 20)
