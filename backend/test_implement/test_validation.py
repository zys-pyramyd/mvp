import sys
import os
from pydantic import ValidationError

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from server import UserRegister, CompleteRegistration
    print("Successfully imported models")

    # Test Valid UserRegister
    try:
        user = UserRegister(
            first_name="Test",
            last_name="User",
            username="testuser",
            email="test@example.com",
            password="password123",
            phone="08012345678"
        )
        print("Valid UserRegister passed")
    except ValidationError as e:
        print(f"Valid UserRegister failed: {e}")

    # Test Invalid Email
    try:
        user = UserRegister(
            first_name="Test",
            last_name="User",
            username="testuser",
            email="invalid-email",
            password="password123",
            phone="08012345678"
        )
        print("Invalid Email failed to raise error")
    except ValidationError as e:
        print("Invalid Email raised error as expected")

    # Test Invalid Phone
    try:
        user = UserRegister(
            first_name="Test",
            last_name="User",
            username="testuser",
            email="test@example.com",
            password="password123",
            phone="12345"
        )
        print("Invalid Phone failed to raise error")
    except ValidationError as e:
        print("Invalid Phone raised error as expected")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
