# Copilot Coding Agent Instructions

## Project Overview

This repository generates **OpenAPI 3.0.3 specifications** for Proxmox APIs by parsing JavaScript documentation files. It supports both **Proxmox Virtual Environment (PVE)** and **Proxmox Backup Server (PBS)** APIs.

**Repository Type**: Python-based API specification generator  
**Languages**: Python 3.9+, JavaScript (parsing), YAML/JSON (output)  
**Size**: ~10MB with large API specification files  
**Key Output**: OpenAPI specs for 398+ PVE endpoints (605 operations) and 233+ PBS endpoints (348 operations)

## Quick Start

**⚠️ ALWAYS use UV, never pip for this project**

### Essential Setup (Required First)
```bash
# 1. Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Add UV to PATH (CRITICAL - needed for all commands)
export PATH="$HOME/.local/bin:$PATH"

# 3. Install dependencies (REQUIRED before any work)
uv sync --extra all

# 4. Verify setup works
uv run python scripts/validate_openapi.py
```

### Verify Your Setup
After initial setup, confirm everything works:
```bash
# Should show: "All OpenAPI specifications are valid!"
uv run python scripts/validate_openapi.py

# Should pass without major errors
./scripts/validate-commit.sh

# Should show current file sizes (~3.0MB PVE JSON, ~1.7MB PBS JSON)
ls -lh proxmox-*/pve-api.json proxmox-*/pbs-api.json
```

## Critical Build & Validation Commands

### Essential Setup
```bash
# Install UV first (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add UV to PATH (REQUIRED for all UV commands)
export PATH="$HOME/.local/bin:$PATH"

# Install dependencies (REQUIRED before any work)
uv sync --extra all

# Run any Python script (ALWAYS use this prefix)
uv run python script_name.py
```

### Generate API Specifications
```bash
# Generate PVE API specifications (takes ~5 seconds)
export PATH="$HOME/.local/bin:$PATH"  # Ensure UV is in PATH
cd scripts/pve && uv run python generate_openapi.py && uv run python convert_to_yaml.py

# Generate PBS API specifications (takes ~3 seconds)  
cd scripts/pbs && uv run python generate_openapi.py && uv run python convert_to_yaml.py
```

### Validation (MUST run before commits)
```bash
# Ensure UV is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Validate OpenAPI specifications
uv run python scripts/validate_openapi.py

# Code quality checks
uv run ruff format scripts/     # Format code
uv run ruff check scripts/      # Lint code  
uv run mypy scripts/            # Type checking

# Complete validation (recommended)
./scripts/validate-commit.sh
```

### Common Build Issues & Solutions

1. **Import Errors**: Always use `uv run python` not direct `python`
2. **Missing Dependencies**: Run `uv sync --extra all` first
3. **UV Command Not Found**: Add UV to PATH with `export PATH="$HOME/.local/bin:$PATH"`
4. **CI/CD Failures**: Scripts generate files in `scripts/{pve,pbs}/` but CI expects them in output directories - ensure file move commands
5. **File Size Validation**: PVE should be ~3.0MB JSON/2.1MB YAML, PBS ~1.7MB JSON/1.3MB YAML
6. **Network Issues**: If UV installation fails, use package manager: `pip install uv` or `brew install uv`

### Troubleshooting

