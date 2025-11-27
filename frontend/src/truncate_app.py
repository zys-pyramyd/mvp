import os

file_path = r'c:\Users\ADMIN\grav_pyramyd\mvp\frontend\src\App.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "ProfilePictureUploadModal"
target_line_index = -1
for i in range(len(lines)):
    if 'ProfilePictureUploadModal' in lines[i]:
        target_line_index = i
        # We want to find the LAST occurrence if there are multiple?
        # But based on step 75, it seems to be around 9620.
        # Let's assume the one around 9620 is the one we want.
        if i > 9000:
            break

if target_line_index != -1:
    print(f"Found target at line {target_line_index + 1}")
    # Keep up to target_line_index (inclusive)
    new_lines = lines[:target_line_index+1]
    
    # Append the correct ending
    ending = """
                {/* Seller Details Modal */}
                {showSellerDetails && <SellerDetailsModal />}

              </div>
              );
}

export default App;
"""
    new_lines.append(ending)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("File truncated and fixed.")
else:
    print("Target not found.")
