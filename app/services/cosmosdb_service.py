import uuid
from azure.cosmos import CosmosClient, exceptions, PartitionKey
import os

class CosmosDBService:
    def __init__(self):
        endpoint = os.getenv('COSMOSDB_ENDPOINT')
        key = os.getenv('COSMOSDB_KEY')
        database_name = os.getenv('COSMOSDB_DATABASE')
        
        self.validators_container_name = 'validators'
        self.blockchain_container_name = 'blockchain'
        self.medical_records_container_name = 'medical_records'

        self.client = CosmosClient(endpoint, key)
        self.database = self.client.get_database_client(database_name)
        self.validators_container = self.database.get_container_client(self.validators_container_name)
        self.blockchain_container = self.database.get_container_client(self.blockchain_container_name)
        self.medical_records_container = self.database.get_container_client(self.medical_records_container_name)
    
    def store_validator(self, validator_id: str) -> bool:
        """Store a new validator in the Validators collection."""
        try:
            self.validators_container.upsert_item({"id": validator_id})
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
        try:
            self.blockchain_container.upsert_item(block)
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error storing block: {str(e)}")
            return False
    
    def store_medical_record(self, medical_record: dict) -> str:
        """
        Store a medical record in the Medical Records collection.
        
        Args:
            medical_record (dict): The medical record data to be stored, including a 'Type' field.
        
        Returns:
            str: The unique ID of the stored medical record.
        """
        if 'Type' not in medical_record:
            raise ValueError("Medical record must include a 'Type' field to specify its subtype.")
        
        medical_record_id = str(uuid.uuid4())
        medical_record['id'] = medical_record_id
        self.medical_records_container.upsert_item(medical_record)
        return medical_record_id

    def get_medical_record(self, record_id: str) -> dict:
        """
        Retrieve a medical record by its ID.
        
        Args:
            record_id (str): The unique ID of the medical record.
        
        Returns:
            dict: The medical record data retrieved from the collection.
        """
        try:
            return self.medical_records_container.read_item(item=record_id, partition_key=record_id)
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error retrieving medical record: {str(e)}")
            raise
