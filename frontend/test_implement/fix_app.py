import os

file_path = r'c:\Users\ADMIN\grav_pyramyd\mvp\frontend\src\App.js'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Read {len(lines)} lines from {file_path}")

# Fix 1: Restore missing functions and fix updateOrderStatus (around line 2161)
# We look for: console.error('Error updating order status:', error);
# And the next line starts with: item.product.seller_type === 'farmer' ||

missing_code = """          alert('Error updating order status');
        }
      };

      const fetchMyOrders = async (orderType = 'buyer') => {
        try {
          const token = localStorage.getItem('token');
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/my-orders?order_type=${orderType}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const data = await response.json();
            setOrders(data.orders || []);
          }
        } catch (error) {
          console.error('Error fetching orders:', error);
        }
      };

      // Checkout and cart management functions
      const calculateOrderSummary = () => {
        let productTotal = 0;
        let deliveryTotal = 0;
        let itemCount = 0;
        let platformServiceCharge = 0;
        let platformCommission = 0;
        let agentCommission = 0;

        // Detect if buyer is an agent
        const isAgent = user && (user.role === 'agent' || user.role === 'purchasing_agent');

        cart.forEach(item => {
          const itemTotal = item.product.price_per_unit * item.quantity;
          productTotal += itemTotal;
          itemCount += item.quantity;

          // Determine platform type from product
          const isFarmHub = item.product.platform === 'pyhub' ||
"""

issue1_found = False
for i in range(2150, 2180):
    if i < len(lines) and "console.error('Error updating order status:', error);" in lines[i]:
        # Check if next line is the broken one
        if i+1 < len(lines) and "item.product.seller_type === 'farmer' ||" in lines[i+1]:
            print(f"Found Issue 1 at line {i+1}. Injecting missing code...")
            # We need to insert the missing code AFTER the console.error line
            # But wait, the console.error line is inside the catch block.
            # The missing code starts with closing the catch block.
            # So we insert after line i.
            lines.insert(i+1, missing_code)
            issue1_found = True
            break

if not issue1_found:
    print("WARNING: Issue 1 not found. Skipping...")

# Fix 2: Remove extra closing div at line 2903 (approx)
# We need to be careful because line numbers shift after insertion.
# We'll search for the pattern again around where we expect it.
# The pattern is 4 closing divs then );
#                 </div>
#               </div>
#             </div>
#           </div>
#         );

# We want to remove one of them.

issue2_found = False
# Since we inserted lines, the line number will be higher than 2903.
# The insertion was about 40 lines. So look around 2940.
for i in range(2900, 3000):
    if i+4 < len(lines):
        if "</div>" in lines[i] and \
           "</div>" in lines[i+1] and \
           "</div>" in lines[i+2] and \
           "</div>" in lines[i+3] and \
           ");" in lines[i+4]:
            print(f"Found extra closing div at line {i+3}. Removing...")
            lines[i+3] = ""
            issue2_found = True
            break

if not issue2_found:
    print("WARNING: Issue 2 not found. Skipping...")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("File updated.")
