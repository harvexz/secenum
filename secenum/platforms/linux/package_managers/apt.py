"""APT package manager implementation for Debian-based systems."""

import re
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging
from pathlib import Path

from .base import PackageManagerInterface, PackageInfo, PackageManagerException

logger = logging.getLogger(__name__)

class AptPackageManager(PackageManagerInterface):
    """Package manager implementation for APT (Debian/Ubuntu)."""
    
    DPKG_STATUS_PATH = "/var/lib/dpkg/status"
    APT_SOURCES_PATH = "/etc/apt/sources.list"
    APT_SOURCES_DIR = "/etc/apt/sources.list.d"
    
    def __init__(self):
        super().__init__()
        if not self._is_debian_based():
            raise PackageManagerException("This system is not Debian-based")
    
    def _is_debian_based(self) -> bool:
        """Check if the system is Debian-based."""
        return os.path.exists(self.DPKG_STATUS_PATH)
    
    def get_installed_packages(self) -> Dict[str, PackageInfo]:
        """Get all installed packages with their information."""
        packages = {}
        stdout, stderr, retcode = self.execute_command(["dpkg-query", "-W", "-f=${Package}\\t${Version}\\t${Architecture}\\t${Status}\\t${Maintainer}\\t${Description}\\n"])
        
        if retcode != 0:
            raise PackageManagerException(f"Failed to get package list: {stderr}")
        
        for line in stdout.splitlines():
            try:
                pkg, version, arch, status, maintainer, desc = line.split("\t")
                if "installed" not in status:
                    continue
                
                # Get package size
                size_out, _, _ = self.execute_command(["dpkg-query", "-W", "-f=${Installed-Size}", pkg])
                size = int(size_out.strip()) * 1024 if size_out.strip().isdigit() else None
                
                packages[pkg] = PackageInfo(
                    name=pkg,
                    version=version,
                    architecture=arch,
                    maintainer=maintainer,
                    description=desc,
                    size=size,
                    signature_valid=self._verify_package_signature(pkg)
                )
            except ValueError as e:
                logger.warning(f"Failed to parse package info for line: {line}. Error: {str(e)}")
                continue
        
        return packages
    
    def verify_package(self, package_name: str) -> bool:
        """Verify package integrity and signature."""
        # Verify package files
        _, _, retcode = self.execute_command(["dpkg", "--verify", package_name])
        if retcode != 0:
            return False
        
        # Verify package signature
        return self._verify_package_signature(package_name)
    
    def _verify_package_signature(self, package_name: str) -> bool:
        """Verify package signature using apt-key."""
        try:
            _, _, retcode = self.execute_command(["apt-key", "verify", package_name])
            return retcode == 0
        except PackageManagerException:
            return False
    
    def verify_repository_sources(self) -> Dict[str, bool]:
        """Verify repository sources are valid and secure."""
        results = {}
        
        # Check main sources file
        if os.path.exists(self.APT_SOURCES_PATH):
            results[self.APT_SOURCES_PATH] = self._verify_source_file(self.APT_SOURCES_PATH)
        
        # Check sources.list.d directory
        if os.path.exists(self.APT_SOURCES_DIR):
            for source_file in Path(self.APT_SOURCES_DIR).glob("*.list"):
                results[str(source_file)] = self._verify_source_file(str(source_file))
        
        return results
    
    def _verify_source_file(self, file_path: str) -> bool:
        """Verify a single source file."""
        try:
            # Check if the source uses HTTPS
            with open(file_path, 'r') as f:
                content = f.read()
                # Skip commented lines and verify HTTPS usage
                for line in content.splitlines():
                    if line.strip() and not line.strip().startswith("#"):
                        if "http://" in line and "https://" not in line:
                            return False
            return True
        except Exception as e:
            logger.error(f"Failed to verify source file {file_path}: {str(e)}")
            return False
    
    def get_package_files(self, package_name: str) -> List[str]:
        """Get list of files installed by a package."""
        stdout, stderr, retcode = self.execute_command(["dpkg-query", "-L", package_name])
        if retcode != 0:
            raise PackageManagerException(f"Failed to get file list for {package_name}: {stderr}")
        return [line.strip() for line in stdout.splitlines() if line.strip()]