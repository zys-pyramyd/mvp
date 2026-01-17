
import re
import sys

def find_top_level_duplicates(file_path):
    print(f"Scanning {file_path} for TOP-LEVEL duplicates...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Regex to capture "const Name =" or "function Name" or "class Name"
        # MUST start at beginning of line (no whitespace) to be top-level generally
        pattern = re.compile(r"^(const|function|class|export default function|export const)\s+([a-zA-Z0-9_]+)")
        
        definitions = {}
        duplicates = {}

        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                name = match.group(2)
                line_num = i + 1
                if name in definitions:
                    if name not in duplicates:
                        duplicates[name] = [definitions[name]]
                    duplicates[name].append(line_num)
                else:
                    definitions[name] = line_num
        
        if duplicates:
            print("Found duplicates:")
            for name, lines in duplicates.items():
                print(f"{name}: {lines}")
        else:
            print("No top-level duplicate definitions found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        find_top_level_duplicates(sys.argv[1])
    else:
        print("Usage: python scan_top_level_dupes.py <file_path>")
