from pydantic import BaseModel
from datetime import datetime, timezone

class Block(BaseModel):
    """
    A model representing a block in the blockchain.
    
    Each block contains metadata, a reference to a medical record, and information
    required to maintain blockchain integrity, such as hashes and validator information.
    """
    
    index: int
    """int: The position of the block in the blockchain (starting from 1)."""

    timestamp: datetime
    """datetime: The time when the block was created. Automatically set to the current UTC time."""

    patient_id: str
    """str: A unique identifier for the patient associated with this block."""

    medical_record_id: str
    """str: A unique identifier for the referenced medical record stored off-chain."""

    previous_hash: str
    """str: The hash of the previous block in the chain, used to maintain blockchain integrity."""

    hash: str
    """str: The SHA-256 hash of the current block, calculated based on the block's contents."""

    validator_id: str
    """str: The identifier of the validator who created this block."""
    
    def __init__(self, **data):
        """
        Initialize a new block.
        
        Automatically sets the timestamp to the current UTC time, ensuring the block's creation time
        is accurate and tamper-proof.
        
        Args:
            **data: Arbitrary keyword arguments containing the block's attributes.
        """
        data['timestamp'] = datetime.now(timezone.utc)
        super().__init__(**data)
