
try:
    with open(r'c:\Users\Downloads\mvp\backend\server.py', 'rb') as f:
        content = f.read()
        if b'\x00' in content:
            print("Null bytes found at indices:")
            indices = [i for i, x in enumerate(content) if x == 0]
            print(indices[:10]) # Show first 10
            # Context
            for idx in indices[:3]:
                print(f"Context around {idx}: {content[max(0, idx-10):idx+10]}")
        else:
            print("No null bytes found.")
except Exception as e:
    print(f"Error: {e}")
