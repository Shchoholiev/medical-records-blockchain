import logging
from datetime import datetime, timezone
from typing import List
import uuid
from app.models.block import Block
from app.services.cosmosdb_service import CosmosDBService
import hashlib
import json

logger = logging.getLogger(__name__)

class BlockchainService:
    def __init__(self):
        """
        Initialize the BlockchainService.
        
        This service is responsible for managing the blockchain, including adding
        validators, creating blocks, validating blocks, and interacting with CosmosDB.
        """
        logger.info("Initializing BlockchainService.")
        self.cosmosdb_service = CosmosDBService()
        self.validators: List[str] = self.cosmosdb_service.get_validators()
        logger.info(f"Loaded validators: {self.validators}")

    def add_validator(self, validator_id: str, name: str):
        """
        Add a new validator to the list of authorized validators.
        
        If the validator is not already in the list, it will be stored in CosmosDB
        and added to the local list of validators.
        
        Args:
            validator_id (str): The unique identifier of the validator.
        """
        logger.info(f"Attempting to add validator: {validator_id}")
        if validator_id not in self.validators:
            if self.cosmosdb_service.store_validator(validator_id, name):
                self.validators.append(validator_id)
                logger.info(f"Validator {validator_id} added successfully.")
            else:
                logger.error(f"Failed to store validator {validator_id}.")
        else:
            logger.info(f"Validator {validator_id} already exists.")

    def create_block_with_medical_record(self, patient_id: str, medical_record: dict, validator_id: str, user_id: str) -> Block:
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
        logger.info(f"Creating a block for patient {patient_id} by validator {validator_id}.")
        if validator_id not in self.validators:
            logger.error(f"Unauthorized validator {validator_id} attempted to create a block.")
            raise ValueError("Unauthorized validator attempted to create a block.")
        
        medical_record['created_date_utc'] = datetime.now(timezone.utc).isoformat()
        medical_record['created_by_id'] = user_id
        
        medical_record_id = self.cosmosdb_service.store_medical_record(medical_record)
        logger.info(f"Medical record stored with ID: {medical_record_id}")
        
        last_block = self.get_last_block()
        previous_hash = last_block['hash'] if last_block else "0"
        
        timestamp = datetime.now(timezone.utc).isoformat()
        hash_value = self.compute_block_hash(
            index=(last_block['index'] + 1) if last_block else 1,
            timestamp=timestamp,
            patient_id=patient_id,
            medical_record_id=medical_record_id,
            medical_record=medical_record,
            previous_hash=previous_hash,
            validator_id=validator_id
        )
        logger.info(f"Created hash")

        logger.info(medical_record)
        
        new_block = Block(
            id=str(uuid.uuid4()),
            index=(last_block['index'] + 1) if last_block else 1,
            timestamp=timestamp,
            patient_id=patient_id,
            medical_record_id=medical_record_id,
            previous_hash=previous_hash,
            validator_id=validator_id,
            hash=hash_value
        )
        logger.info(f"Saving block")
        
        if self.cosmosdb_service.store_block(new_block.model_dump()):
            logger.info(f"New block created and stored successfully: {new_block}")
            return new_block
        else:
            logger.error("Failed to store the new block in the blockchain.")
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
        logger.debug("Computing hash for a block.")
        medical_record_string = json.dumps(medical_record, sort_keys=True)
        block_string = (
            f"{index}{timestamp}{patient_id}{medical_record_id}"
            f"{medical_record_string}{previous_hash}{validator_id}"
        )
        hash_value = hashlib.sha256(block_string.encode()).hexdigest()
        logger.debug(f"Computed hash: {hash_value}")
        return hash_value
    
    def get_last_block(self) -> dict:
        """
        Retrieve the last block in the blockchain.
        
        Returns:
            dict: The last block's data from CosmosDB, or None if the blockchain is empty.
        """
        logger.info("Retrieving the last block from the blockchain.")
        query = "SELECT * FROM c ORDER BY c.index DESC OFFSET 0 LIMIT 1"
        items = list(self.cosmosdb_service.blockchain_container.query_items(query=query, enable_cross_partition_query=True))
        last_block = items[0] if items else None
        logger.info(f"Last block retrieved: {last_block}")
        return last_block
    
    def get_blockchain(self) -> List[Block]:
        """
        Retrieve the full blockchain from CosmosDB.
        
        Returns:
            List[Block]: A list of all blocks in the blockchain, ordered by their index.
        """
        logger.info("Retrieving the full blockchain.")
        query = "SELECT * FROM c ORDER BY c.index ASC"
        items = list(self.cosmosdb_service.blockchain_container.query_items(query=query, enable_cross_partition_query=True))
        logger.info(f"Blockchain retrieved with {len(items)} blocks.")
        return [Block(**item) for item in items]
    
    def validate_block(self, block: Block) -> bool:
        """
        Validate a block by recalculating its hash and comparing it to the stored hash.
        
        Args:
            block (Block): The block to be validated.
        
        Returns:
            bool: True if the block is valid, False otherwise.
        """
        logger.info(f"Validating block with index {block.index}.")
        medical_record = self.cosmosdb_service.get_medical_record(block.medical_record_id)
        logger.info(medical_record)
        recomputed_hash = self.compute_block_hash(
            index=block.index,
            timestamp=block.timestamp,
            patient_id=block.patient_id,
            medical_record_id=block.medical_record_id,
            medical_record=medical_record,
            previous_hash=block.previous_hash,
            validator_id=block.validator_id
        )
        is_valid = recomputed_hash == block.hash
        logger.info(f"Block validation result: {'valid' if is_valid else 'invalid'}.")
        return is_valid
    
    def validate_blockchain(self) -> bool:
        """
        Validate the entire blockchain to ensure the integrity of the data.
        
        Each block's hash is recalculated and compared to its stored hash, and the 
        previous block's hash is checked against the current block's previous_hash field.
        
        Returns:
            bool: True if the entire blockchain is valid, False otherwise.
        """
        logger.info("Validating the entire blockchain.")
        blockchain = self.get_blockchain()
        
        for i in range(1, len(blockchain)):
            current_block = blockchain[i]
            previous_block = blockchain[i - 1]
            
            if not self.validate_block(current_block):
                logger.error(f"Block {current_block.index} failed validation.")
                return False
            
            if current_block.previous_hash != previous_block.hash:
                logger.error(f"Block {current_block.index} has an incorrect previous hash.")
                return False
        
        logger.info("Blockchain validation completed successfully.")
        return True
