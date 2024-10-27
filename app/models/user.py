from typing import List, Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """
    Model for User data.
    """
    id: str
    name: str
    email: EmailStr
    password_hash: str
    roles: List[str]
    validator_id: Optional[str]
