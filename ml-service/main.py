"""
ML Inference Service - FastAPI Application

This is a standalone microservice for ML-based expense categorization.
It is completely isolated from the backend and communicates only via REST API.

Key Principles:
- NO database access
- NO authentication logic
- NO business rules
- ONLY inference and predictions
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from schemas import (
    PredictionRequest,
    PredictionResponse,
    PredictionResult,
    PredictionMetadata,
    ErrorResponse,
    ErrorDetail,
    HealthResponse,
    ModelInfoResponse,
    ModelInfo,
    BatchPredictionRequest,
    BatchPredictionResponse,
    BatchPredictionItem,
    BatchPredictionMetadata,
)
from models import ml_model, preload_models, ModelNotLoadedError, InferenceError
from preprocessing import validate_text


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Application startup time
APP_START_TIME = datetime.now()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    
    # Preload models if configured
    if settings.model_preload:
        try:
            preload_models()
        except Exception as e:
            logger.error(f"Failed to preload models: {e}")
            logger.warning("Service starting without models loaded")
    
    logger.info(f"Service ready on {settings.host}:{settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ML Inference Service")


# Initialize FastAPI app
app = FastAPI(
    title="ML Inference Service",
    description="Standalone ML service for expense categorization",
    version=settings.service_version,
    lifespan=lifespan,
)


# CORS middleware (configure based on your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ModelNotLoadedError)
async def model_not_loaded_handler(request, exc):
    """Handle model not loaded errors."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            error=ErrorDetail(
                code="MODEL_NOT_LOADED",
                message="ML models are not loaded",
                details=str(exc)
            )
        ).model_dump()
    )


@app.exception_handler(InferenceError)
async def inference_error_handler(request, exc):
    """Handle inference errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INFERENCE_ERROR",
                message="Prediction failed",
                details=str(exc)
            )
        ).model_dump()
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "predict": "/api/v1/predict/category",
            "model_info": "/api/v1/model/info",
            "docs": "/docs"
        }
    }


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        HealthResponse with service status
    """
    uptime = (datetime.now() - APP_START_TIME).total_seconds()
    
    if ml_model.is_loaded:
        return HealthResponse(
            status="healthy",
            service=settings.service_name,
            version=settings.service_version,
            models_loaded=True,
            uptime_seconds=round(uptime, 2)
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=HealthResponse(
                status="unhealthy",
                service=settings.service_name,
                version=settings.service_version,
                models_loaded=False,
                uptime_seconds=round(uptime, 2),
                error="Models not loaded"
            ).model_dump()
        )


# Prediction endpoint
@app.post("/api/v1/predict/category", response_model=PredictionResponse)
async def predict_category(request: PredictionRequest):
    """
    Predict expense category from description.
    
    Args:
        request: PredictionRequest with description
    
    Returns:
        PredictionResponse with category and confidence
    
    Raises:
        HTTPException: If validation fails or prediction errors
    """
    # Validate input
    is_valid, error_msg = validate_text(
        request.description,
        min_length=settings.min_description_length,
        max_length=settings.max_description_length
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_INPUT",
                    message=error_msg,
                    field="description"
                )
            ).model_dump()
        )
    
    try:
        # Perform prediction
        result = ml_model.predict(
            request.description,
            include_alternatives=True,
            top_n_alternatives=3
        )
        
        # Build response
        response = PredictionResponse(
            success=True,
            prediction=PredictionResult(
                category=result['category'],
                confidence=result['confidence'],
                alternatives=result.get('alternatives', [])
            ),
            metadata=PredictionMetadata(
                model_version=ml_model.model_version,
                inference_time_ms=result['inference_time_ms'],
                preprocessed_text=result['preprocessed_text']
            )
        )
        
        return response
        
    except ModelNotLoadedError:
        raise
    except InferenceError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_ERROR",
                    message="An unexpected error occurred",
                    details=str(e)
                )
            ).model_dump()
        )


# Model info endpoint
@app.get("/api/v1/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """
    Get information about the loaded ML model.
    
    Returns:
        ModelInfoResponse with model details
    """
    if not ml_model.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="MODEL_NOT_LOADED",
                    message="Models are not loaded"
                )
            ).model_dump()
        )
    
    model_info = ml_model.get_model_info()
    
    return ModelInfoResponse(
        model=ModelInfo(
            name=model_info['name'],
            version=model_info['version'],
            algorithm=model_info['algorithm'],
            features=model_info['features'],
            categories=model_info['categories'],
            training_samples=None,  # Not tracked in this version
            accuracy=None,  # Not tracked in this version
            last_trained=None  # Not tracked in this version
        )
    )


# Batch prediction endpoint (optional)
@app.post("/api/v1/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest):
    """
    Predict categories for multiple descriptions at once.
    
    Args:
        request: BatchPredictionRequest with list of descriptions
    
    Returns:
        BatchPredictionResponse with predictions for all descriptions
    """
    if not ml_model.is_loaded:
        raise ModelNotLoadedError("Models not loaded")
    
    start_time = time.time()
    
    predictions = []
    successful = 0
    failed = 0
    
    for description in request.descriptions:
        try:
            result = ml_model.predict(description, include_alternatives=False)
            predictions.append(
                BatchPredictionItem(
                    description=description,
                    category=result['category'],
                    confidence=result['confidence']
                )
            )
            successful += 1
        except Exception as e:
            logger.error(f"Batch prediction failed for '{description}': {str(e)}")
            failed += 1
            # Optionally add failed items with null category
            predictions.append(
                BatchPredictionItem(
                    description=description,
                    category="",
                    confidence=0.0
                )
            )
    
    total_time = (time.time() - start_time) * 1000
    
    return BatchPredictionResponse(
        success=True,
        predictions=predictions,
        metadata=BatchPredictionMetadata(
            total=len(request.descriptions),
            successful=successful,
            failed=failed,
            total_inference_time_ms=round(total_time, 2)
        )
    )


# Manual model loading endpoint (for debugging)
@app.post("/api/v1/model/load")
async def load_model():
    """
    Manually trigger model loading.
    Useful for debugging or reloading updated models.
    """
    try:
        ml_model.load_models()
        return {
            "success": True,
            "message": "Models loaded successfully",
            "model_info": ml_model.get_model_info()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="LOAD_ERROR",
                    message="Failed to load models",
                    details=str(e)
                )
            ).model_dump()
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # Set to True for development
        log_level=settings.log_level.lower()
    )
