import re

filepath = r"c:\Users\Downloads\mvp\frontend\src\App.js"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove specific state variables
state_vars = [
    "showDriverPortal", "showLogisticsDashboard", "showAddDriver",
    "showCreateDeliveryRequest", "driverStatus", "availableDeliveries",
    "myDrivers", "myVehicles", "newDriverForm", "driverSearch",
    "searchResults", "selectedDriver", "showDriverMessages",
    "deliveryMessages", "currentDeliveryChat", "newDeliveryMessage",
    "showDriverManagement", "driverSlots", "availableDrivers",
    "showFindDrivers", "driverSearchFilters"
]

for var in state_vars:
    # Handle const [var, setVar] = useState(...);
    # This regex is robust enough for typical state declarations.
    pattern = r"^\s*const\s+\[\s*" + var + r"\s*,\s*set" + var[0].upper() + var[1:] + r"\s*\]\s*=\s*useState\(.*?\);\n?"
    content = re.sub(pattern, "", content, flags=re.MULTILINE | re.DOTALL)

# 2. Block removal by matching opening tag/brace and counting to closing brace/tag
def remove_block_by_signature(text, signature, block_type='{'):
    # block_type can be '{' or '<'
    close_type = '}' if block_type == '{' else '>'
    
    idx = text.find(signature)
    while idx != -1:
        # Find the start of the block after the signature
        start_idx = text.find(block_type, idx)
        if start_idx == -1:
            break
        
        # Count braces/tags
        count = 1
        curr_idx = start_idx + 1
        while count > 0 and curr_idx < len(text):
            if text[curr_idx] == block_type:
                count += 1
            elif text[curr_idx] == close_type:
                count -= 1
            curr_idx += 1
            
        if count == 0:
            # We found the matching close brace
            # Return new text with this block removed
            text = text[:idx] + text[curr_idx:]
        else:
            break
            
        # Look for next occurrence
        idx = text.find(signature)
        
    return text

# Remove driver logic functions
functions_to_remove = [
    "const fetchDriverSlots = ",
    "const purchaseDriverSlots = ",
    "const assignDriverToSlot = ",
    "const fetchMyDrivers = ",
    "const searchDrivers = ",
    "const registerDriver = ",
    "const addDriver = ",
    "const getDrivers = ",
    "const updateDriverLocation = ",
    "const acceptDelivery = ",
    "const negotiateDeliveryPrice = ",
    "const completeDeliveryWithOtp = ",
    "const sendDeliveryMessage = ",
    "const getDeliveryMessages = "
]

for sig in functions_to_remove:
    content = remove_block_by_signature(content, sig, '{')

# Remove JSX Modals for Drivers
jsx_to_remove = [
    "{showDriverPortal && (",
    "{showDriverManagement && (",
    "{showFindDrivers && (",
    "{showAddDriver && (",
    "{showDriverMessages && ("
]

# For JSX modal conditionals that look like: {showMenu && ( <div...> </div> )}
# Our remover can look for the open parenthesis '('
for sig in jsx_to_remove:
    # Since the signature includes (, we find the match for '('
    idx = content.find(sig)
    while idx != -1:
        start_idx = content.find('(', idx)
        count = 1
        curr_idx = start_idx + 1
        while count > 0 and curr_idx < len(content):
            if content[curr_idx] == '(':
                count += 1
            elif content[curr_idx] == ')':
                count -= 1
            curr_idx += 1
            
        if count == 0:
            # Found matching ), remove including the wrapped { }
            # Wait, the signature starts with '{' and we matched ')'. 
            # The closing brace for the outer {} comes after ).
            close_brace = content.find('}', curr_idx)
            if close_brace != -1:
                content = content[:idx] + content[close_brace+1:]
        
        idx = content.find(sig)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("App.js stripped of driver functions and portals")
