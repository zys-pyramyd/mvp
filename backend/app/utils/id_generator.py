
import string
import secrets

def generate_tracking_id(prefix: str = "NGN_PYD-", length: int = 12) -> str:
    """
    Generate a unique tracking ID using a secure random alphanumeric string.
    
    Args:
        prefix (str): Prefix for the ID. Defaults to "NGN_PYD-".
        length (int): Length of the random suffix. Defaults to 12.
        
    Returns:
        str: The formatted tracking ID (e.g., NGN_PYD-A1B2C3D4E5F6)
    """
    alphabet = string.ascii_uppercase + string.digits
    suffix = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}{suffix}"