**UV not found after installation**:
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc  # or restart terminal
```

**Permission errors**:
```bash
# Ensure UV installation directory is writable
chmod +x ~/.local/bin/uv
```

## Project Architecture & Key Locations

### Data Flow
```
apidoc.js → unified_parser.py → generate_openapi.py → {pve,pbs}-api.json → convert_to_yaml.py → {pve,pbs}-api.yaml
```

### Critical File Locations
- **Main Outputs**: `proxmox-virtual-environment/pve-api.{json,yaml}`, `proxmox-backup-server/pbs-api.{json,yaml}`
- **Build Artifacts**: `artifacts/pve-specs/` and `artifacts/pbs-specs/` (CI/CD output directories)
- **Core Parser**: `scripts/unified_parser.py` (central engine with file caching)
- **Generators**: `scripts/{pve,pbs}/generate_openapi.py` (API-specific wrappers)
- **Converters**: `scripts/{pve,pbs}/convert_to_yaml.py` (JSON to YAML conversion)
- **Validator**: `scripts/validate_openapi.py` (OpenAPI 3.0.3 validation)
- **Source Docs**: `{proxmox-virtual-environment,proxmox-backup-server}/apidoc.js`

### Configuration Files
- **Dependencies**: `pyproject.toml` (defines all dependencies and project config)
- **Linting**: Ruff configuration in `pyproject.toml` (target Python 3.9, line length 88)
- **Type Checking**: MyPy configuration in `pyproject.toml`
- **Git**: `.gitmessage` template (conventional commits required)
- **CI/CD**: `.github/workflows/update-api-specs.yml` (automated updates)

### Project Layout
```
Proxmox-OpenAPI/
├── scripts/
│   ├── unified_parser.py           # Core parsing engine (file caching, orjson optimization)
│   ├── validate_openapi.py         # Validation script  
│   ├── validate-commit.sh          # Pre-commit validation
│   ├── pve/                        # PVE-specific generators
│   └── pbs/                        # PBS-specific generators  
├── proxmox-virtual-environment/    # PVE API outputs + source
├── proxmox-backup-server/          # PBS API outputs + source
├── artifacts/                      # CI/CD build outputs
│   ├── pve-specs/                  # Generated PVE specifications
│   └── pbs-specs/                  # Generated PBS specifications
├── docs/                           # Documentation  
│   └── GIT_COMMIT_WORKFLOW.md      # Detailed commit requirements
└── .github/workflows/              # CI/CD automation
```

## Git Workflow Requirements

**🚨 MANDATORY: Follow conventional commits with atomic changes**

### Commit Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert  
**Scopes**: api, pve, pbs, spec, parser, schema, validation, deps

### Pre-commit Validation (ALWAYS run)
```bash
# Ensure UV is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Complete validation
./scripts/validate-commit.sh

# Or individual checks
uv run ruff check . && uv run ruff format . && uv run mypy scripts/
uv run python scripts/validate_openapi.py
```

### Security Requirements
- **Dependency changes**: MUST run security validation (`safety check`)
- **Document security fixes**: Include CVE information in commit messages
- **Breaking changes**: Must start footer with `BREAKING CHANGE:`

## Common Development Patterns

### Adding New API Support
1. Create APIConfig in `scripts/unified_parser.py`
2. Add API-specific generator script following PVE/PBS pattern
3. Update validation script to include new specs
4. Add CI/CD workflow steps

### Modifying Parser Logic
1. Update `scripts/unified_parser.py` (handles both APIs)
2. Test with both PVE and PBS: `uv run python scripts/validate_openapi.py`
3. Regenerate specs to verify changes
4. Check file sizes match expected ranges

### Performance Optimization
- Parser uses file caching with mtime checking
- orjson library for JSON performance (optional dependency)
- Target parse time < 5 seconds for full API

## Validation Checklist

Before any commit, ensure:
- [ ] `export PATH="$HOME/.local/bin:$PATH"` is set (UV requirement)
- [ ] `uv run ruff check .` passes (linting)
- [ ] `uv run ruff format .` applied (formatting)  
- [ ] `uv run mypy scripts/` passes (type checking - may show import warnings)
- [ ] `uv run python scripts/validate_openapi.py` passes (OpenAPI validation)
- [ ] Generated file sizes match expected ranges
- [ ] Conventional commit format used
- [ ] Security validation for dependency changes

**Note**: MyPy may show import warnings for relative imports but should not have error-level issues.

## Expected Outputs & Validation

**PVE Specifications**:
- JSON: ~3.0MB, ~398 endpoints, ~605 operations
- YAML: ~2.1MB (same content, different format)

**PBS Specifications**:  
- JSON: ~1.7MB, ~233 endpoints, ~348 operations
- YAML: ~1.3MB (same content, different format)

**Validation Success**: All specs must pass OpenAPI 3.0.3 validation with no errors.

## Dependencies & Environment

**Python Version**: 3.9+ (check `pyproject.toml` for current requirements)  
**Package Manager**: UV only (never use pip)  
**Key Dependencies**: openapi-spec-validator, PyYAML, ruff, mypy  
**Optional Performance**: orjson (for faster JSON processing)

**Trust these instructions** - only search/explore if information is incomplete or incorrect. This covers all essential patterns for efficient development.