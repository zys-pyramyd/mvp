with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('server.py', 'w', encoding='utf-8') as f:
    for line in lines:
        if line.strip().endswith(' = db.users') or line.strip().endswith('_collection = db.') or '= db.' in line:
            if 'geo_helper = GeopyHelper' not in line:
                continue
        f.write(line)
