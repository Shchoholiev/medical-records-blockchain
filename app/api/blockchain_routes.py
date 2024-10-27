import logging
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.medical_record import MedicalRecordRequest
from app.services.blockchain_service import BlockchainService
from app.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()
blockchain_service = BlockchainService()

@router.post("", response_model=dict)
async def create_record(
    record: MedicalRecordRequest,
    user: dict = Depends(get_current_user)
):
    try:
        user_id = user.get("user_id")
        validator_id = user.get("validator_id")
        if not validator_id:
            logger.error("Validator ID is missing from the user data.")
            raise ValueError("Validator ID is missing from the user data.")

        medical_record_data = record.model_dump()
        logger.info(f"Creating a new medical record block for patient {record.patient_id} by user {user_id}.")

        new_block = blockchain_service.create_block_with_medical_record(
            patient_id=record.patient_id,
            medical_record=medical_record_data,
            validator_id=validator_id,
            user_id=user_id
        )

        logger.info(f"Successfully created block with index {new_block.index} for patient {record.patient_id}.")
        return new_block.model_dump()
    
    except ValueError as e:
        logger.warning(f"Bad request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

@router.get("", response_model=List[dict])
async def get_all_blocks(user: dict = Depends(get_current_user)):
    try:
        logger.info(f"User {user.get('user_id')} requested the full blockchain.")
        blockchain = blockchain_service.get_blockchain()
        logger.info(f"Retrieved {len(blockchain)} blocks from the blockchain.")
        return [block.model_dump() for block in blockchain]
    except Exception as e:
        logger.error(f"Internal Server Error while retrieving blockchain: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )

@router.get("/validate", response_model=dict)
async def validate_blockchain(user: dict = Depends(get_current_user)):
    """
    Validate the entire blockchain and return the result.
    
    This endpoint allows external systems or administrators to verify the blockchain's integrity.
    
    Returns:
        dict: The validation status and any relevant messages.
    """
    try:
        is_valid = blockchain_service.validate_blockchain()
        if is_valid:
            return {"status": "success", "message": "Blockchain is valid."}
        else:
            logger.warning("Blockchain validation failed.")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Blockchain validation failed."
            )
    except Exception as e:
        raise e
    except Exception as e:
        logger.error(f"Error while validating the blockchain: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )