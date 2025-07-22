# Proxmox OpenAPI Development Guide

## Project Architecture

This repository generates OpenAPI 3.0.3 specifications for **Proxmox Virtual Environment (PVE)** and **Proxmox Backup Server (PBS)** APIs by parsing their official JavaScript API documentation files.

### Core Components

- **`scripts/unified_parser.py`**: Central parsing engine with file caching, handles both PVE and PBS
- **`scripts/pve/generate_openapi.py`** & **`scripts/pbs/generate_openapi.py`**: API-specific generators
- **`scripts/*/convert_to_yaml.py`**: JSON-to-YAML format converters
- **Output directories**: `proxmox-virtual-environment/` (PVE) and `proxmox-backup-server/` (PBS)

### Data Flow
```
apidoc.js → UnifiedProxmoxParser → generate_openapi.py → {pve,pbs}-api.json → convert_to_yaml.py → {pve,pbs}-api.yaml
```

## Development Environment

**Always use UV, never pip**:
```bash
uv sync --extra all        # Install all dependencies
uv run python script.py   # Run scripts
uv add package-name        # Add dependencies
```

**Python Version**: 3.9+ (check `.python-version`)

## Critical File Naming Conventions

- API specs: `pve-api.{json,yaml}` and `pbs-api.{json,yaml}`
- Source docs: `apidoc.js` (in respective output directories)
- Generators: `generate_openapi.py` (in `scripts/{pve,pbs}/`)

## Key Development Workflows

### Generate API Specifications
```bash
# PVE generation
cd scripts/pve && uv run python generate_openapi.py && uv run python convert_to_yaml.py

# PBS generation  
cd scripts/pbs && uv run python generate_openapi.py && uv run python convert_to_yaml.py
```

### Quality Checks (run before commits)
```bash
uv run ruff check scripts/
uv run ruff format scripts/
uv run mypy scripts/
```

### CI/CD Workflow Debugging
The GitHub Actions workflow may fail due to:
1. **File path issues**: Scripts generate files in `scripts/{pve,pbs}/` but validation expects them in output directories
2. **npm PATH issues**: Use `npx swagger-parser` instead of `swagger-parser` directly
3. **Python version compatibility**: Use Python 3.12 (supported), not 3.13
4. **Missing file moves**: PBS job needs explicit `mv` commands like PVE job

## Parser Architecture Patterns

The `UnifiedProxmoxParser` uses several key patterns:

1. **File Caching**: Caches `apidoc.js` content with mtime checking for performance
2. **Enum Configuration**: `ProxmoxAPI.PVE/PBS` with `APIConfig` dataclasses
3. **JavaScript Parsing**: Extracts `apiSchema` arrays from JS using regex patterns
4. **Standardized Auth**: Common security schemes across PVE/PBS specs

## Expected Output Sizes

Validate generation success by checking file sizes:
- **PVE**: ~1.8MB JSON, ~1.2MB YAML, ~385 endpoints, ~687 operations
- **PBS**: ~1.1MB JSON, ~821KB YAML, ~233 endpoints, ~348 operations

## Project-Specific Conventions

- **Error Handling**: Always include port numbers (PVE: 8006, PBS: 8007) in server configs
- **Tag Mapping**: Use `tag_mapping` in `APIConfig` for consistent endpoint grouping
- **Path Discovery**: Scripts auto-discover `apidoc.js` files using multiple search paths
- **Atomic Changes**: Separate commits for PVE vs PBS changes, dependency updates, and features

## Integration Points

- **Input**: JavaScript `apidoc.js` files from Proxmox documentation
- **Processing**: `unified_parser.py` with API-specific configurations
- **Output**: Dual-format (JSON/YAML) OpenAPI 3.0.3 specifications
- **CI/CD**: GitHub Actions for automated spec updates (see `.github/workflows/`)

When modifying parsers, ensure both PVE and PBS outputs remain valid and maintain consistent authentication patterns across specifications.
