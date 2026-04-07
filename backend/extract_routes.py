import ast
import os

def extract_routes(server_path, target_path, routes_prefixes, router_name="router"):
    with open(server_path, 'r', encoding='utf-8') as f:
        source = f.read()
        
    lines = source.splitlines()
    tree = ast.parse(source)
    
    extracted_lines = []
    ranges_to_delete = []
    
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not getattr(node, 'decorator_list', None): continue
            
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and getattr(dec.func, 'value', None) and getattr(dec.func.value, 'id', '') == 'app':
                    if not dec.args: continue
                    route_path = getattr(dec.args[0], 'value', '')
                    if any(route_path.startswith(prefix) for prefix in routes_prefixes):
                        start = node.decorator_list[0].lineno - 1
                        end = node.end_lineno
                        
                        func_lines = lines[start:end]
                        for i, l in enumerate(func_lines):
                            if "@app." in l:
                                func_lines[i] = l.replace("@app.", f"@{router_name}.")
                        
                        extracted_lines.extend(func_lines)
                        extracted_lines.append("")
                        
                        ranges_to_delete.append((start, end))
                        break

    if not extracted_lines:
        print(f"[{target_path}] No routes found for prefix {routes_prefixes}")
        return

    ranges_to_delete.sort(reverse=True)
    for start, end in ranges_to_delete:
         for _ in range(end - start):
             lines.pop(start)
             
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
        
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write('# Auto-extracted Router\n')
        f.write('from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks\n')
        f.write('from app.api.deps import get_db, get_current_user\n')
        f.write('from typing import List, Optional, Dict, Any\n')
        f.write('from pydantic import BaseModel, Field\n')
        f.write('from datetime import datetime\n')
        f.write('import uuid\n')
        f.write('import random\n')
        f.write('import string\n\n')
        f.write(f'{router_name} = APIRouter()\n\n')
        f.write('\n'.join(extracted_lines) + '\n')
        
    print(f"Extracted {len(ranges_to_delete)} endpoints to {target_path}")

base = 'c:/Users/Downloads/mvp/backend'
server = os.path.join(base, 'server.py')
api_dir = os.path.join(base, 'app', 'api')

extract_routes(server, os.path.join(api_dir, 'logistics.py'), ['/api/delivery', '/api/drivers', '/api/logistics'])
extract_routes(server, os.path.join(api_dir, 'messages.py'), ['/api/messages'])
extract_routes(server, os.path.join(api_dir, 'preorders.py'), ['/api/preorder', '/api/my-preorders'])
extract_routes(server, os.path.join(api_dir, 'group_buying.py'), ['/api/group-buying', '/api/outsource'])
extract_routes(server, os.path.join(api_dir, 'platform.py'), ['/api/platform'])
