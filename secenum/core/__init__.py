"""Core functionality for SecEnum."""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class EnumerationException(Exception):
    """Base exception for enumeration errors."""
    pass

class SecurityException(Exception):
    """Base exception for security-related errors."""
    pass