"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request schema for category prediction."""
    
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Transaction description to categorize"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata for tracking"
    )
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Ensure description is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()


class AlternativePrediction(BaseModel):
    """Alternative category prediction."""
    
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class PredictionResult(BaseModel):
    """Prediction result with confidence."""
    
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    alternatives: List[AlternativePrediction] = Field(default_factory=list)


class PredictionMetadata(BaseModel):
    """Metadata about the prediction."""
    
    model_version: str
    inference_time_ms: float
    preprocessed_text: str


class PredictionResponse(BaseModel):
    """Successful prediction response."""
    
    success: bool = True
    prediction: PredictionResult
    metadata: PredictionMetadata


class ErrorDetail(BaseModel):
    """Error details."""
    
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response."""
    
    success: bool = False
    error: ErrorDetail


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str  # "healthy" or "unhealthy"
    service: str
    version: str
    models_loaded: bool
    uptime_seconds: Optional[float] = None
    error: Optional[str] = None


class ModelInfo(BaseModel):
    """Model information."""
    
    name: str
    version: str
    algorithm: str
    features: str
    categories: List[str]
    training_samples: Optional[int] = None
    accuracy: Optional[float] = None
    last_trained: Optional[datetime] = None


class ModelInfoResponse(BaseModel):
    """Model info response."""
    
    model: ModelInfo


class BatchPredictionRequest(BaseModel):
    """Batch prediction request."""
    
    descriptions: List[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of descriptions to categorize"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional prediction options"
    )


class BatchPredictionItem(BaseModel):
    """Single item in batch prediction."""
    
    description: str
    category: str
    confidence: float


class BatchPredictionMetadata(BaseModel):
    """Batch prediction metadata."""
    
    total: int
    successful: int
    failed: int
    total_inference_time_ms: float


class BatchPredictionResponse(BaseModel):
    """Batch prediction response."""
    
    success: bool = True
    predictions: List[BatchPredictionItem]
    metadata: BatchPredictionMetadata
