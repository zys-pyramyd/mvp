class FarmerKYCSubmission(BaseModel):
    verification_method: str = "self_verified"  # "self_verified" or "agent_verified"
    verifying_agent_id: Optional[str] = None
    farm_size_hectares: Optional[float] = None
    primary_crops: Optional[List[str]] = []
    farm_location: Optional[str] = None
    additional_notes: Optional[str] = None
