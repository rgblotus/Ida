from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """Domain model for User entity"""
    id: Optional[int] = None
    email: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def activate(self) -> None:
        """Activate the user account"""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the user account"""
        self.is_active = False

    def update_email(self, new_email: str) -> None:
        """Update user email"""
        # Add email validation logic here if needed
        self.email = new_email

    def is_new(self) -> bool:
        """Check if this is a new user (not yet persisted)"""
        return self.id is None