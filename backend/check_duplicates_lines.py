
import ast
import collections

def check_duplicates_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return

    definitions = collections.defaultdict(list)
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definitions[node.name].append(node.lineno)

    found = False
    for name, lines in definitions.items():
        if len(lines) > 1:
            print(f"Duplicate: {name} at lines {lines}")
            found = True
            
    with open("backend/dupes.txt", "w", encoding="utf-8") as out:
        if not found:
            out.write("No duplicates found.\n")
        else:
            for name, lines in definitions.items():
                if len(lines) > 1:
                    out.write(f"Duplicate: {name} at lines {lines}\n")

if __name__ == "__main__":
    check_duplicates_lines("backend/server.py")
