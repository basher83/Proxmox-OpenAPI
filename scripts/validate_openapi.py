#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "PyYAML",
#     "openapi-spec-validator",
# ]
# ///

"""
OpenAPI Specification Validator

Validates OpenAPI JSON and YAML files using the openapi-spec-validator library.
Supports validation of both PVE and PBS API specifications with detailed error reporting.
"""

import json
import sys
from pathlib import Path

import yaml
from openapi_spec_validator import validate_spec
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError


def validate_openapi_file(file_path: Path) -> tuple[bool, str]:
    """
    Validate a single OpenAPI specification file.

    Args:
        file_path: Path to the OpenAPI specification file

    Returns:
        Tuple of (success, error_message)
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    try:
        # Load the specification
        with open(file_path, encoding="utf-8") as f:
            if file_path.suffix.lower() in [".yaml", ".yml"]:
                spec = yaml.safe_load(f)
            elif file_path.suffix.lower() == ".json":
                spec = json.load(f)
            else:
                return False, f"Unsupported file format: {file_path.suffix}"

        # Validate the specification
        validate_spec(spec)
        return True, ""

    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except json.JSONDecodeError as e:
        return False, f"JSON parsing error: {e}"
    except OpenAPIValidationError as e:
        return False, f"OpenAPI validation error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def find_api_specs() -> list[Path]:
    """Find all OpenAPI specification files in the project."""
    project_root = Path(__file__).parent.parent
    spec_files: list[Path] = []

    # Look for API specs in common locations
    search_patterns = [
        "proxmox-virtual-environment/pve-api.*",
        "proxmox-backup-server/pbs-api.*",
        "scripts/pve/pve-api.*",
        "scripts/pbs/pbs-api.*",
        "pve-api.*",
        "pbs-api.*",
    ]

    for pattern in search_patterns:
        spec_files.extend(project_root.glob(pattern))

    # Filter to only JSON and YAML files
    return [f for f in spec_files if f.suffix.lower() in [".json", ".yaml", ".yml"]]


def main() -> int:
    """Main validation function."""
    if len(sys.argv) > 1:
        # Validate specific files provided as arguments
        files_to_validate = [Path(arg) for arg in sys.argv[1:]]
    else:
        # Auto-discover API specification files
        files_to_validate = find_api_specs()
        if not files_to_validate:
            print("❌ No OpenAPI specification files found.")
            print(
                "   Expected files: pve-api.json, pve-api.yaml, pbs-api.json, pbs-api.yaml"
            )
            return 1

    print(f"🔍 Validating {len(files_to_validate)} OpenAPI specification file(s)...\n")

    success_count = 0
    total_count = len(files_to_validate)

    for file_path in files_to_validate:
        print(f"📋 Validating: {file_path}")

        success, error_msg = validate_openapi_file(file_path)

        if success:
            print(f"✅ {file_path.name} - Valid OpenAPI 3.0.3 specification")
            success_count += 1
        else:
            print(f"❌ {file_path.name} - Validation failed:")
            print(f"   {error_msg}")

        print()  # Add blank line for readability

    # Summary
    print("=" * 60)
    print("📊 Validation Summary:")
    print(f"   ✅ Passed: {success_count}")
    print(f"   ❌ Failed: {total_count - success_count}")
    print(f"   📋 Total:  {total_count}")

    if success_count == total_count:
        print("🎉 All OpenAPI specifications are valid!")
        return 0
    else:
        print("⚠️  Some OpenAPI specifications failed validation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
