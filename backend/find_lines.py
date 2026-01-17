
import ast

def find_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return

    targets = {"KYCDocument", "create_order", "verify_password"}
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in targets:
                print(f"{node.name} found at line {node.lineno}")

if __name__ == "__main__":
    find_lines("backend/server.py")
