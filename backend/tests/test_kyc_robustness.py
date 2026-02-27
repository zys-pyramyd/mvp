import requests
import uuid
import sys

BASE_URL = "http://localhost:8001"

def print_result(msg, success=True):
    icon = "[OK]" if success else "[FAIL]"
    print(f"{icon} {msg}")

def test_kyc_flow():
    print("Testing KYC Robustness Flow...")
    
    # 1. Register New User
    username = f"kyc_user_{str(uuid.uuid4())[:6]}"
    email = f"{username}@example.com"
    password = "password123"
    
    try:
        reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
            "role": "agent",
            "first_name": "Test",
            "last_name": "User"
        })
        if reg_res.status_code != 200:
            print_result(f"Registration Failed: {reg_res.text}", False)
            return

        token = reg_res.json()['token']
        headers = {"Authorization": f"Bearer {token}"}
        user_id = reg_res.json()['user']['id']
        print_result("User Registered")

        # 2. Upload Documents (Mock IDs)
        doc1_id = str(uuid.uuid4()) 
        # In a real integration test we'd upload actual files, but for robustness logic check, 
        # we can try to submit with made-up IDs. 
        # Wait, the endpoint checks if documents exist. So we MUST upload.
        
        # We'll skip file upload and inject into DB or mock the check? 
        # No, let's use the actual upload endpoint.
        
        files = {'file': ('test.txt', b'test content', 'application/pdf')}
        data = {'document_type': 'national_id_doc'}
        
        up_res = requests.post(f"{BASE_URL}/api/kyc/upload-document", headers=headers, files=files, data=data) 
        if up_res.status_code != 200:
             print_result(f"Upload Failed: {up_res.text}", False)
             return
        
        doc1_id = up_res.json()['document_id']
        print_result("Document Uploaded")

        # 3. Submit KYC (First Time -> Success)
        kyc_payload = {
            "headshot_photo_id": doc1_id,
            "national_id_document_id": doc1_id,
            "utility_bill_id": doc1_id,
            "address": "123 Test St",
            "state": "Lagos",
            "lga": "Ikeja"
        }
        
        sub_res = requests.post(f"{BASE_URL}/api/kyc/submit/agent", headers=headers, json=kyc_payload)
        if sub_res.status_code == 200:
            print_result("First KYC Submission Successful (Pending)")
        else:
            print_result(f"First Submission Failed: {sub_res.text}", False)
            return

        # 4. Try Submit Again (Should Fail - 400 Already pending)
        sub_res_2 = requests.post(f"{BASE_URL}/api/kyc/submit/agent", headers=headers, json=kyc_payload)
        if sub_res_2.status_code == 400 and "under review" in sub_res_2.text:
            print_result("Duplicate Submission Blocked (Pending State)")
        else:
            print_result(f"Failed block duplicate submission: {sub_res_2.status_code} {sub_res_2.text}", False)

        # 5. Admin Approve
        # Need Admin Token. Let's hijack the session or use a known admin.
        # Assuming we can login as admin or just update DB directly if we were inside app.
        # Since this is external script, we need admin credentials.
        # Let's hope the default admin exists.
        admin_login = requests.post(f"{BASE_URL}/api/auth/login", json={"email_or_phone": "admin@example.com", "password": "AdminInitialPassword123!"})
        if admin_login.status_code == 200:
            admin_token = admin_login.json()['access_token']
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            
            approve_res = requests.post(f"{BASE_URL}/api/kyc/admin/approve/{user_id}", headers=admin_headers)
            if approve_res.status_code == 200:
                print_result("Admin Approved KYC")
            else:
                print_result(f"Admin Approval Failed: {approve_res.text}", False)
        else:
            print_result("Skipping Admin Approval (No Creds) - Cannot test Notification", False)
            # Check DB directly if possible? No.
            return

        # 6. Verify Notification Created
        notif_res = requests.get(f"{BASE_URL}/api/notifications/", headers=headers)
        if notif_res.status_code == 200:
            notifs = notif_res.json()
            if any(n['type'] == 'kyc' and 'Approved' in n['title'] for n in notifs):
                print_result("Notification Received: KYC Approved")
            else:
                print_result("Notification Missing", False)
        
        # 7. Try Submit Again (Should Fail - 400 Already approved)
        sub_res_3 = requests.post(f"{BASE_URL}/api/kyc/submit/agent", headers=headers, json=kyc_payload)
        if sub_res_3.status_code == 400 and "already approved" in sub_res_3.text:
            print_result("Duplicate Submission Blocked (Approved State)")
        else:
            print_result(f"Failed block duplicate submission (Approved): {sub_res_3.status_code} {sub_res_3.text}", False)

    except Exception as e:
        print_result(f"Test Exception: {e}", False)

if __name__ == "__main__":
    test_kyc_flow()
