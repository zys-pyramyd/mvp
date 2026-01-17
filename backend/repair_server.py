
import os

file_path = r'c:\Users\Downloads\mvp\backend\server.py'

try:
    with open(file_path, 'rb') as f:
        content = f.read()

    # Repair: Remove null bytes
    new_content = content.replace(b'\x00', b'')

    if len(new_content) != len(content):
        print(f"Removed {len(content) - len(new_content)} null bytes.")
        # Create backup
        with open(file_path + '.bak', 'wb') as f:
            f.write(content)
        
        # Write back
        with open(file_path, 'wb') as f:
            f.write(new_content)
        print("File repaired.")
    else:
        print("No null bytes found to remove.")

except Exception as e:
    print(f"Error repairing file: {e}")
