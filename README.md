# Proxmox OpenAPI Specifications

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0.3-green.svg)](https://swagger.io/specification/)
![GitHub commit activity](https://img.shields.io/github/commit-activity/w/basher83/Proxmox-OpenAPI)
![GitHub last commit](https://img.shields.io/github/last-commit/basher83/Proxmox-OpenAPI)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fbasher83%2FProxmox-OpenAPI%2Fmain%2Fpyproject.toml)
[![Update Proxmox API Specifications](https://github.com/basher83/Proxmox-OpenAPI/actions/workflows/update-api-specs.yml/badge.svg)](https://github.com/basher83/Proxmox-OpenAPI/actions/workflows/update-api-specs.yml)

Complete OpenAPI 3.0.3 specifications for Proxmox APIs, automatically generated from official documentation.

## 📋 Overview

This repository provides comprehensive OpenAPI specifications for:

- **[Proxmox Virtual Environment (PVE)](./proxmox-virtual-environment/)** - VM and container management
- **[Proxmox Backup Server (PBS)](./proxmox-backup-server/)** - Backup and data protection

Both specifications are available in JSON and YAML formats with proper naming conventions:

- `pve-api.json` / `pve-api.yaml`
- `pbs-api.json` / `pbs-api.yaml`

## 🚀 Quick Start

### Download Specifications

```bash
# Clone the repository
git clone https://github.com/basher83/Proxmox-OpenAPI.git
cd Proxmox-OpenAPI

# Use PVE specification
curl -o pve-spec.json https://raw.githubusercontent.com/basher83/Proxmox-OpenAPI/main/proxmox-virtual-environment/pve-api.json

# Use PBS specification
curl -o pbs-spec.json https://raw.githubusercontent.com/basher83/Proxmox-OpenAPI/main/proxmox-backup-server/pbs-api.json
```

### Generate Client Code

```bash
# Generate Python client for PVE
openapi-generator-cli generate \
  -i proxmox-virtual-environment/pve-api.yaml \
  -g python \
  -o ./pve-client

# Generate Python client for PBS
openapi-generator-cli generate \
  -i proxmox-backup-server/pbs-api.yaml \
  -g python \
  -o ./pbs-client
```

## 📊 Specifications Overview

| API     | Endpoints | Operations | Size (JSON) | Size (YAML) | Port |
| ------- | --------- | ---------- | ----------- | ----------- | ---- |
| **PVE** | 385       | 687        | 1.8MB       | 1.2MB       | 8006 |
| **PBS** | 233       | 348        | 1.1MB       | 821KB       | 8007 |

## 📁 Repository Structure

```
Proxmox-OpenAPI/
├── proxmox-virtual-environment/    # PVE API specifications
│   ├── pve-api.json               # PVE OpenAPI JSON spec
│   ├── pve-api.yaml               # PVE OpenAPI YAML spec
│   ├── apidoc.js                  # Source API documentation
│   └── README.md                  # PVE-specific documentation
├── proxmox-backup-server/         # PBS API specifications
│   ├── pbs-api.json               # PBS OpenAPI JSON spec
│   ├── pbs-api.yaml               # PBS OpenAPI YAML spec
│   ├── apidoc.js                  # Source API documentation
│   └── README.md                  # PBS-specific documentation
├── scripts/                       # Generation scripts
│   ├── pve/                       # PVE OpenAPI generation scripts
│   │   ├── generate_openapi.py    # Main PVE OpenAPI generator
│   │   └── convert_to_yaml.py     # JSON to YAML converter
│   └── pbs/                       # PBS OpenAPI generation scripts
│       ├── generate_openapi.py    # Main PBS OpenAPI generator
│       └── convert_to_yaml.py     # JSON to YAML converter
├── .github/workflows/             # CI/CD automation (planned)
├── LICENSE                        # AGPL-3.0 license
└── README.md                      # This file
```

## 🔧 Development

### Prerequisites

- Python 3.8+
- [UV](https://github.com/astral-sh/uv) (recommended) or pip
- Node.js (optional, for enhanced JavaScript parsing)

### Setup with UV (Recommended)

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup the project
git clone https://github.com/basher83/Proxmox-OpenAPI.git
cd Proxmox-OpenAPI

# Install dependencies
uv sync

# Install with development dependencies
uv sync --extra dev

# Install all optional dependencies
uv sync --extra all
```

### Regenerate Specifications

#### Using UV (Recommended)

```bash
# PVE API
cd scripts/pve
uv run python generate_openapi.py
uv run python convert_to_yaml.py

# PBS API
cd scripts/pbs
uv run python generate_openapi.py
uv run python convert_to_yaml.py

# Or use the unified parser (future)
uv run proxmox-openapi pve proxmox-virtual-environment/apidoc.js proxmox-virtual-environment/
uv run proxmox-openapi pbs proxmox-backup-server/apidoc.js proxmox-backup-server/
```

#### Using Python directly

```bash
# PVE API
cd scripts/pve
python3 generate_openapi.py
python3 convert_to_yaml.py

# PBS API
cd scripts/pbs
python3 generate_openapi.py
python3 convert_to_yaml.py
```

### Unified Parser (Planned)

A unified parsing framework is being developed to reduce code duplication and standardize the generation process across both APIs.

## 📖 API Documentation

Each API has detailed documentation in its respective directory:

- **[PVE API Documentation](./proxmox-virtual-environment/README.md)** - Virtual Environment management
- **[PBS API Documentation](./proxmox-backup-server/README.md)** - Backup Server operations

## 🔐 Authentication

Both APIs support multiple authentication methods:

### PVE Authentication

- **API Token**: `PVEAPIToken=USER@REALM!TOKENID=UUID`
- **Session Cookie**: From `/access/ticket` endpoint
- **CSRF Token**: Required for state-changing operations

### PBS Authentication

- **API Token**: Header-based token authentication
- **Session Cookie**: From `/access/ticket` endpoint
- **CSRF Protection**: Required for state-changing operations

## 🚦 Usage Examples

### PVE - List VMs

```bash
curl -k -H "Authorization: PVEAPIToken=USER@REALM!TOKENID=UUID" \
     https://your-pve-server:8006/api2/json/nodes/nodename/qemu
```

### PBS - List Datastores

```bash
curl -k -H "Authorization: PBSAPIToken=USER@REALM!TOKENID=UUID" \
     https://your-pbs-server:8007/api2/json/admin/datastore
```

## 🛣️ Roadmap

- [ ] **Unified Parser Framework** - Combine PVE and PBS parsing logic
- [ ] **CI/CD Pipeline** - Automated spec generation and updates
- [ ] **Direct API Fetching** - Parse from live API viewers instead of downloaded files
- [ ] **Enhanced Validation** - Comprehensive OpenAPI spec validation
- [ ] **Client Libraries** - Pre-generated clients in multiple languages
- [ ] **Docker Images** - Containerized parsing and generation tools

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/improvement`
3. **Make your changes** ensuring compatibility with official Proxmox APIs
4. **Validate specifications** using OpenAPI tools
5. **Update documentation** as needed
6. **Submit a pull request**

### Contribution Guidelines

- **Follow the [Git Commit Workflow](./docs/GIT_COMMIT_WORKFLOW.md)** - Comprehensive commit standards and quality gates
- Maintain compatibility with official Proxmox API documentation
- Follow OpenAPI 3.0.3 specification standards
- Update both JSON and YAML formats
- Include appropriate tests and validation
- Update relevant README files

#### Quick Validation

Use the automated validation script before committing:

```bash
# Run all quality checks
./scripts/validate-commit.sh

# Run checks and commit with template
./scripts/validate-commit.sh --commit
```

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

The specifications are generated from official Proxmox documentation and follow the same AGPL-3.0 licensing terms as the source material.

## 🔗 Related Resources

- **[Proxmox VE API Viewer](https://pve.proxmox.com/pve-docs/api-viewer/index.html)** - Official PVE API documentation
- **[Proxmox PBS API Viewer](https://pbs.proxmox.com/docs/api-viewer/index.html)** - Official PBS API documentation
- **[OpenAPI Specification](https://swagger.io/specification/)** - OpenAPI 3.0.3 standard
- **[OpenAPI Generator](https://openapi-generator.tech/)** - Code generation tools
- **[Proxmox Website](https://www.proxmox.com/)** - Official Proxmox resources

## 📧 Support

For issues related to:

- **OpenAPI specifications**: Open an issue in this repository
- **Proxmox APIs**: Contact [Proxmox Support](https://www.proxmox.com/en/support)
- **OpenAPI standard**: Refer to [OpenAPI documentation](https://swagger.io/docs/)

---

**Generated**: 2025-01-28  
**Status**: ✅ Production Ready  
**Maintainer**: [basher83](https://github.com/basher83)
