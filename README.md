# SecEnum: Advanced System Software Enumeration & Security Assessment Tool

## Overview
SecEnum is a comprehensive system enumeration and security assessment tool designed for security professionals and system administrators. It provides detailed software inventory management with integrated vulnerability assessment capabilities.

## Architecture
The tool is structured into several key components:

### Core Components (`/secenum/core/`)
- `enumerator.py`: Main enumeration engine
- Base interfaces and common utilities
- Exception handling and logging

### Platform-Specific Components (`/secenum/platforms/`)
#### Linux (`/platforms/linux/`)
- Package Manager Support
  - Current focus on Debian/Ubuntu systems (APT)
  - Modular design for easy extension to other distributions
- System Service Enumeration
- Security Policy Verification

## Key Features
- Package Enumeration
  - Installed software detection
  - Version tracking
  - Package integrity verification
  - Repository validation
  - Security signature verification
- Service Analysis
  - Running service detection
  - Security configuration assessment
  - Dependency mapping
- Security Features
  - Package hash verification
  - Digital signature validation
  - CVE database integration
  - Security policy verification
  - Audit logging
  - Encrypted storage

## Current Support
- Operating Systems:
  - Linux (Debian/Ubuntu)
  - More distributions planned
- Package Managers:
  - APT (Advanced Package Tool)
  - More package managers planned

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
```bash
# Basic software enumeration
python -m secenum scan

# Full security assessment
python -m secenum assess --full

# Export results to JSON
python -m secenum scan --output report.json
```

## Development
### Project Structure
```
secenum/
├── core/
│   ├── __init__.py          # Core exceptions and utilities
│   └── enumerator.py        # Main enumeration interface
├── platforms/
│   └── linux/
│       ├── package_managers/
│       │   ├── __init__.py
│       │   ├── base.py      # Abstract package manager interface
│       │   └── apt.py       # Debian/Ubuntu implementation
│       └── services.py      # Service enumeration (planned)
├── interfaces/
│   ├── __init__.py
│   └── cli.py              # Command-line interface
└── utils/                  # Utility functions (planned)
```

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## Security Considerations
- All package verifications use cryptographic validation
- Repository sources are checked for secure connections
- Service configurations are validated against security best practices
- Root privileges are required for complete enumeration

## License
This project is licensed under the MIT License - see the LICENSE file for details.