"""
ML Model loading and inference logic.
This module handles all machine learning operations.
"""

import joblib
import os
import logging
from pathlib import Path
from typing import Optional, List, Tuple
import time
from datetime import datetime

from preprocessing import preprocess_text
from config import settings


logger = logging.getLogger(__name__)


class ModelNotLoadedError(Exception):
    """Raised when models are not loaded."""
    pass


class InferenceError(Exception):
    """Raised when inference fails."""
    pass


class MLModel:
    """
    ML Model manager for expense categorization.
    
    Handles model loading, caching, and inference.
    Models are loaded once at startup and kept in memory.
    """
    
    def __init__(self):
        """Initialize model manager."""
        self._model = None
        self._vectorizer = None
        self._model_loaded = False
        self._load_time: Optional[datetime] = None
        self._model_version = "1.2.0"  # Track model version
        
    @property
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self._model_loaded and self._model is not None and self._vectorizer is not None
    
    @property
    def model_version(self) -> str:
        """Get model version."""
        return self._model_version
    
    @property
    def categories(self) -> List[str]:
        """Get list of supported categories."""
        if not self.is_loaded:
            return []
        return list(self._model.classes_)
    
    def load_models(self, model_path: Optional[str] = None, vectorizer_path: Optional[str] = None) -> bool:
        """
        Load ML models from disk.
        
        Args:
            model_path: Path to model file (uses config default if None)
            vectorizer_path: Path to vectorizer file (uses config default if None)
        
        Returns:
            True if successful, False otherwise
        
        Raises:
            FileNotFoundError: If model files don't exist
            Exception: If model loading fails
        """
        model_path = model_path or settings.model_path
        vectorizer_path = vectorizer_path or settings.vectorizer_path
        
        logger.info(f"Loading models from {model_path} and {vectorizer_path}")
        
        # Check if files exist
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        if not os.path.exists(vectorizer_path):
            logger.error(f"Vectorizer file not found: {vectorizer_path}")
            raise FileNotFoundError(f"Vectorizer file not found: {vectorizer_path}")
        
        try:
            # Load model and vectorizer
            start_time = time.time()
            
            self._model = joblib.load(model_path)
            self._vectorizer = joblib.load(vectorizer_path)
            
            load_time = time.time() - start_time
            
            self._model_loaded = True
            self._load_time = datetime.now()
            
            logger.info(
                f"✓ Models loaded successfully in {load_time:.2f}s. "
                f"Categories: {len(self.categories)}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            self._model_loaded = False
            raise
    
    def predict(
        self, 
        description: str, 
        include_alternatives: bool = True,
        top_n_alternatives: int = 3
    ) -> dict:
        """
        Predict category for a transaction description.
        
        Args:
            description: Transaction description text
            include_alternatives: Whether to include alternative predictions
            top_n_alternatives: Number of alternative predictions to include
        
        Returns:
            Dictionary with prediction results:
            {
                'category': str,
                'confidence': float,
                'alternatives': List[dict],
                'preprocessed_text': str,
                'inference_time_ms': float
            }
        
        Raises:
            ModelNotLoadedError: If models are not loaded
            InferenceError: If prediction fails
        """
        if not self.is_loaded:
            raise ModelNotLoadedError("Models are not loaded. Call load_models() first.")
        
        try:
            start_time = time.time()
            
            # Preprocess input
            processed_text = preprocess_text(description)
            
            if not processed_text:
                raise InferenceError("Description contains no valid content after preprocessing")
            
            # Vectorize
            X = self._vectorizer.transform([processed_text])
            
            # Predict
            predicted_category = self._model.predict(X)[0]
            probabilities = self._model.predict_proba(X)[0]
            confidence = float(probabilities.max())
            
            # Get alternatives
            alternatives = []
            if include_alternatives:
                # Get top N alternatives (excluding the main prediction)
                prob_indices = probabilities.argsort()[::-1]
                for idx in prob_indices[1:top_n_alternatives+1]:
                    alternatives.append({
                        'category': self._model.classes_[idx],
                        'confidence': float(probabilities[idx])
                    })
            
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = {
                'category': predicted_category,
                'confidence': confidence,
                'alternatives': alternatives,
                'preprocessed_text': processed_text,
                'inference_time_ms': round(inference_time, 2)
            }
            
            logger.debug(
                f"Prediction: '{description}' -> {predicted_category} "
                f"(confidence: {confidence:.4f}, time: {inference_time:.2f}ms)"
            )
            
            return result
            
        except ModelNotLoadedError:
            raise
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise InferenceError(f"Prediction failed: {str(e)}")
    
    def predict_batch(self, descriptions: List[str]) -> List[dict]:
        """
        Predict categories for multiple descriptions.
        
        Args:
            descriptions: List of transaction descriptions
        
        Returns:
            List of prediction results
        
        Raises:
            ModelNotLoadedError: If models are not loaded
        """
        if not self.is_loaded:
            raise ModelNotLoadedError("Models are not loaded. Call load_models() first.")
        
        results = []
        for description in descriptions:
            try:
                result = self.predict(description, include_alternatives=False)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch prediction failed for '{description}': {str(e)}")
                results.append({
                    'category': None,
                    'confidence': 0.0,
                    'error': str(e)
                })
        
        return results
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        if not self.is_loaded:
            return {
                'loaded': False,
                'error': 'Models not loaded'
            }
        
        return {
            'loaded': True,
            'name': 'expense_categorizer',
            'version': self._model_version,
            'algorithm': 'Multinomial Naive Bayes',
            'features': 'TF-IDF',
            'categories': self.categories,
            'num_categories': len(self.categories),
            'loaded_at': self._load_time.isoformat() if self._load_time else None
        }


# Global model instance
ml_model = MLModel()


def preload_models():
    """
    Preload models at application startup.
    
    This ensures models are ready before handling requests.
    """
    if settings.model_preload:
        try:
            logger.info("Preloading models...")
            ml_model.load_models()
            logger.info("✓ Models preloaded successfully")
        except Exception as e:
            logger.error(f"Failed to preload models: {str(e)}")
            logger.warning("Service will start but predictions will fail until models are loaded")
