#!/usr/bin/env python3
"""
Convert PBS OpenAPI JSON specification to YAML format.
"""

import json
import os
import sys

import yaml


def convert_json_to_yaml(input_file, output_file):
    """Convert JSON file to YAML format."""
    try:
        # Read JSON file
        with open(input_file, encoding="utf-8") as f:
            data = json.load(f)

        # Write YAML file
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
            )

        print(f"Successfully converted {input_file} to {output_file}")

    except Exception as e:
        print(f"Error converting file: {e}")
        return False

    return True


def main():
    """Main function."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(os.path.dirname(script_dir))

    # Define input and output paths
    json_file = os.path.join(workspace_root, "proxmox-backup-server", "pbs-api.json")
    yaml_file = os.path.join(workspace_root, "proxmox-backup-server", "pbs-api.yaml")

    if not os.path.exists(json_file):
        print(f"Error: JSON file not found at {json_file}")
        print("Please run generate_openapi.py first.")
        return 1

    # Convert JSON to YAML
    if convert_json_to_yaml(json_file, yaml_file):
        # Get file sizes
        json_size = os.path.getsize(json_file)
        yaml_size = os.path.getsize(yaml_file)

        print("\nFile sizes:")
        print(f"JSON: {json_size:,} bytes")
        print(f"YAML: {yaml_size:,} bytes")

        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
