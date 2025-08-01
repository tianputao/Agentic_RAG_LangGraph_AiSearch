"""
Utility functions and helpers for the Agentic RAG system
Contains common functionality used across different modules
"""

import re
import hashlib
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timezone
import time
from functools import wraps

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
    
    # Trim whitespace
    text = text.strip()
    
    return text

def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length allowed
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text string
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text using simple regex patterns
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Remove common stop words (simplified list)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    # Extract words (3+ characters)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter stop words and get unique keywords
    keywords = list(set(word for word in words if word not in stop_words))
    
    # Sort by length (longer keywords first) and return top N
    keywords.sort(key=len, reverse=True)
    
    return keywords[:max_keywords]

def generate_content_hash(content: str) -> str:
    """
    Generate a hash for content deduplication
    
    Args:
        content: Content to hash
        
    Returns:
        SHA-256 hash string
    """
    if not content:
        return ""
    
    # Normalize content for consistent hashing
    normalized = clean_text(content).lower()
    
    # Generate hash
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    Format timestamp for display
    
    Args:
        timestamp: Optional datetime object, defaults to current time
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

def safe_json_parse(json_str: str, default: Any = None) -> Any:
    """
    Safely parse JSON string with fallback
    
    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse JSON: {json_str[:100]}...")
        return default

def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split a list into batches of specified size
    
    Args:
        items: List to batch
        batch_size: Size of each batch
        
    Returns:
        List of batched lists
    """
    if batch_size <= 0:
        raise ValueError("Batch size must be positive")
    
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    
    return batches

def measure_execution_time(func):
    """
    Decorator to measure function execution time
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function with timing
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f} seconds: {e}")
            raise
    
    return wrapper

def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL format
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove excessive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Trim and ensure non-empty
    sanitized = sanitized.strip('_')
    
    if not sanitized:
        sanitized = "file"
    
    return sanitized

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple text similarity using Jaccard index
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not text1 or not text2:
        return 0.0
    
    # Tokenize and create sets
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator for retrying functions on exceptions
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay on each retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}: {e}. "
                            f"Retrying in {current_delay:.1f} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")
            
            # Re-raise the last exception if all retries failed
            raise last_exception
        
        return wrapper
    return decorator

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries with nested support
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    
    for d in dicts:
        for key, value in d.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dictionaries(result[key], value)
            else:
                result[key] = value
    
    return result

def validate_azure_resource_name(name: str, resource_type: str = "general") -> bool:
    """
    Validate Azure resource naming conventions
    
    Args:
        name: Resource name to validate
        resource_type: Type of Azure resource
        
    Returns:
        True if name is valid
    """
    if not name:
        return False
    
    # General Azure naming rules
    if not re.match(r'^[a-zA-Z0-9-]+$', name):
        return False
    
    # Length constraints based on resource type
    length_limits = {
        "storage": (3, 24),
        "search": (2, 60),
        "openai": (2, 64),
        "general": (1, 50)
    }
    
    min_len, max_len = length_limits.get(resource_type, length_limits["general"])
    
    if not (min_len <= len(name) <= max_len):
        return False
    
    # Cannot start or end with hyphen
    if name.startswith('-') or name.endswith('-'):
        return False
    
    return True

class PerformanceTracker:
    """Simple performance tracking utility"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.metrics[operation] = {"start_time": time.time()}
    
    def end_timer(self, operation: str) -> float:
        """End timing and return duration"""
        if operation in self.metrics:
            duration = time.time() - self.metrics[operation]["start_time"]
            self.metrics[operation]["duration"] = duration
            return duration
        return 0.0
    
    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get all tracked metrics"""
        return self.metrics.copy()
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()

# Global performance tracker instance
performance_tracker = PerformanceTracker()

# Example usage and testing
if __name__ == "__main__":
    # Test utility functions
    test_text = "This is a sample text with various characters! @#$% Testing 123."
    
    print("Testing utility functions:")
    print(f"Original: {test_text}")
    print(f"Cleaned: {clean_text(test_text)}")
    print(f"Truncated: {truncate_text(test_text, 20)}")
    print(f"Keywords: {extract_keywords(test_text)}")
    print(f"Hash: {generate_content_hash(test_text)[:16]}...")
    print(f"Timestamp: {format_timestamp()}")
    
    # Test performance tracking
    performance_tracker.start_timer("test_operation")
    time.sleep(0.1)  # Simulate work
    duration = performance_tracker.end_timer("test_operation")
    print(f"Test operation took: {duration:.3f} seconds")
