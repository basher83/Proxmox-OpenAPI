# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository generates OpenAPI 3.0.3 specifications for Proxmox APIs by parsing their JavaScript documentation files. It supports both Proxmox Virtual Environment (PVE) and Proxmox Backup Server (PBS).

## Essential Commands

### Development Setup
```bash
# Install all dependencies (ALWAYS use UV, never pip)
uv sync --extra all

# Run any Python script
uv run python script_name.py
```

### Generate API Specifications
```bash
# Generate PVE API specifications
cd scripts/pve && uv run python generate_openapi.py && uv run python convert_to_yaml.py

# Generate PBS API specifications  
cd scripts/pbs && uv run python generate_openapi.py && uv run python convert_to_yaml.py
```

### Code Quality Checks (MUST run before commits)
```bash
# Format code
uv run ruff format scripts/

# Check linting
uv run ruff check scripts/

# Type checking
uv run mypy scripts/

# Validate OpenAPI specs
uv run python scripts/validate_openapi.py

# Run ALL validation (recommended)
./scripts/validate-commit.sh
```

### Git Commit Validation
```bash
# Validate commit readiness
./scripts/validate-commit.sh

# Commit with automatic validation
./scripts/validate-commit.sh --commit
```

## High-Level Architecture

### Data Flow
```
apidoc.js → Parser → generate_openapi.py → {pve,pbs}-api.json → convert_to_yaml.py → {pve,pbs}-api.yaml
```

### Core Components

1. **Unified Parser** (`scripts/unified_parser.py`):
   - Central parsing engine with file caching for performance
   - Handles both PVE and PBS with API-specific configurations
   - Extracts API schemas from JavaScript using regex patterns
   - Standardizes authentication across specifications

2. **API Generators** (`scripts/{pve,pbs}/generate_openapi.py`):
   - API-specific wrappers around the unified parser
   - Generate JSON specifications in respective output directories
   - Handle file path discovery and output placement

3. **Format Converters** (`scripts/{pve,pbs}/convert_to_yaml.py`):
   - Convert JSON specifications to YAML format
   - Maintain consistent file naming: `{pve,pbs}-api.{json,yaml}`

### Key Design Patterns

1. **File Caching**: The unified parser caches `apidoc.js` content with mtime checking to avoid repeated file reads during development.

2. **Configuration-Driven**: Each API (PVE/PBS) has an `APIConfig` dataclass defining:
   - Port numbers (PVE: 8006, PBS: 8007)
   - Authentication schemes
   - Tag mappings for endpoint grouping
   - Server paths and metadata

3. **Path Discovery**: Scripts automatically search multiple locations for `apidoc.js` files, supporting flexible directory structures.

4. **Atomic Commits**: The project enforces strict commit conventions with separate commits for different change types (features, fixes, dependencies).

## Critical File Locations

- **PVE Output**: `proxmox-virtual-environment/pve-api.{json,yaml}`
- **PBS Output**: `proxmox-backup-server/pbs-api.{json,yaml}`
- **Source Docs**: `{proxmox-virtual-environment,proxmox-backup-server}/apidoc.js`
- **Parsers**: `scripts/unified_parser.py`, `scripts/{pve,pbs}/generate_openapi.py`

## Expected Outputs

Validate generation success by checking:
- **PVE**: ~1.8MB JSON, ~1.2MB YAML, ~385 endpoints, ~687 operations
- **PBS**: ~1.1MB JSON, ~821KB YAML, ~233 endpoints, ~348 operations

## Common Issues and Solutions

1. **CI/CD Failures**: 
   - Scripts generate files in `scripts/{pve,pbs}/` but CI expects them in output directories
   - Solution: Ensure file move commands in workflows

2. **Validation Errors**:
   - Run `uv run python scripts/validate_openapi.py` to check specifications
   - Common issues: missing required fields, invalid schema references

3. **Import Errors**:
   - Always use `uv run` to execute scripts, not direct Python
   - UV manages virtual environments automatically

## Development Workflow

1. **Before Making Changes**:
   - Understand existing patterns in similar files
   - Check file naming conventions (especially for API specs)
   - Review the Git commit workflow in `docs/GIT_COMMIT_WORKFLOW.md`

2. **Making Changes**:
   - Use the unified parser for new features when possible
   - Maintain compatibility with both JSON and YAML outputs
   - Follow existing authentication patterns

3. **Before Committing**:
   - Run `./scripts/validate-commit.sh` for all quality checks
   - Use conventional commit format: `type(scope): description`
   - Ensure atomic commits (one logical change per commit)

## Project-Specific Conventions

- **Dependency Management**: ONLY use UV (`uv add`, `uv sync`), never pip
- **Python Version**: 3.9+ (check `.python-version`)
- **Code Style**: Ruff for formatting/linting (configured in `pyproject.toml`)
- **Commit Style**: Conventional commits with project-specific scopes (api, pve, pbs, parser, schema, deps)