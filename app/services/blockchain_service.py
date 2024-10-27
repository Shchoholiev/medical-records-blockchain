from datetime import datetime, timezone
from typing import List
from app.models.block import Block
from app.services.cosmosdb_service import CosmosDBService
import hashlib
import json

class BlockchainService:
    def __init__(self):
        """
        Initialize the BlockchainService.
        
        This service is responsible for managing the blockchain, including adding
        validators, creating blocks, validating blocks, and interacting with CosmosDB.
        """
        self.cosmosdb_service = CosmosDBService()
        self.validators: List[str] = self.cosmosdb_service.get_validators()
    
    def add_validator(self, validator_id: str):
        """
        Add a new validator to the list of authorized validators.
        
        If the validator is not already in the list, it will be stored in CosmosDB
        and added to the local list of validators.
        
        Args:
            validator_id (str): The unique identifier of the validator.
        """
        if validator_id not in self.validators:
            if self.cosmosdb_service.store_validator(validator_id):
                self.validators.append(validator_id)
    
    def create_block_with_medical_record(self, patient_id: str, medical_record: dict, validator_id: str) -> Block:
        """
        Create a new block that references a stored medical record.
        
        The method first stores the provided medical record in a separate collection in CosmosDB.
        It then creates a new block that links to this medical record using its unique ID.
        If the validator is not authorized, an error is raised.
        
        Args:
            patient_id (str): The unique identifier of the patient.
            medical_record (dict): The medical record data to be stored and referenced.
            validator_id (str): The unique identifier of the validator attempting to create the block.
        
        Returns:
            Block: The newly created block.
        
        Raises:
            ValueError: If the validator is not authorized.
            Exception: If the new block cannot be stored in the blockchain.
        """
        if validator_id not in self.validators:
            raise ValueError("Unauthorized validator attempted to create a block.")
        
        medical_record_id = self.cosmosdb_service.store_medical_record(medical_record)
        
        last_block = self.get_last_block()
        # If there's no last block, this is the genesis block
        previous_hash = last_block['hash'] if last_block else "0"
        
        hash_value = self.compute_block_hash(
            index=(last_block['index'] + 1) if last_block else 1,
            timestamp=datetime.now(timezone.utc),
            patient_id=patient_id,
            medical_record_id=medical_record_id,
            medical_record=medical_record,
            previous_hash=previous_hash,
            validator_id=validator_id
        )
        
        new_block = Block(
            index=(last_block['index'] + 1) if last_block else 1,
            patient_id=patient_id,
            medical_record_id=medical_record_id,
            previous_hash=previous_hash,
            validator_id=validator_id,
            hash=hash_value
        )
        
        if self.cosmosdb_service.store_block(new_block.model_dump()):
            return new_block
        else:
            raise Exception("Failed to store the new block in the blockchain.")
    
    def compute_block_hash(self, index, timestamp, patient_id, medical_record_id, medical_record, previous_hash, validator_id) -> str:
        """
        Compute the hash for a block based on its contents, including the medical record.
        
        Args:
            index (int): The block's position in the chain.
            timestamp (datetime): The timestamp of the block's creation.
            patient_id (str): The unique identifier of the patient.
            medical_record_id (str): The ID of the medical record referenced by the block.
            medical_record (dict): The medical record data used for hash computation.
            previous_hash (str): The hash of the previous block.
            validator_id (str): The unique identifier of the validator who created this block.
        
        Returns:
            str: The computed SHA-256 hash of the block's contents.
        """
        medical_record_string = json.dumps(medical_record, sort_keys=True)
        block_string = (
            f"{index}{timestamp}{patient_id}{medical_record_id}"
            f"{medical_record_string}{previous_hash}{validator_id}"
        )
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def get_last_block(self) -> dict:
        """
        Retrieve the last block in the blockchain.
        
        Returns:
            dict: The last block's data from CosmosDB, or None if the blockchain is empty.
        """
        query = "SELECT * FROM c ORDER BY c.index DESC OFFSET 0 LIMIT 1"
        items = list(self.cosmosdb_service.blockchain_container.query_items(query=query, enable_cross_partition_query=True))
        return items[0] if items else None
    
    def get_blockchain(self) -> List[Block]:
        """
        Retrieve the full blockchain from CosmosDB.
        
        Returns:
            List[Block]: A list of all blocks in the blockchain, ordered by their index.
        """
        query = "SELECT * FROM c ORDER BY c.index ASC"
        items = list(self.cosmosdb_service.blockchain_container.query_items(query=query, enable_cross_partition_query=True))
        return [Block(**item) for item in items]
    
    def validate_block(self, block: Block) -> bool:
        """
        Validate a block by recalculating its hash and comparing it to the stored hash.
        
        Args:
            block (Block): The block to be validated.
        
        Returns:
            bool: True if the block is valid, False otherwise.
        """
        medical_record = self.cosmosdb_service.get_medical_record(block.medical_record_id)
        recomputed_hash = self.compute_block_hash(
            index=block.index,
            timestamp=block.timestamp,
            patient_id=block.patient_id,
            medical_record_id=block.medical_record_id,
            medical_record=medical_record,
            previous_hash=block.previous_hash,
            validator_id=block.validator_id
        )
        return recomputed_hash == block.hash
    
    def validate_blockchain(self) -> bool:
        """
        Validate the entire blockchain to ensure the integrity of the data.
        
        Each block's hash is recalculated and compared to its stored hash, and the 
        previous block's hash is checked against the current block's previous_hash field.
        
        Returns:
            bool: True if the entire blockchain is valid, False otherwise.
        """
        blockchain = self.get_blockchain()
        
        for i in range(1, len(blockchain)):
            current_block = blockchain[i]
            previous_block = blockchain[i - 1]
            
            if not self.validate_block(current_block):
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
