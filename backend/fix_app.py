
try:
    with open('frontend/src/App.js', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Check if already imported
    if any("RecommendedCommunities" in line for line in lines[:20]):
        print("Already imported")
    else:
        lines.insert(10, "import RecommendedCommunities from './components/community/RecommendedCommunities';\n")
        with open('frontend/src/App.js', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Import added")
except Exception as e:
    print(f"Error: {e}")
