"""Base interface for Linux package managers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import subprocess
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PackageInfo:
    """Data class for package information."""
    name: str
    version: str
    architecture: str
    install_date: Optional[datetime] = None
    size: Optional[int] = None
    source: Optional[str] = None
    maintainer: Optional[str] = None
    signature_valid: Optional[bool] = None
    description: Optional[str] = None

class PackageManagerException(Exception):
    """Base exception for package manager operations."""
    pass

class PackageManagerInterface(ABC):
    """Abstract base class for package manager implementations."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def get_installed_packages(self) -> Dict[str, PackageInfo]:
        """Get all installed packages with their information."""
        pass
    
    @abstractmethod
    def verify_package(self, package_name: str) -> bool:
        """Verify package integrity and signature."""
        pass
    
    @abstractmethod
    def verify_repository_sources(self) -> Dict[str, bool]:
        """Verify repository sources are valid and secure."""
        pass
    
    @abstractmethod
    def get_package_files(self, package_name: str) -> List[str]:
        """Get list of files installed by a package."""
        pass
    
    def execute_command(self, command: List[str], timeout: int = 30) -> Tuple[str, str, int]:
        """
        Safely execute a command and return its output.
        
        Args:
            command: List of command and arguments
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (stdout, stderr, return_code)
            
        Raises:
            PackageManagerException: If command execution fails
        """
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={"LC_ALL": "C"}  # Ensure consistent output format
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout, stderr, process.returncode
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise PackageManagerException(f"Command timed out after {timeout} seconds: {' '.join(command)}")
            
        except subprocess.SubprocessError as e:
            raise PackageManagerException(f"Failed to execute command: {' '.join(command)}. Error: {str(e)}")
            
    def check_root_permissions(self) -> bool:
        """Check if the script has root permissions."""
        try:
            return subprocess.check_call(["id", "-u"]) == 0
        except subprocess.SubprocessError:
            return False