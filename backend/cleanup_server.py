import ast

with open('server.py', 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

lines_to_delete = set()

for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == 'app':
                    # It's an @app.something decorator
                    args = [arg.value for arg in decorator.args if isinstance(arg, ast.Constant)]
                    if args and args[0] not in ('/', '/api/health', 'startup'):
                        start_line = node.lineno
                        end_line = node.end_lineno
                        for i in range(start_line - 1, end_line):
                            lines_to_delete.add(i)

lines = source.splitlines()
new_lines = []
for i, line in enumerate(lines):
    if i not in lines_to_delete:
        new_lines.append(line)

with open('server_cleaned.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines) + '\n')
print(f"Deleted {len(lines_to_delete)} lines")
