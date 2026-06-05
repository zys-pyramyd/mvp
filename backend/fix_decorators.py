with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for line in lines:
    if line.startswith('@app.post') or line.startswith('@app.get') or line.startswith('@app.put') or line.startswith('@app.delete'):
        # Don't keep any @app decorators anymore because I already kept the valid ones, except if they're empty lines
        if '("/")' in line or '("/api/health")' in line:
            out.append(line)
        else:
            # We skip this line
            continue
    else:
        out.append(line)

with open('server.py', 'w', encoding='utf-8') as f:
    f.writelines(out)
