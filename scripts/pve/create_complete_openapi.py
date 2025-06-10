#!/usr/bin/env python3
"""
Create complete OpenAPI specification from Proxmox VE API documentation
Final comprehensive parser
"""

import json
import os
import re
import sys
from typing import Dict, List, Any, Set

def extract_all_api_info(js_content: str) -> Dict[str, Dict]:
    """Extract all API information using comprehensive regex patterns"""
    
    # Dictionary to store all path information
    path_info = {}
    
    # First, find all path definitions
    print("🔍 Finding all API paths...")
    path_pattern = r'"path"\s*:\s*"([^"]+)"'
    paths = set(re.findall(path_pattern, js_content))
    print(f"   Found {len(paths)} unique paths")
    
    # For each path, find all associated methods and information
    for path in paths:
        print(f"   Processing: {path}")
        
        # Find all occurrences of this path in the content
        path_escaped = re.escape(path)
        path_occurrences = list(re.finditer(f'"path"\\s*:\\s*"{path_escaped}"', js_content))
        
        methods = {}
        
        for occurrence in path_occurrences:
            # Get a large context around this occurrence
            start = max(0, occurrence.start() - 1000)
            end = min(len(js_content), occurrence.end() + 10000)
            context = js_content[start:end]
            
            # Look for method definitions in this context
            method_patterns = [
                (r'"GET"\s*:\s*\{', 'GET'),
                (r'"POST"\s*:\s*\{', 'POST'),
                (r'"PUT"\s*:\s*\{', 'PUT'),
                (r'"DELETE"\s*:\s*\{', 'DELETE')
            ]
            
            for pattern, method in method_patterns:
                method_matches = list(re.finditer(pattern, context))
                
                for method_match in method_matches:
                    # Extract the method block starting from the opening brace
                    method_start = method_match.end() - 1  # Start from the opening brace
                    
                    # Find the matching closing brace
                    brace_count = 0
                    i = method_start
                    while i < len(context):
                        if context[i] == '{':
                            brace_count += 1
                        elif context[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                method_block = context[method_start + 1:i]  # Exclude braces
                                break
                        i += 1
                    
                    if brace_count == 0:  # We found a complete method block
                        method_info = parse_method_block(method_block)
                        method_info['method'] = method
                        methods[method] = method_info
        
        if methods:
            path_info[path] = methods
    
    return path_info

def parse_method_block(method_block: str) -> Dict:
    """Parse a method block to extract all relevant information"""
    info = {}
    
    # Extract basic fields
    fields = {
        'description': r'"description"\s*:\s*"([^"]*(?:\\.[^"]*)*)"',
        'name': r'"name"\s*:\s*"([^"]*)"',
        'allowtoken': r'"allowtoken"\s*:\s*(\d+)',
    }
    
    for field, pattern in fields.items():
        match = re.search(pattern, method_block)
        if match:
            if field == 'allowtoken':
                info[field] = int(match.group(1)) == 1
            else:
                info[field] = match.group(1).replace('\\"', '"').replace('\\n', '\n')
    
    # Extract parameters
    param_match = re.search(r'"parameters"\s*:\s*\{', method_block)
    if param_match:
        param_start = param_match.end() - 1
        param_block = extract_nested_block(method_block, param_start)
        if param_block:
            info['parameters'] = parse_parameters_block(param_block)
    
    # Extract returns
    returns_match = re.search(r'"returns"\s*:\s*\{', method_block)
    if returns_match:
        returns_start = returns_match.end() - 1
        returns_block = extract_nested_block(method_block, returns_start)
        if returns_block:
            info['returns'] = parse_returns_block(returns_block)
    
    # Extract permissions
    perm_match = re.search(r'"permissions"\s*:\s*\{', method_block)
    if perm_match:
        perm_start = perm_match.end() - 1
        perm_block = extract_nested_block(method_block, perm_start)
        if perm_block:
            perm_desc = re.search(r'"description"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', perm_block)
            if perm_desc:
                info['permissions'] = perm_desc.group(1).replace('\\"', '"')
    
    return info

def extract_nested_block(content: str, start_pos: int) -> str:
    """Extract a nested JSON block starting from a position"""
    if start_pos >= len(content) or content[start_pos] != '{':
        return ""
    
    brace_count = 0
    i = start_pos
    
    while i < len(content):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return content[start_pos + 1:i]  # Exclude braces
        i += 1
    
    return ""

def parse_parameters_block(param_block: str) -> Dict:
    """Parse parameters block to extract parameter definitions"""
    parameters = {}
    
    # Look for properties section
    props_match = re.search(r'"properties"\s*:\s*\{', param_block)
    if not props_match:
        return parameters
    
    props_start = props_match.end() - 1
    props_block = extract_nested_block(param_block, props_start)
    
    if not props_block:
        return parameters
    
    # Extract individual parameters using a more robust approach
    # Split by parameter definitions
    param_pattern = r'"(\w+)"\s*:\s*\{'
    param_matches = list(re.finditer(param_pattern, props_block))
    
    for i, param_match in enumerate(param_matches):
        param_name = param_match.group(1)
        param_start = param_match.end() - 1
        
        # Find the end of this parameter definition
        if i + 1 < len(param_matches):
            param_end = param_matches[i + 1].start()
            param_content = props_block[param_start:param_end]
        else:
            param_content = props_block[param_start:]
        
        # Extract the parameter block
        param_def = extract_nested_block(param_content, 0)
        if param_def:
            param_info = {}
            
            # Extract parameter properties
            type_match = re.search(r'"type"\s*:\s*"([^"]*)"', param_def)
            if type_match:
                param_info['type'] = type_match.group(1)
            
            desc_match = re.search(r'"description"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', param_def)
            if desc_match:
                param_info['description'] = desc_match.group(1).replace('\\"', '"').replace('\\n', '\n')
            
            opt_match = re.search(r'"optional"\s*:\s*(\d+)', param_def)
            if opt_match:
                param_info['optional'] = int(opt_match.group(1)) == 1
            
            default_match = re.search(r'"default"\s*:\s*([^,}]+)', param_def)
            if default_match:
                default_val = default_match.group(1).strip().strip('"')
                try:
                    if default_val.isdigit():
                        param_info['default'] = int(default_val)
                    elif default_val.lower() in ['true', 'false']:
                        param_info['default'] = default_val.lower() == 'true'
                    else:
                        param_info['default'] = default_val
                except:
                    param_info['default'] = default_val
            
            format_match = re.search(r'"format"\s*:\s*"([^"]*)"', param_def)
            if format_match:
                param_info['format'] = format_match.group(1)
            
            # Extract enum values
            enum_match = re.search(r'"enum"\s*:\s*\[([^\]]*)\]', param_def)
            if enum_match:
                enum_content = enum_match.group(1)
                enum_values = re.findall(r'"([^"]*)"', enum_content)
                if enum_values:
                    param_info['enum'] = enum_values
            
            parameters[param_name] = param_info
    
    return parameters

def parse_returns_block(returns_block: str) -> Dict:
    """Parse returns block to extract return type information"""
    returns_info = {}
    
    type_match = re.search(r'"type"\s*:\s*"([^"]*)"', returns_block)
    if type_match:
        returns_info['type'] = type_match.group(1)
    
    return returns_info

def create_openapi_specification(path_info: Dict[str, Dict]) -> Dict:
    """Create complete OpenAPI specification from extracted path information"""
    
    openapi_spec = {
        'openapi': '3.0.3',
        'info': {
            'title': 'Proxmox VE API',
            'description': '''Complete Proxmox Virtual Environment API specification for managing virtualized infrastructure.

This specification covers all aspects of Proxmox VE management including:
- **Virtual Machine Management**: Create, configure, and manage VMs
- **Container Management**: LXC container lifecycle management  
- **Storage Management**: Configure and manage storage backends
- **Network Configuration**: Virtual networks and firewall rules
- **Cluster Operations**: Multi-node cluster management
- **User Management**: Authentication, authorization, and access control
- **Backup & Restore**: Data protection and recovery
- **Monitoring**: System status and performance metrics

The API supports both token-based authentication and session-based authentication with CSRF protection.''',
            'version': '8.0.0',
            'contact': {
                'name': 'Proxmox Support',
                'url': 'https://www.proxmox.com',
                'email': 'support@proxmox.com'
            },
            'license': {
                'name': 'AGPL v3',
                'url': 'https://www.gnu.org/licenses/agpl-3.0.html'
            }
        },
        'servers': [
            {
                'url': 'https://{host}:8006/api2/json',
                'description': 'Proxmox VE Server (JSON format)',
                'variables': {
                    'host': {
                        'default': 'localhost',
                        'description': 'Proxmox VE server hostname or IP address'
                    }
                }
            }
        ],
        'components': {
            'securitySchemes': {
                'ApiTokenAuth': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'Authorization',
                    'description': 'API token authentication. Format: PVEAPIToken=USER@REALM!TOKENID=UUID'
                },
                'CookieAuth': {
                    'type': 'apiKey',
                    'in': 'cookie',
                    'name': 'PVEAuthCookie',
                    'description': 'Session cookie authentication obtained from /access/ticket'
                },
                'CSRFPreventionToken': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'CSRFPreventionToken',
                    'description': 'CSRF prevention token required for state-changing operations when using cookie auth'
                }
            },
            'schemas': {
                'Error': {
                    'type': 'object',
                    'properties': {
                        'data': {
                            'type': 'object',
                            'nullable': True
                        },
                        'errors': {
                            'type': 'object',
                            'additionalProperties': {
                                'type': 'string'
                            }
                        }
                    }
                },
                'Task': {
                    'type': 'object',
                    'properties': {
                        'data': {
                            'type': 'string',
                            'description': 'Task ID for tracking async operations'
                        }
                    }
                }
            }
        },
        'paths': {}
    }
    
    # Convert each path and its methods
    for path, methods in path_info.items():
        openapi_path = {}
        
        for method, method_info in methods.items():
            method_lower = method.lower()
            
            # Create operation
            operation = {
                'summary': method_info.get('name', method_lower).replace('_', ' ').title(),
                'description': method_info.get('description', f'{method} operation for {path}'),
                'operationId': f"{method_lower}_{path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}",
                'tags': [determine_tag(path)]
            }
            
            # Add parameters
            parameters = []
            
            # Add path parameters
            path_params = re.findall(r'\{([^}]+)\}', path)
            for param in path_params:
                parameters.append({
                    'name': param,
                    'in': 'path',
                    'required': True,
                    'description': f'{param} identifier',
                    'schema': get_path_param_schema(param)
                })
            
            # Add query parameters
            if 'parameters' in method_info:
                for param_name, param_info in method_info['parameters'].items():
                    if param_name not in path_params:
                        param_schema = convert_param_to_openapi_schema(param_info)
                        parameters.append({
                            'name': param_name,
                            'in': 'query',
                            'required': not param_info.get('optional', False),
                            'description': param_info.get('description', ''),
                            'schema': param_schema
                        })
            
            if parameters:
                operation['parameters'] = parameters
            
            # Add responses
            returns_info = method_info.get('returns', {})
            response_schema = convert_returns_to_openapi_schema(returns_info)
            
            operation['responses'] = {
                '200': {
                    'description': 'Successful operation',
                    'content': {
                        'application/json': {
                            'schema': response_schema
                        }
                    }
                },
                '400': {
                    'description': 'Bad request',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '401': {
                    'description': 'Unauthorized',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '403': {
                    'description': 'Forbidden',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                },
                '500': {
                    'description': 'Internal server error',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                }
            }
            
            # Add security
            if method_info.get('allowtoken', True):
                operation['security'] = [
                    {'ApiTokenAuth': []},
                    {'CookieAuth': [], 'CSRFPreventionToken': []}
                ]
            
            # Add permissions info to description
            if 'permissions' in method_info:
                operation['description'] += f"\n\n**Required permissions:** {method_info['permissions']}"
            
            openapi_path[method_lower] = operation
        
        openapi_spec['paths'][path] = openapi_path
    
    return openapi_spec

def determine_tag(path: str) -> str:
    """Determine the OpenAPI tag from the path"""
    path_parts = path.strip('/').split('/')
    if path_parts:
        first_part = path_parts[0]
        # Map to appropriate tags
        tag_mapping = {
            'nodes': 'Nodes',
            'cluster': 'Cluster', 
            'access': 'Access Control',
            'storage': 'Storage',
            'pools': 'Resource Pools',
            'version': 'System Info'
        }
        return tag_mapping.get(first_part, 'Other')
    return 'Other'

def get_path_param_schema(param_name: str) -> Dict:
    """Get appropriate schema for path parameters"""
    if param_name == 'vmid':
        return {
            'type': 'integer',
            'minimum': 1,
            'maximum': 999999999,
            'description': 'Virtual machine ID'
        }
    elif param_name == 'node':
        return {
            'type': 'string',
            'pattern': r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$',
            'description': 'Node name'
        }
    elif param_name == 'storage':
        return {
            'type': 'string',
            'description': 'Storage identifier'
        }
    else:
        return {'type': 'string'}

def convert_param_to_openapi_schema(param_info: Dict) -> Dict:
    """Convert parameter info to OpenAPI schema"""
    param_type = param_info.get('type', 'string')
    schema = {'type': param_type}
    
    if 'description' in param_info:
        schema['description'] = param_info['description']
    
    if 'default' in param_info:
        schema['default'] = param_info['default']
    
    if 'enum' in param_info:
        schema['enum'] = param_info['enum']
    
    return schema

def convert_returns_to_openapi_schema(returns_info: Dict) -> Dict:
    """Convert returns info to OpenAPI schema"""
    if not returns_info or not returns_info.get('type'):
        return {'type': 'object'}
    
    return_type = returns_info['type']
    
    if return_type == 'array':
        return {
            'type': 'array',
            'items': {'type': 'object'}
        }
    elif return_type == 'object':
        return {'type': 'object'}
    else:
        return {'type': return_type}

def main():
    # Look for apidoc.js in the current directory (when run from scripts/pve)
    # or in the proxmox-virtual-environment directory
    possible_paths = [
        "apidoc.js",
        "../../proxmox-virtual-environment/apidoc.js",
        "../proxmox-virtual-environment/apidoc.js"
    ]
    
    js_file = None
    for path in possible_paths:
        if os.path.exists(path):
            js_file = path
            break
    
    if not js_file:
        print("❌ Error: Could not find apidoc.js file")
        print("   Expected locations:")
        for path in possible_paths:
            print(f"     - {path}")
        return
    
    print("🚀 Creating complete Proxmox VE OpenAPI specification...")
    print(f"📂 Using input file: {js_file}")
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        print("📊 Extracting all API information...")
        path_info = extract_all_api_info(js_content)
        
        if not path_info:
            print("❌ No API information extracted")
            return
        
        print(f"✅ Successfully extracted {len(path_info)} endpoints")
        
        # Count total operations
        total_operations = sum(len(methods) for methods in path_info.values())
        print(f"   🔧 Total operations: {total_operations}")
        
        # Create OpenAPI specification
        print("🔧 Building OpenAPI specification...")
        openapi_spec = create_openapi_specification(path_info)
        
        # Write to file
        output_file = 'pve-api.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
        
        print(f"🎉 Complete OpenAPI specification created: {output_file}")
        print(f"   📈 Total paths: {len(openapi_spec['paths'])}")
        print(f"   🔧 Total operations: {sum(len(methods) for methods in openapi_spec['paths'].values())}")
        
        # Statistics
        tags = {}
        method_counts = {'get': 0, 'post': 0, 'put': 0, 'delete': 0}
        
        for path_methods in openapi_spec['paths'].values():
            for method, operation in path_methods.items():
                tag = operation.get('tags', ['Other'])[0]
                tags[tag] = tags.get(tag, 0) + 1
                method_counts[method] = method_counts.get(method, 0) + 1
        
        print("\n📊 API Statistics:")
        print("   By category:")
        for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True):
            print(f"     - {tag}: {count} operations")
        
        print("   By HTTP method:")
        for method, count in sorted(method_counts.items()):
            if count > 0:
                print(f"     - {method.upper()}: {count} operations")
        
        # Show example endpoints
        print("\n🔍 Example endpoints:")
        example_paths = list(openapi_spec['paths'].keys())[:10]
        for i, path in enumerate(example_paths, 1):
            methods = list(openapi_spec['paths'][path].keys())
            print(f"   {i}. {path} ({', '.join(m.upper() for m in methods)})")
        
        print(f"\n✨ OpenAPI specification successfully created with {len(openapi_spec['paths'])} endpoints!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 