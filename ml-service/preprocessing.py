"""
Text preprocessing functions for ML inference.
MUST match the preprocessing used during model training.
"""

import re
from typing import Optional


def preprocess_text(text: str, remove_noise_words: bool = True) -> str:
    """
    Preprocess expense description text.
    
    This MUST exactly match the preprocessing used during training.
    Any deviation will cause prediction accuracy to drop.
    
    Args:
        text: Raw input text
        remove_noise_words: Whether to remove common noise words
    
    Returns:
        Cleaned and preprocessed text
    
    Examples:
        >>> preprocess_text("Zomato Order!")
        "zomato order"
        
        >>> preprocess_text("₹500 for food")
        "for food"
        
        >>> preprocess_text("Uber   ride")
        "uber ride"
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove noise words (optional, must match training)
    if remove_noise_words:
        noise_words = [
            'online', 'advance', 'emergency', 'monthly',
            'for office', 'for home', 'personal', 'with family',
            'charges', 'payment', 'bill', 'expense', 'fees'
        ]
        for word in noise_words:
            text = re.sub(r'\b' + word + r'\b', '', text)
    
    # Remove special characters and numbers (keep only letters and spaces)
    text = re.sub(r'[^a-z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def validate_text(text: str, min_length: int = 1, max_length: int = 500) -> tuple[bool, Optional[str]]:
    """
    Validate input text meets requirements.
    
    Args:
        text: Input text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not isinstance(text, str):
        return False, "Text must be a non-empty string"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"Text must be at least {min_length} character(s)"
    
    if len(text) > max_length:
        return False, f"Text must not exceed {max_length} characters"
    
    # Check if text becomes empty after preprocessing
    processed = preprocess_text(text)
    if not processed:
        return False, "Text contains no valid content after preprocessing"
    
    return True, None


def extract_features(text: str) -> dict:
    """
    Extract useful features from text for logging/debugging.
    
    Args:
        text: Input text
    
    Returns:
        Dictionary of extracted features
    """
    return {
        'length': len(text),
        'word_count': len(text.split()),
        'has_numbers': bool(re.search(r'\d', text)),
        'has_special_chars': bool(re.search(r'[^a-zA-Z0-9\s]', text)),
        'is_uppercase': text.isupper(),
    }
