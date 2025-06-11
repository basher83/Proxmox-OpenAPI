---
description: 
globs: 
alwaysApply: true
---
# Proxmox OpenAPI Project Conventions

## Project Overview

This repository generates OpenAPI 3.0.3 specifications for Proxmox APIs (PVE and PBS). Follow these conventions for consistency and maintainability.

## Python Environment & Dependencies

- **Python Version**: Use Python 3.9+ (specified in [.python-version](mdc:.python-version))
- **Dependency Management**: Always use UV instead of pip
  - Install dependencies: `uv sync`
  - Add new dependencies: `uv add package-name`
  - Dev dependencies: `uv add --dev package-name`
- **Project Configuration**: All settings are in [pyproject.toml](mdc:pyproject.toml)

## File Naming Conventions

### API Specifications
- PVE API files: `pve-api.json` and `pve-api.yaml`
- PBS API files: `pbs-api.json` and `pbs-api.yaml`
- Source documentation: `apidoc.js`

### Script Files
- Main generators: `generate_openapi.py`
- Format converters: `convert_to_yaml.py`
- Use snake_case for Python files
- Place scripts in appropriate subdirectories (`scripts/pve/`, `scripts/pbs/`)

## Directory Structure

```
scripts/
├── pve/               # PVE-specific generation scripts
├── pbs/               # PBS-specific generation scripts
└── unified_parser.py  # Shared parsing logic

proxmox-virtual-environment/    # PVE outputs
├── pve-api.json
├── pve-api.yaml
├── apidoc.js
└── README.md

proxmox-backup-server/          # PBS outputs
├── pbs-api.json
├── pbs-api.yaml
├── apidoc.js
└── README.md
```

## Code Quality Standards

### Formatting & Linting
- **Black**: Code formatting (line length: 88)
- **Ruff**: Linting with comprehensive rule set
- **MyPy**: Type checking enabled
- **Target Python**: 3.8+ for compatibility

### Pre-commit Checks
Always run before committing:
```bash
uv run black scripts/
uv run ruff check scripts/
uv run mypy scripts/
```

## Development Workflow

### Adding New Features
1. Use UV for all dependency management
2. Follow existing script structure in `scripts/pve/` or `scripts/pbs/`
3. Maintain compatibility with both JSON and YAML outputs
4. Update relevant README files

### Running Scripts
- Preferred: `uv run python script_name.py`
- Alternative: `cd scripts/pve && uv run python generate_openapi.py`

### Testing Changes
- Validate OpenAPI specs after generation
- Ensure both JSON and YAML formats are updated
- Check file sizes match expected ranges (PVE: ~1.8MB JSON, PBS: ~1.1MB JSON)

## API-Specific Guidelines

### PVE (Proxmox Virtual Environment)
- Port: 8006
- Focus: VM and container management
- Endpoint count: ~385 with ~687 operations

### PBS (Proxmox Backup Server)  
- Port: 8007
- Focus: Backup and data protection
- Endpoint count: ~233 with ~348 operations

## Documentation Standards

- Update component README files when changing APIs
- Maintain specification overview table in main [README.md](mdc:README.md)
- Include authentication examples for both PVE and PBS
- Document any new script functionality

## Version Management

- Follow semantic versioning in [pyproject.toml](mdc:pyproject.toml)
- Update version when releasing new specifications
- Tag releases appropriately in Git

## Unified Parser Migration

- New features should consider the unified parser framework in [scripts/unified_parser.py](mdc:scripts/unified_parser.py)
- Reduce code duplication between PVE and PBS scripts
- Maintain backward compatibility during migration
