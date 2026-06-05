import ast
import os

server_path = 'c:/Users/HP/pyramydhub/mvp/backend/server.py'
with open(server_path, 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)
routes = []

for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if not getattr(node, 'decorator_list', None): continue
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, 'value', None) and getattr(dec.func.value, 'id', '') == 'app':
                if dec.args:
                    route_path = getattr(dec.args[0], 'value', '')
                    routes.append(route_path)

print("Found", len(routes), "routes in server.py")
for r in sorted(set(routes)):
    print(r)
