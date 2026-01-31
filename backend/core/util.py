"""Reusable utility functions."""

import logging
import sys
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def safe_str(value: str | None, default: str = "") -> str:
    """Safely convert value to string with default."""
    return value if value is not None else default


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for a module.
    
    Creates a logger with consistent formatting and output to stdout.
    Debug messages are enabled for development.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
        
    Returns:
        Configured Logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console handler with formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            "[%(levelname)s] %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Prevent propagation to root logger (avoid duplicate logs)
        logger.propagate = False
    
    return logger
