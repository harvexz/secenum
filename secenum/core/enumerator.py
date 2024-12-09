"""Main enumeration coordinator module."""

from typing import Dict, Any, Optional
import logging
import platform
from datetime import datetime

from ..platforms.linux.package_managers.apt import AptPackageManager
from ..platforms.linux.system_info import SystemInfoGatherer
from ..platforms.linux.services import ServiceEnumerator

logger = logging.getLogger(__name__)

class EnumerationResult:
    """Container for enumeration results."""
    def __init__(self):
        self.timestamp = datetime.now()
        self.system_info = {}
        self.packages = {}
        self.services = {}
        self.security_info = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary format."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "system_info": self.system_info,
            "packages": self.packages,
            "services": self.services,
            "security_info": self.security_info
        }

class SystemEnumerator:
    """Main system enumeration coordinator."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.result = EnumerationResult()
        self._init_components()

    def _init_components(self):
        """Initialize appropriate components based on system type."""
        if self.system != "linux":
            raise NotImplementedError(f"System {self.system} is not supported yet")
            
        self.system_info = SystemInfoGatherer()
        if self.system_info.is_debian_based():
            self.package_manager = AptPackageManager()
        else:
            raise NotImplementedError("Only Debian-based systems are supported")
            
        self.service_enumerator = ServiceEnumerator()

    def enumerate_all(self) -> Dict[str, Any]:
        """Perform complete system enumeration."""
        logger.info("Starting complete system enumeration")
        
        try:
            # Gather system information
            sys_info = self.system_info.get_system_info()
            self.result.system_info = {
                "hostname": sys_info.hostname,
                "kernel": sys_info.kernel_version,
                "distribution": sys_info.distribution,
                "version": sys_info.distribution_version,
                "architecture": sys_info.architecture,
                "cpu_info": sys_info.cpu_info,
                "memory_info": sys_info.memory_info
            }
            
            # Gather security information
            self.result.security_info = self.system_info.get_security_info()
            
            # Enumerate packages
            logger.info("Enumerating installed packages")
            self.result.packages = self.package_manager.get_installed_packages()
            
            # Enumerate services
            logger.info("Enumerating system services")
            services = self.service_enumerator.get_all_services()
            
            # Add security analysis for each service
            for service_name, service_info in services.items():
                security_analysis = self.service_enumerator.analyze_service_security(service_name)
                setattr(service_info, "security_analysis", security_analysis)
            
            self.result.services = services
            
            return self.result.to_dict()
            
        except Exception as e:
            logger.error(f"Enumeration failed: {str(e)}")
            raise

    def enumerate_packages(self) -> Dict[str, Any]:
        """Enumerate only installed packages."""
        return {"packages": self.package_manager.get_installed_packages()}

    def enumerate_services(self) -> Dict[str, Any]:
        """Enumerate only system services."""
        return {"services": self.service_enumerator.get_all_services()}

    def analyze_security(self) -> Dict[str, Any]:
        """Perform security analysis of the system."""
        security_info = self.system_info.get_security_info()
        services = self.service_enumerator.get_all_services()
        
        # Analyze package security
        package_security = {
            pkg: self.package_manager.verify_package(pkg)
            for pkg in self.package_manager.get_installed_packages().keys()
        }
        
        # Analyze service security
        service_security = {
            name: self.service_enumerator.analyze_service_security(name)
            for name in services.keys()
        }
        
        return {
            "system_security": security_info,
            "package_security": package_security,
            "service_security": service_security
        }