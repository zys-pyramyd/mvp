"""
Utility functions for input sanitization.
"""
import re


def sanitize_regex(user_input: str) -> str:
    """
    Escape special regex characters in user input to prevent ReDoS attacks.
    Use this before passing user input to MongoDB $regex operators.
    """
    if not user_input:
        return ""
    return re.escape(user_input)
