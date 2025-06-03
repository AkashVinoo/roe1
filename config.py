from typing import Optional
import os
from pydantic import BaseModel
import json

class AuthConfig(BaseModel):
    # Course website credentials
    course_username: Optional[str] = None
    course_password: Optional[str] = None
    
    # Discourse forum credentials
    discourse_username: Optional[str] = None
    discourse_password: Optional[str] = None
    
    # Session tokens (will be populated after login)
    course_session: Optional[str] = None
    discourse_session: Optional[str] = None
    
    @classmethod
    def load(cls, path: str = "auth_config.json"):
        """Load configuration from JSON file"""
        if os.path.exists(path):
            with open(path, 'r') as f:
                return cls(**json.load(f))
        return cls()
    
    def save(self, path: str = "auth_config.json"):
        """Save configuration to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.dict(), f, indent=2)
    
    def is_course_configured(self) -> bool:
        """Check if course credentials are configured"""
        return bool(self.course_username and self.course_password)
    
    def is_discourse_configured(self) -> bool:
        """Check if discourse credentials are configured"""
        return bool(self.discourse_username and self.discourse_password) 