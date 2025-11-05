#!/usr/bin/env python3
"""
Create a proper agent user for testing
"""

import requests
import json
from datetime import datetime

def create_agent_user():
    base_url = "https://farm2consumer.preview.emergentagent.com"
    
    # Agent registration data
    timestamp = datetime.now().strftime("%H%M%S")
    agent_data = {
        "first_name": "Test",
        "last_name": "Agent",
        "username": f"testagent_new_{timestamp}",
        "email_or_phone": f"testagent_new_{timestamp}@pyramyd.com",
        "password": "password123",
        "phone": "+2348012345678",
        "gender": "male",
        "date_of_birth": "1990-01-01",
        "user_path": "partner",
        "partner_type": "agent",
        "business_info": {
            "business_name": "Test Agent Business",
            "business_address": "Test Address, Lagos"
        },
        "verification_info": {
            "nin": "12345678901"
        }
    }
    
    try:
        # Complete registration as agent
        response = requests.post(
            f"{base_url}/api/auth/complete-registration",
            json=agent_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Agent user created successfully!")
            print(f"Username: {agent_data['username']}")
            print(f"Email: {agent_data['email_or_phone']}")
            print(f"Password: {agent_data['password']}")
            print(f"Token: {result.get('token', 'N/A')}")
            print(f"User ID: {result.get('user', {}).get('id', 'N/A')}")
            print(f"Role: {result.get('user', {}).get('role', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to create agent user: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating agent user: {str(e)}")
        return False

if __name__ == "__main__":
    create_agent_user()