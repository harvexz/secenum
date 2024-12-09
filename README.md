# SecEnum: Advanced System Software Enumeration & Security Assessment Tool

## Overview
SecEnum is a comprehensive system enumeration and security assessment tool designed for security professionals and system administrators. It provides detailed software inventory management with integrated vulnerability assessment capabilities.

## Features
### Package Enumeration
- Complete package inventory with versions
- Package integrity verification
- Repository security validation
- Package signature verification
- Dependency tracking

### Service Enumeration
- System service detection
- Service status monitoring
- Security context analysis
- Resource usage tracking
- Dependency mapping
- Security configuration analysis

### System Information
- Detailed system information gathering
- Security configuration assessment
- Resource utilization monitoring
- User enumeration
- Security policy verification

## Current Support
- Debian/Ubuntu Linux systems
- APT package management
- Systemd services

## Installation
```bash
# Clone the repository
git clone https://github.com/harvexz/secenum.git
cd secenum

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage
Basic enumeration:
```python
from secenum.core.enumerator import SystemEnumerator

# Create enumerator instance
enumerator = SystemEnumerator()

# Perform complete enumeration
results = enumerator.enumerate_all()

# Enumerate specific components
packages = enumerator.enumerate_packages()
services = enumerator.enumerate_services()

# Perform security analysis
security = enumerator.analyze_security()
```

Command-line usage:
```bash
# Complete system enumeration
python -m secenum scan

# Security analysis only
python -m secenum analyze

# Export results to JSON
python -m secenum scan --output report.json
```

## Security Features
- Package integrity verification
- Service security analysis
- Repository validation
- Security context checking
- Configuration assessment
- Resource monitoring

## Development
The project follows a modular architecture:
```
secenum/
├── core/
│   ├── __init__.py
│   └── enumerator.py      # Main coordination
├── platforms/
│   └── linux/
│       ├── package_managers/
│       │   ├── base.py    # Package manager interface
│       │   └── apt.py     # APT implementation
│       ├── services.py    # Service enumeration
│       └── system_info.py # System information
└── interfaces/
    └── cli.py            # Command-line interface
```

## Contributing
See CONTRIBUTING.md for guidelines on contributing to the project.

## License
This project is licensed under the MIT License - see the LICENSE file for details.