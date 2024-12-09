"""Linux system service enumeration and analysis module."""

import os
import subprocess
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ServiceInfo:
    """Data class for service information."""
    name: str
    status: str  # active, inactive, failed
    enabled: bool
    loaded: bool
    unit_file: str
    description: Optional[str] = None
    dependencies: List[str] = None
    start_time: Optional[datetime] = None
    restart_count: int = 0
    process_id: Optional[int] = None
    memory_usage: Optional[int] = None
    user: Optional[str] = None
    group: Optional[str] = None
    security_context: Optional[str] = None

class ServiceEnumerator:
    """Handles system service enumeration and analysis."""
    
    SYSTEMD_PATH = "/etc/systemd/system"
    SYSTEMD_USER_PATH = "/usr/lib/systemd/user"
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._verify_systemd()
    
    def _verify_systemd(self):
        """Verify systemd is the init system."""
        if not os.path.exists("/run/systemd/system"):
            raise RuntimeError("Systemd is not the active init system")
    
    def get_all_services(self) -> Dict[str, ServiceInfo]:
        """Get information about all system services."""
        services = {}
        
        # Get list of all units
        stdout, stderr, retcode = self._execute_command(
            ["systemctl", "list-units", "--type=service", "--all", "--plain", "--no-legend"]
        )
        
        if retcode != 0:
            self.logger.error(f"Failed to list services: {stderr}")
            return services
        
        for line in stdout.splitlines():
            fields = line.split()
            if len(fields) >= 4:
                service_name = fields[0]
                if service_name.endswith('.service'):
                    service_name = service_name[:-8]  # Remove .service suffix
                    services[service_name] = self._get_service_info(service_name)
        
        return services
    
    def _get_service_info(self, service_name: str) -> ServiceInfo:
        """Get detailed information about a specific service."""
        # Get service properties
        props = self._get_service_properties(service_name)
        
        # Get dependencies
        deps = self._get_service_dependencies(service_name)
        
        # Get security context if available
        security_context = self._get_security_context(service_name)
        
        return ServiceInfo(
            name=service_name,
            status=props.get("ActiveState", "unknown"),
            enabled=props.get("UnitFileState", "") == "enabled",
            loaded=props.get("LoadState", "") == "loaded",
            unit_file=props.get("FragmentPath", ""),
            description=props.get("Description", ""),
            dependencies=deps,
            start_time=self._parse_timestamp(props.get("ActiveEnterTimestamp")),
            restart_count=int(props.get("NRestarts", 0)),
            process_id=int(props.get("MainPID", 0)) or None,
            memory_usage=self._get_memory_usage(props.get("MainPID")),
            user=props.get("User", ""),
            group=props.get("Group", ""),
            security_context=security_context
        )
    
    def _get_service_properties(self, service_name: str) -> Dict[str, str]:
        """Get all properties of a service."""
        properties = {}
        stdout, stderr, retcode = self._execute_command(
            ["systemctl", "show", f"{service_name}.service"]
        )
        
        if retcode == 0:
            for line in stdout.splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    properties[key] = value
        
        return properties
    
    def _get_service_dependencies(self, service_name: str) -> List[str]:
        """Get list of service dependencies."""
        stdout, stderr, retcode = self._execute_command(
            ["systemctl", "list-dependencies", f"{service_name}.service", "--plain", "--no-legend"]
        )
        
        if retcode == 0:
            return [line.split()[0].replace(".service", "") 
                   for line in stdout.splitlines() 
                   if line.strip()]
        return []
    
    def _get_security_context(self, service_name: str) -> Optional[str]:
        """Get SELinux/AppArmor security context for service."""
        if os.path.exists("/sys/kernel/security/apparmor"):
            # Check AppArmor profile
            stdout, stderr, retcode = self._execute_command(
                ["aa-status"]
            )
            if retcode == 0:
                for line in stdout.splitlines():
                    if service_name in line:
                        return f"AppArmor: {line.strip()}"
        
        elif os.path.exists("/etc/selinux"):
            # Check SELinux context
            process_id = self._get_service_properties(service_name).get("MainPID")
            if process_id and process_id != "0":
                stdout, stderr, retcode = self._execute_command(
                    ["ps", "-Z", process_id]
                )
                if retcode == 0 and len(stdout.splitlines()) > 1:
                    return f"SELinux: {stdout.splitlines()[1].split()[0]}"
        
        return None
    
    def _get_memory_usage(self, pid: Optional[str]) -> Optional[int]:
        """Get memory usage of service in bytes."""
        if not pid or pid == "0":
            return None
            
        try:
            with open(f"/proc/{pid}/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        # Convert kB to bytes
                        return int(line.split()[1]) * 1024
        except (FileNotFoundError, ValueError):
            pass
        return None
    
    def _parse_timestamp(self, timestamp: Optional[str]) -> Optional[datetime]:
        """Parse systemd timestamp into datetime object."""
        if not timestamp or timestamp == "0":
            return None
        try:
            # Convert microseconds to seconds
            return datetime.fromtimestamp(int(timestamp) / 1000000)
        except ValueError:
            return None
    
    def _execute_command(self, command: List[str]) -> tuple:
        """Safely execute a command and return its output."""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={"LC_ALL": "C"}
            )
            
            stdout, stderr = process.communicate(timeout=30)
            return stdout, stderr, process.returncode
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError(f"Command timed out: {' '.join(command)}")
        
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Command failed: {' '.join(command)}. Error: {str(e)}")
    
    def analyze_service_security(self, service_name: str) -> Dict[str, bool]:
        """Analyze security configuration of a service."""
        service_info = self._get_service_info(service_name)
        unit_file = service_info.unit_file
        
        security_checks = {
            "runs_as_root": service_info.user == "root",
            "has_security_policy": bool(service_info.security_context),
            "protected_mode": False,
            "private_tmp": False,
            "no_new_privileges": False,
            "restricted_namespaces": False
        }
        
        if os.path.exists(unit_file):
            with open(unit_file) as f:
                content = f.read()
                security_checks.update({
                    "protected_mode": "ProtectSystem=strict" in content,
                    "private_tmp": "PrivateTmp=yes" in content,
                    "no_new_privileges": "NoNewPrivileges=yes" in content,
                    "restricted_namespaces": "RestrictNamespaces=yes" in content
                })
        
        return security_checks