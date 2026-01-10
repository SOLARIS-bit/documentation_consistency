"""
User management module.
"""

class User:
    """
    Represents a user in the system.
    
    Attributes:
        name (str): User's name
        email (str): User's email
    """
    
    def __init__(self, name, email):
        """
        Initialize a new user.
        
        Args:
            name (str): User's name
            email (str): User's email
        """
        self.name = name
        self.email = email
    
    def get_name(self):
        # Intentionally missing docstring
        return self.name
    
    def get_email(self):
        """
        Get the user's email.
        
        Returns:
            str: The email address
        """
        return self.email
    
    def update_profile(self, name=None, email=None):
        # Intentionally missing docstring
        if name:
            self.name = name
        if email:
            self.email = email
    
    def is_active(self):
        # Intentionally missing docstring
        return True


def validate_email(email):
    # Intentionally missing docstring - utility function
    return "@" in email


def send_notification(user, message):
    # Intentionally missing docstring
    print(f"Sending to {user.email}: {message}")
