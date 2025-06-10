#!/usr/bin/env python3
"""
Convert Proxmox VE OpenAPI specification from JSON to YAML format
"""

import json
import yaml
import sys

def convert_json_to_yaml(input_file, output_file):
    """Convert JSON OpenAPI spec to YAML format"""
    
    print(f"🔄 Converting {input_file} to YAML format...")
    
    try:
        # Read the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            
        print(f"   ✅ Loaded JSON specification")
        print(f"   📊 Paths: {len(json_data.get('paths', {}))}")
        print(f"   📋 Info: {json_data.get('info', {}).get('title', 'N/A')}")
        
        # Convert to YAML with proper formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(
                json_data, 
                f, 
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120,
                indent=2
            )
            
        print(f"   ✅ Successfully converted to {output_file}")
        
        # Get file sizes for comparison
        import os
        json_size = os.path.getsize(input_file)
        yaml_size = os.path.getsize(output_file)
        
        print(f"\n📁 File Comparison:")
        print(f"   JSON: {json_size:,} bytes ({json_size/1024/1024:.1f} MB)")
        print(f"   YAML: {yaml_size:,} bytes ({yaml_size/1024/1024:.1f} MB)")
        print(f"   Ratio: {yaml_size/json_size:.1%}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    input_file = "pve-api.json"
    output_file = "pve-api.yaml"
    
    print("🚀 Proxmox VE OpenAPI JSON to YAML Converter")
    print("=" * 50)
    
    if convert_json_to_yaml(input_file, output_file):
        print(f"\n🎉 Conversion completed successfully!")
        print(f"📄 YAML specification: {output_file}")
        
        # Show a sample of the YAML content
        print(f"\n📋 YAML Sample (first 20 lines):")
        with open(output_file, 'r') as f:
            lines = f.readlines()[:20]
            for i, line in enumerate(lines, 1):
                print(f"   {i:2d}: {line.rstrip()}")
            if len(lines) == 20:
                print("   ...")
                
    else:
        print(f"\n❌ Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 