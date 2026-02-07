"""
Utility functions for the Document Q&A Agent.
Provides logging, configuration, and helper functions.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration management class."""
    
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
    
    # Processing Settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    PDF_DIR = DATA_DIR / "pdfs"
    PROCESSED_DIR = DATA_DIR / "processed"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if cls.LLM_PROVIDER == "gemini" and not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return True


def setup_logging(name: str = __name__, level: str = None) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    if level is None:
        level = Config.LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    # Remove potentially dangerous characters
    sanitized = text.strip()
    
    # Limit length to prevent DoS
    max_length = 10000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = Config.CHUNK_SIZE
    if overlap is None:
        overlap = Config.CHUNK_OVERLAP
    
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    
    return chunks


def extract_metrics(text: str) -> Dict[str, Any]:
    """
    Extract numerical metrics from text.
    
    Args:
        text: Text containing metrics
        
    Returns:
        Dictionary of extracted metrics
    """
    import re
    
    metrics = {}
    
    # Common metric patterns
    patterns = {
        'accuracy': r'accuracy[:\s]+(\d+\.?\d*)%?',
        'f1_score': r'f1[- ]?score[:\s]+(\d+\.?\d*)',
        'precision': r'precision[:\s]+(\d+\.?\d*)%?',
        'recall': r'recall[:\s]+(\d+\.?\d*)%?',
        'auc': r'auc[:\s]+(\d+\.?\d*)',
        'loss': r'loss[:\s]+(\d+\.?\d*)',
    }
    
    for metric_name, pattern in patterns.items():
        matches = re.findall(pattern, text.lower())
        if matches:
            metrics[metric_name] = [float(m) for m in matches]
    
    return metrics


def save_json(data: Dict, filepath: str) -> None:
    """
    Save data as JSON file.
    
    Args:
        data: Dictionary to save
        filepath: Path to save file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str) -> Dict:
    """
    Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded dictionary
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_directories() -> None:
    """Create necessary project directories."""
    directories = [
        Config.DATA_DIR,
        Config.PDF_DIR,
        Config.PROCESSED_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, calls_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: Maximum calls allowed per minute
        """
        import time
        from collections import deque
        
        self.calls_per_minute = calls_per_minute
        self.calls = deque()
        self.time = time
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = self.time.time()
        
        # Remove calls older than 1 minute
        while self.calls and self.calls[0] < now - 60:
            self.calls.popleft()
        
        # Wait if at limit
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                self.time.sleep(sleep_time)
        
        self.calls.append(now)


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        
    Returns:
        Decorator function
    """
    from functools import wraps
    import time
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        raise last_exception
            
            raise last_exception
        
        return wrapper
    
    return decorator