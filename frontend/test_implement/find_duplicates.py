
import re

def find_duplicates(file_path):
    print(f"Scanning {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        pattern = r"const\s+CreateCommunityModal\s*="
        matches = []
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                matches.append(i + 1)
        
        if matches:
            print(f"Found 'CreateCommunityModal' definitions at lines: {matches}")
        else:
            print("No definitions found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_duplicates(r"c:\Users\ADMIN\grav_pyramyd\mvp\frontend\src\App.js")
