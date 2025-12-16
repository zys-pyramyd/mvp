
import re

file_path = r'c:\Users\ADMIN\grav_pyramyd\mvp\frontend\src\App.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
last_match = None

for i, line in enumerate(lines):
    line_num = i + 1
    # Remove strings and comments
    clean_line = re.sub(r'"(?:[^"\\]|\\.)*"', '""', line)
    clean_line = re.sub(r"'(?:[^'\\]|\\.)*'", "''", clean_line)
    clean_line = re.sub(r'`(?:[^`\\]|\\.)*`', '``', clean_line)
    clean_line = re.sub(r'//.*', '', clean_line)
    
    for char in clean_line:
        if char == '{':
            stack.append(line_num)
        elif char == '}':
            if stack:
                opened_at = stack.pop()
                last_match = (opened_at, line_num)
            else:
                print(f"Extra '}}' at line {line_num}")

if stack:
    print(f"Unclosed: {stack}")
else:
    print("Balanced")

if last_match:
    print(f"Last close: {last_match[1]} -> {last_match[0]}")
