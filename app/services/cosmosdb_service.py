import uuid
from azure.cosmos import CosmosClient, exceptions
import os
from app.models.medical_record import MedicalRecordRequest
from app.models.user import User

class CosmosDBService:
    def __init__(self):
        endpoint = os.getenv('COSMOSDB_ENDPOINT')
        key = os.getenv('COSMOSDB_KEY')
        database_name = os.getenv('COSMOSDB_DATABASE')
        
        self.validators_container_name = 'validators'
        self.blockchain_container_name = 'blockchain'
        self.medical_records_container_name = 'medical_records'
        self.users_container_name = 'users'

        self.client = CosmosClient(endpoint, key)
        self.database = self.client.get_database_client(database_name)
        self.validators_container = self.database.get_container_client(self.validators_container_name)
        self.blockchain_container = self.database.get_container_client(self.blockchain_container_name)
        self.medical_records_container = self.database.get_container_client(self.medical_records_container_name)
        self.users_container = self.database.get_container_client(self.users_container_name)
    
    def store_validator(self, validator_id: str, name: str) -> bool:
        """Store a new validator in the Validators collection."""
        try:
            self.validators_container.upsert_item(
                {
                    "id": validator_id, 
                    "name": name
                })
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error storing validator: {str(e)}")
            return False
    
    def get_validators(self) -> list:
        """Retrieve the list of authorized validators from CosmosDB."""
        try:
            return [item['id'] for item in self.validators_container.read_all_items()]
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error retrieving validators: {str(e)}")
            return []

    def store_block(self, block: dict) -> bool:
        """Store a block in the Blockchain collection."""
        id = str(uuid.uuid4())
        block['id'] = id
        try:
            self.blockchain_container.upsert_item(block)
            return id
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error storing block: {str(e)}")
            return False
    
    def store_medical_record(self, medical_record: dict) -> str:
        """
        Store a medical record in the Medical Records collection.
        
        Args:
            medical_record (dict): The medical record data to be stored, including a 'type' field.
        
        Returns:
            str: The unique ID of the stored medical record.
        """
        if 'type' not in medical_record:
            raise ValueError("Medical record must include a 'type' field to specify its subtype.")
        
        medical_record_id = str(uuid.uuid4())
        medical_record['id'] = medical_record_id
        self.medical_records_container.upsert_item(medical_record)
        return medical_record_id

    def get_medical_record(self, record_id: str) -> dict:
        """
        Retrieve a medical record by its ID and return it as a MedicalRecordRequest model.
        
        Args:
            record_id (str): The unique ID of the medical record.
        
        Returns:
            MedicalRecordRequest: The medical record data retrieved from the collection.
        """
        try:
            record_data = self.medical_records_container.read_item(item=record_id, partition_key=record_id)
            
            cleaned_record_data = {key: value for key, value in record_data.items() if not key.startswith('_')}
            
            return cleaned_record_data
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error retrieving medical record: {str(e)}")
            raise

    def create_user(self, user_data: dict) -> User:
        """
        Store a new user in the Users collection.
        
        Args:
            user_data (dict): The user data to store.
        
        Returns:
            User: The created user object.
        """
        user_data["id"] = str(uuid.uuid4())  
        self.users_container.upsert_item(user_data)
        return User(**user_data)
    
    def get_user_by_email(self, email: str) -> User:
        """
        Retrieve a user from CosmosDB by email.
        
        Args:
            email (str): The email address of the user.
        
        Returns:
            User: The user object if found, None otherwise.
        """
        query = f"SELECT * FROM c WHERE c.email = @email"
        parameters = [{"name": "@email", "value": email}]
        
        items = list(self.users_container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        if items:
            return User(**items[0])
        return None

    def get_user_by_id(self, user_id: str) -> User:
        """
        Retrieve a user from CosmosDB by user ID.
        
        Args:
            user_id (str): The user ID.
        
        Returns:
            User: The user object if found, None otherwise.
        """
        query = f"SELECT * FROM c WHERE c.id = @id"
        parameters = [{"name": "@id", "value": user_id}]
        
        items = list(self.users_container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True))
        if items:
            return User(**items[0])
        return None
