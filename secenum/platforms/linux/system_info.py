"""Linux system information gathering module."""

import os
import platform
import subprocess
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@dataclass
class SystemInfo:
    """Data class for system information."""
    hostname: str
    kernel_version: str
    distribution: str
    distribution_version: str
    architecture: str
    cpu_info: Dict[str, str]
    memory_info: Dict[str, int]
    users: List[str]
    uptime: str
    boot_time: datetime

class SystemInfoGatherer:
    """Gathers detailed system information."""
    
    def __init__(self):
        self._system_info: Optional[SystemInfo] = None
    
    def get_system_info(self) -> SystemInfo:
        """
        Collect and return system information.
        
        Returns:
            SystemInfo object containing system details
        """
        if self._system_info:
            return self._system_info
            
        try:
            self._system_info = SystemInfo(
                hostname=platform.node(),
                kernel_version=platform.release(),
                distribution=self._get_distribution_info()[0],
                distribution_version=self._get_distribution_info()[1],
                architecture=platform.machine(),
                cpu_info=self._get_cpu_info(),
                memory_info=self._get_memory_info(),
                users=self._get_users(),
                uptime=self._get_uptime(),
                boot_time=self._get_boot_time()
            )
            return self._system_info
            
        except Exception as e:
            logger.error(f"Failed to gather system information: {str(e)}")
            raise
    
    def _get_distribution_info(self) -> Tuple[str, str]:
        """Get Linux distribution information."""
        try:
            with open("/etc/os-release") as f:
                os_info = dict(line.strip().split('=', 1) for line in f if '=' in line)
                return (
                    os_info.get("ID", "unknown").strip('"'),
                    os_info.get("VERSION_ID", "unknown").strip('"')
                )
        except FileNotFoundError:
            return "unknown", "unknown"
    
    def _get_cpu_info(self) -> Dict[str, str]:
        """Get CPU information."""
        cpu_info = {}
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        cpu_info[key.strip()] = value.strip()
        except FileNotFoundError:
            logger.warning("Could not read CPU information from /proc/cpuinfo")
        return cpu_info
    
    def _get_memory_info(self) -> Dict[str, int]:
        """Get memory information in bytes."""
        memory_info = {"total": 0, "free": 0, "available": 0}
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        # Convert kB to bytes
                        value = int(re.search(r'\d+', value.strip()).group()) * 1024
                        if key.strip() == "MemTotal":
                            memory_info["total"] = value
                        elif key.strip() == "MemFree":
                            memory_info["free"] = value
                        elif key.strip() == "MemAvailable":
                            memory_info["available"] = value
        except FileNotFoundError:
            logger.warning("Could not read memory information from /proc/meminfo")
        return memory_info
    
    def _get_users(self) -> List[str]:
        """Get list of system users."""
        users = []
        try:
            with open("/etc/passwd") as f:
                for line in f:
                    if ":" in line:
                        user = line.split(":")[0]
                        if user:
                            users.append(user)
        except FileNotFoundError:
            logger.warning("Could not read user information from /etc/passwd")
        return users
    
    def _get_uptime(self) -> str:
        """Get system uptime as a formatted string."""
        try:
            with open("/proc/uptime") as f:
                uptime_seconds = float(f.readline().split()[0])
                days = int(uptime_seconds // (24 * 3600))
                hours = int((uptime_seconds % (24 * 3600)) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{days}d {hours}h {minutes}m"
        except FileNotFoundError:
            logger.warning("Could not read uptime information from /proc/uptime")
            return "unknown"
    
    def _get_boot_time(self) -> datetime:
        """Get system boot time."""
        try:
            with open("/proc/stat") as f:
                for line in f:
                    if line.startswith("btime"):
                        boot_timestamp = int(line.split()[1])
                        return datetime.fromtimestamp(boot_timestamp)
        except FileNotFoundError:
            logger.warning("Could not read boot time information from /proc/stat")
            return datetime.fromtimestamp(0)  # Unix epoch as fallback

    def is_debian_based(self) -> bool:
        """Check if the system is Debian-based."""
        distro, _ = self._get_distribution_info()
        return distro.lower() in ["debian", "ubuntu"]

    def get_security_info(self) -> Dict[str, bool]:
        """Get security-related system information."""
        return {
            "selinux_enabled": os.path.exists("/etc/selinux/config"),
            "apparmor_enabled": os.path.exists("/etc/apparmor.d"),
            "firewall_enabled": self._check_firewall_status(),
            "ssh_running": self._check_service_status("ssh"),
            "root_login_disabled": self._check_root_login_disabled()
        }
    
    def _check_firewall_status(self) -> bool:
        """Check if firewall is enabled."""
        try:
            result = subprocess.run(
                ["ufw", "status"],
                capture_output=True,
                text=True
            )
            return "active" in result.stdout.lower()
        except FileNotFoundError:
            return False
    
    def _check_service_status(self, service_name: str) -> bool:
        """Check if a service is running."""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _check_root_login_disabled(self) -> bool:
        """Check if root login is disabled in SSH config."""
        try:
            with open("/etc/ssh/sshd_config") as f:
                content = f.read()
                return "PermitRootLogin no" in content
        except FileNotFoundError:
            return False