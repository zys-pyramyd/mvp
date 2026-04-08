import re

filepath = r"c:\Users\Downloads\mvp\backend\server.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Models to regex sweep
models_to_remove = [
    "DriverStatus",
    "Driver",
    "DriverSearchResult",
    "DriverCreate",
    "DriverSubscriptionStatus",
    "LogisticsDriverSlot",
    "DriverSlotCreate",
    "DriverSlotUpdate",
    "DriverRegistrationComplete",
    "EnhancedDriverProfile"
]

for model in models_to_remove:
    # Match class Name(...): to the next class or end
    pattern = r"class\s+" + model + r"\s*\(.*?\):.*?(?=\nclass\s+|$)"
    content = re.sub(pattern, "", content, flags=re.DOTALL)

# Delete single line references
lines = content.split('\n')
new_lines = []
skip_next = False
for line in lines:
    if "driver_slots_collection = db.driver_slots" in line:
        continue
    if 'DRIVER = "driver"' in line:
        continue
    if 'DRIVER_RATING = "driver_rating"' in line:
        continue
    if "db.drivers." in line or "db.driver_slots." in line:
        continue
    if "driver" in line and "roles = " in line:
        line = line.replace("'driver', ", "").replace("'driver'", "")
    new_lines.append(line)

content = "\n".join(new_lines)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("server.py cleaned of driver references")
