from typing import Optional
from pydantic import BaseModel

class MedicalRecordRequest(BaseModel):
    """
    Model for the medical record request data.
    """
    type: str
    note: Optional[str] = None
    patient_id: str
    work_type: Optional[str] = None
    residency_type: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    smoking_status: Optional[str] = None
    systolic_pressure: Optional[float] = None
    diastolic_pressure: Optional[float] = None
    glucose_level: Optional[float] = None
    disease_type: Optional[str] = None
