---
description: Project development tasks, enviroment setup, code generation, quality checks, validation
globs: 
alwaysApply: false
---
# Development Shortcuts & Commands

## Quick Commands Reference

### Environment Setup
```bash
# Initial setup
uv sync --extra all

# Development dependencies only
uv sync --extra dev

# Add new dependency
uv add package-name
uv add --dev package-name  # for dev dependencies
```

### Code Generation Workflow
```bash
# Generate PVE API spec
cd scripts/pve
uv run python generate_openapi.py
uv run python convert_to_yaml.py

# Generate PBS API spec  
cd scripts/pbs
uv run python generate_openapi.py
uv run python convert_to_yaml.py

# Future: Unified approach
uv run proxmox-openapi pve proxmox-virtual-environment/apidoc.js proxmox-virtual-environment/
uv run proxmox-openapi pbs proxmox-backup-server/apidoc.js proxmox-backup-server/
```

### Code Quality Checks
```bash
# Run all checks
uv run black scripts/
uv run ruff check scripts/
uv run mypy scripts/

# Auto-fix what's possible
uv run black scripts/
uv run ruff check --fix scripts/
```

### Validation
```bash
# Validate OpenAPI specs (if validator is installed)
uv run python -m openapi_spec_validator proxmox-virtual-environment/pve-api.json
uv run python -m openapi_spec_validator proxmox-backup-server/pbs-api.json
```

## File Templates

### New Script Template
When creating new scripts in `scripts/pve/` or `scripts/pbs/`:

```python
#!/usr/bin/env python3
"""
Brief description of what this script does.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main() -> None:
    """Main execution function."""
    logger.info("Starting script execution")
    # Implementation here
    logger.info("Script execution completed")

if __name__ == "__main__":
    main()
```

## Common File Locations

- PVE output: [proxmox-virtual-environment/pve-api.json](mdc:proxmox-virtual-environment/pve-api.json)
- PBS output: [proxmox-backup-server/pbs-api.json](mdc:proxmox-backup-server/pbs-api.json)
- Project config: [pyproject.toml](mdc:pyproject.toml)
- Main README: [README.md](mdc:README.md)
- Unified parser: [scripts/unified_parser.py](mdc:scripts/unified_parser.py)

## Debugging Tips

### Script Issues
- Check Python version: `python --version` (should be 3.9+)
- Verify UV installation: `uv --version`
- Check dependencies: `uv pip list`

### Output Validation
- JSON file sizes: PVE (~1.8MB), PBS (~1.1MB)
- YAML file sizes: PVE (~1.2MB), PBS (~821KB)
- Endpoint counts: PVE (385 endpoints, 687 ops), PBS (233 endpoints, 348 ops)

### Git Workflow
```bash
# Before committing
uv run black scripts/
uv run ruff check scripts/
uv run mypy scripts/

# Create feature branch
git checkout -b feature/description

# Standard commit
git add .
git commit -m "feat: description of changes"
```
