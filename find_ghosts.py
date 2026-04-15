import re
import os

backend_routes = set()
frontend_calls = set()

for root, _, files in os.walk('backend'):
    if 'venv' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = re.findall(r'@(?:app|router)\.(?:get|post|put|delete|patch)\([\'\"]([^\'\"]+)[\'\"]', content)
                for match in matches:
                    backend_routes.add(match)

for root, _, files in os.walk('frontend/src'):
    for file in files:
        if file.endswith('.js') or file.endswith('.jsx'):
            with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Finding typical fetch URLs
                matches = re.findall(r'[\'\"\`](/api/[^\'\"\`\?$]+)[\'\"\`\?]', content)
                for match in matches:
                    frontend_calls.add(match)
                # also dynamic ones like `/api/users/${userId}`
                dynamic_matches = re.findall(r'[`"\']/api/([^/]+)/\$', content)
                for match in dynamic_matches:
                    frontend_calls.add(f"/api/{match}/{{id}}")

print("Backend routes count:", len(backend_routes))
print("Frontend calls mapped:", len(frontend_calls))

# Convert to a more generic pattern matching because frontend calls /api/users/123 while backend has /api/users/{user_id}
def to_regex(route):
    # Convert {param} to [^/]+
    pattern = re.sub(r'\{[^\}]+\}', r'[^/]+', route)
    return r'^' + pattern + r'$'

orphaned = []
for route in backend_routes:
    # See if any frontend call matches this backend route
    matched = False
    route_regex = to_regex(route)
    for call in frontend_calls:
        # Ignore query params in call
        call_path = call.split('?')[0]
        try:
            if re.match(route_regex, call_path):
                matched = True
                break
            # Also try substring match for dynamic routes that were partially parsed
            if "{" in route and call_path.startswith(route.split("{")[0]):
                 matched = True
                 break
        except:
            pass
    if not matched:
        orphaned.append(route)

print("\nPotentially Orphaned Routes:")
for r in sorted(orphaned):
    print(r)
