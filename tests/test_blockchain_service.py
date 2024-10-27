import pytest
from unittest.mock import MagicMock, patch
from app.services.blockchain_service import BlockchainService
from app.models.block import Block

@pytest.fixture
def blockchain_service():
    """
    Fixture for setting up the BlockchainService with a mocked CosmosDB service.
    
    Mocks the interactions with CosmosDB to avoid actual database operations.
    """
    with patch('app.services.cosmosdb_service.CosmosClient'):
        # Mock the CosmosDB service methods before initializing BlockchainService
        mock_cosmos_service = MagicMock()
        mock_cosmos_service.get_validators = MagicMock(return_value=["validator_001"])
        
        # Inject the mocked CosmosDB service into BlockchainService
        with patch('app.services.blockchain_service.CosmosDBService', return_value=mock_cosmos_service):
            service = BlockchainService()
        
        # Set up other mocks
        service.cosmosdb_service.store_validator = MagicMock(return_value=True)
        service.cosmosdb_service.store_medical_record = MagicMock(return_value="medical_record_001")
        service.cosmosdb_service.get_medical_record = MagicMock(return_value={
            "id": "record_001",
            "diagnosis": "Test Diagnosis",
            "treatment": "Test Treatment"
        })
        service.cosmosdb_service.store_block = MagicMock(return_value=True)
        service.cosmosdb_service.blockchain_container = MagicMock()
        
        # Mock blockchain retrieval for testing block validation
        service.get_last_block = MagicMock(return_value={
            "index": 1,
            "timestamp": "2023-10-01T12:00:00Z",
            "patient_id": "patient_001",
            "medical_record_id": "record_001",
            "previous_hash": "previous_hash",
            "hash": "correct_hash",
            "validator_id": "validator_001"
        })

        return service

def test_add_validator(blockchain_service):
    """
    Test that a validator can be successfully added to the list.
    
    Validates the correct storage of a new validator in CosmosDB.
    """
    blockchain_service.add_validator("validator_002")
    assert "validator_002" in blockchain_service.validators
    blockchain_service.cosmosdb_service.store_validator.assert_called_with("validator_002")

def test_create_block_with_authorized_validator(blockchain_service):
    """
    Test that a block is created successfully with an authorized validator.
    
    Verifies the creation of a new block and its correct interaction with CosmosDB.
    """
    patient_id = "patient_001"
    medical_record = {
        "type": "PhysicalExam",
        "diagnosis": "Hypertension",
        "treatment": "Medication"
    }
    validator_id = "validator_001"

    new_block = blockchain_service.create_block_with_medical_record(patient_id, medical_record, validator_id)
    assert new_block.patient_id == patient_id
    assert new_block.validator_id == validator_id
    assert new_block.medical_record_id is not None
    blockchain_service.cosmosdb_service.store_medical_record.assert_called_once_with(medical_record)
    blockchain_service.cosmosdb_service.store_block.assert_called_once()

def test_create_block_with_unauthorized_validator(blockchain_service):
    """
    Test that creating a block with an unauthorized validator raises a ValueError.
    """
    patient_id = "patient_001"
    medical_record = {
        "diagnosis": "Hypertension",
        "treatment": "Medication"
    }
    unauthorized_validator_id = "validator_999"

    with pytest.raises(ValueError, match="Unauthorized validator attempted to create a block."):
        blockchain_service.create_block_with_medical_record(patient_id, medical_record, unauthorized_validator_id)

def test_validate_correct_block(blockchain_service):
    """
    Test the validation of a correct block with a valid hash.
    
    Confirms that a manually created block with a correct hash passes validation.
    """
    block = Block(
        index=1,
        timestamp="2023-10-01T12:00:00Z",
        patient_id="patient_001",
        medical_record_id="record_001",
        previous_hash="previous_hash",
        validator_id="validator_001",
        hash="correct_hash"
    )

    blockchain_service.compute_block_hash = MagicMock(return_value="correct_hash")
    is_valid = blockchain_service.validate_block(block)
    assert is_valid

def test_validate_incorrect_block(blockchain_service):
    """
    Test the detection of an invalid block due to an incorrect hash.
    
    Ensures that the validation fails when the block's hash does not match the expected value.
    """
    block = Block(
        index=1,
        timestamp="2023-10-01T12:00:00Z",
        patient_id="patient_001",
        medical_record_id="record_001",
        previous_hash="previous_hash",
        validator_id="validator_001",
        hash="wrong_hash"
    )

    blockchain_service.compute_block_hash = MagicMock(return_value="correct_hash")
    is_valid = blockchain_service.validate_block(block)
    assert not is_valid
