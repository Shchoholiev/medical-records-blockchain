from typing import Optional
from passlib.context import CryptContext
from app.models.user import User
from app.services.cosmosdb_service import CosmosDBService

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self):
        self.db_service = CosmosDBService()
    
    def create_user(self, name: str, email: str, password: str, roles: list, validator_id: Optional[str] = None) -> User:
        """
        Create a new user with hashed password and store it in the database.
        
        Args:
            name (str): The full name of the user.
            email (str): The email address of the user.
            password (str): The plain text password of the user.
            roles (list): List of roles assigned to the user.
            validator_id (Optional[str]): Optional validator ID for the user.
        
        Returns:
            User: The created user object.
        """
        password_hash = pwd_context.hash(password)
        user_data = {
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "roles": roles,
            "validator_id": validator_id 
        }
        return self.db_service.create_user(user_data)
    
    def verify_user(self, email: str, password: str) -> User:
        """
        Verify user credentials.
        
        Args:
            email (str): The email address of the user.
            password (str): The plain text password.
        
        Returns:
            User: The user object if authentication is successful, None otherwise.
        """
        user = self.db_service.get_user_by_email(email)
        if user and pwd_context.verify(password, user.password_hash):
            return user
        return None
