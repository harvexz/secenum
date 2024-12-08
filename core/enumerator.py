"""Core enumeration functionality."""

from typing import Dict, List, Optional
import logging
import platform
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseEnumerator(ABC):
    """Base class for system enumeration."""

    def __init__(self):
        self.results: Dict[str, str] = {}
        self.system = platform.system().lower()

    @abstractmethod
    def enumerate_software(self) -> Dict[str, str]:
        """Enumerate installed software."""
        pass

    @abstractmethod
    def verify_software(self, name: str, version: str) -> bool:
        """Verify software authenticity."""
        pass

    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }