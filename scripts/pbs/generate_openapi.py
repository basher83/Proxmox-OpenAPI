#!/usr/bin/env python3
"""
Proxmox Backup Server OpenAPI specification generator.
Uses the enhanced UnifiedProxmoxParser with integrated standardization components.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add the parent scripts directory to the path so we can import the unified parser
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified_parser import UnifiedProxmoxParser, get_pbs_config


def find_apidoc_file() -> Optional[str]:
    """Find the PBS apidoc.js file using multiple search paths."""
    possible_paths = [
        "apidoc.js",  # When run from within the PBS directory
        "../../proxmox-backup-server/apidoc.js",  # From scripts/pbs/
        "../proxmox-backup-server/apidoc.js",  # From scripts/
        "proxmox-backup-server/apidoc.js",  # From project root
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def main() -> int:
    """Generate PBS OpenAPI specification using the enhanced unified parser."""
    print(
        "🚀 Creating Proxmox Backup Server OpenAPI specification using enhanced unified parser..."
    )

    # Find the apidoc.js file
    js_file = find_apidoc_file()
    if not js_file:
        print("❌ Error: Could not find apidoc.js file")
        print("   Expected locations:")
        print("     - apidoc.js (current directory)")
        print("     - ../../proxmox-backup-server/apidoc.js")
        print("     - ../proxmox-backup-server/apidoc.js")
        print("     - proxmox-backup-server/apidoc.js")
        return 1

    print(f"📂 Using input file: {js_file}")

    try:
        # Get PBS configuration with all integrated standardization components
        config = get_pbs_config()
        parser = UnifiedProxmoxParser(config)

        # Extract API schema using unified parser
        print("📊 Extracting API schema using enhanced unified parser...")
        schema = parser.extract_api_schema(js_file)

        # Flatten endpoints
        print("🔧 Flattening API endpoints...")
        endpoints = parser.flatten_api_endpoints(schema)
        print(f"✅ Found {len(endpoints)} endpoints")

        # Create OpenAPI specification with integrated standardization
        print("🏗️ Building OpenAPI specification with standardized components...")
        openapi_spec = parser.create_openapi_spec(endpoints)

        # Write JSON output
        output_file = "pbs-api.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

        print(f"🎉 OpenAPI JSON specification created: {output_file}")

        # Write YAML output if PyYAML is available
        try:
            import yaml

            yaml_file = "pbs-api.yaml"
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)
            print(f"🎉 OpenAPI YAML specification created: {yaml_file}")
        except ImportError:
            print(
                "⚠️  PyYAML not installed, skipping YAML output. Install with: pip install PyYAML"
            )

        # Report statistics
        total_operations = sum(
            len(
                [
                    k
                    for k in path_item.keys()
                    if k in ["get", "post", "put", "delete", "patch"]
                ]
            )
            for path_item in openapi_spec["paths"].values()
        )

        print("\n📊 Generation Summary:")
        print(f"   📈 Total endpoints: {len(openapi_spec['paths'])}")
        print(f"   🔧 Total operations: {total_operations}")
        print(f"   🏷️  Tags: {len(openapi_spec.get('tags', []))}")
        print(
            f"   🔐 Security schemes: {len(openapi_spec['components']['securitySchemes'])}"
        )
        print(f"   📋 Standard schemas: {len(openapi_spec['components']['schemas'])}")

        # Show integrated standardization components
        print("\n✅ Integrated Standardization Components:")
        print(
            f"   🔐 Security: {', '.join(openapi_spec['components']['securitySchemes'].keys())}"
        )
        print(
            f"   📋 Schemas: {', '.join(openapi_spec['components']['schemas'].keys())}"
        )
        print(f"   🌐 Server: {openapi_spec['servers'][0]['url']}")
        print(f"   📧 Contact: {openapi_spec['info']['contact']['email']}")

        # Show example endpoints
        print("\n🔍 Example endpoints:")
        example_paths = list(openapi_spec["paths"].keys())[:5]
        for i, path in enumerate(example_paths, 1):
            methods = list(openapi_spec["paths"][path].keys())
            print(f"   {i}. {path} ({', '.join(m.upper() for m in methods)})")

        print(
            f"\n✨ Enhanced unified parser successfully generated {len(openapi_spec['paths'])} consistent, standardized endpoints!"
        )
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
