#!/usr/bin/env python3
"""
Generate OpenAPI specification for Proxmox Backup Server.
Parses PBS API documentation and creates comprehensive OpenAPI 3.0.3 specification.
"""

import json
import re
import ast
from typing import Dict, List, Any
import os
import sys


def extract_api_schema_robust(js_file_path: str) -> List[Dict]:
    """Extract the API schema using a more robust approach."""
    with open(js_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the start and end of apiSchema
    start_match = re.search(r'var apiSchema = \[', content)
    if not start_match:
        raise ValueError("Could not find apiSchema start")
    
    start_pos = start_match.end() - 1  # Include the opening bracket
    
    # Find the matching closing bracket
    bracket_count = 0
    end_pos = start_pos
    
    for i, char in enumerate(content[start_pos:], start_pos):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                end_pos = i + 1
                break
    
    if bracket_count != 0:
        raise ValueError("Could not find apiSchema end")
    
    schema_str = content[start_pos:end_pos]
    
    # Use Node.js to parse the JavaScript if available
    try:
        return parse_with_nodejs(schema_str)
    except:
        # Fallback to Python-based parsing
        return parse_with_python_fallback(schema_str)


def parse_with_nodejs(schema_str: str) -> List[Dict]:
    """Try to parse using Node.js."""
    import subprocess
    import tempfile
    
    # Create temporary JS file
    js_code = f"""
    const apiSchema = {schema_str};
    console.log(JSON.stringify(apiSchema, null, 2));
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_code)
        temp_file = f.name
    
    try:
        # Run with node
        result = subprocess.run(['node', temp_file], capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            raise Exception(f"Node.js error: {result.stderr}")
    finally:
        os.unlink(temp_file)


def parse_with_python_fallback(schema_str: str) -> List[Dict]:
    """Fallback parser using Python regex and string manipulation."""
    # More aggressive cleanup for JavaScript to JSON conversion
    
    # Handle regex patterns - replace them with string placeholders
    regex_patterns = []
    pattern_counter = 0
    
    def replace_regex(match):
        nonlocal pattern_counter
        pattern = match.group(0)
        placeholder = f'"__REGEX_PATTERN_{pattern_counter}__"'
        regex_patterns.append((placeholder, pattern))
        pattern_counter += 1
        return placeholder
    
    # Find and replace regex patterns
    schema_str = re.sub(r'"/[^"]*/"', replace_regex, schema_str)
    
    # Basic JavaScript to JSON conversion
    # Replace single quotes with double quotes (but not inside regex patterns)
    schema_str = re.sub(r"'([^']*)':", r'"\1":', schema_str)
    schema_str = re.sub(r": '([^']*)'", r': "\1"', schema_str)
    
    # Handle boolean and null values
    schema_str = re.sub(r'\btrue\b', 'true', schema_str)
    schema_str = re.sub(r'\bfalse\b', 'false', schema_str)
    schema_str = re.sub(r'\bnull\b', 'null', schema_str)
    
    # Remove trailing commas
    schema_str = re.sub(r',(\s*[}\]])', r'\1', schema_str)
    
    # Handle undefined
    schema_str = re.sub(r'\bundefined\b', 'null', schema_str)
    
    try:
        # Parse JSON
        schema = json.loads(schema_str)
        
        # Restore regex patterns
        def restore_patterns(obj):
            if isinstance(obj, dict):
                return {k: restore_patterns(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [restore_patterns(item) for item in obj]
            elif isinstance(obj, str):
                for placeholder, original in regex_patterns:
                    if obj == placeholder.strip('"'):
                        return original
                return obj
            return obj
        
        return restore_patterns(schema)
        
    except json.JSONDecodeError as e:
        # If still failing, try a more basic approach
        return extract_basic_structure(schema_str)


def extract_basic_structure(content: str) -> List[Dict]:
    """Extract basic structure when JSON parsing fails."""
    endpoints = []
    
    # Look for path patterns
    path_pattern = r'"path":\s*"([^"]+)"'
    method_pattern = r'"(GET|POST|PUT|DELETE|PATCH)":\s*\{'
    
    paths = re.findall(path_pattern, content)
    
    for path in paths:
        # Find the context around this path
        path_start = content.find(f'"path": "{path}"')
        if path_start == -1:
            continue
        
        # Find the containing object
        obj_start = content.rfind('{', 0, path_start)
        bracket_count = 1
        obj_end = obj_start + 1
        
        for i in range(obj_start + 1, len(content)):
            if content[i] == '{':
                bracket_count += 1
            elif content[i] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    obj_end = i + 1
                    break
        
        obj_content = content[obj_start:obj_end]
        
        # Extract methods
        methods = re.findall(method_pattern, obj_content)
        
        if methods:
            endpoint = {
                'path': path,
                'methods': {method: {'description': f'{method} {path}', 'method': method} for method in methods}
            }
            endpoints.append(endpoint)
    
    return [{'children': endpoints, 'path': '/', 'text': 'root'}] if endpoints else []


def flatten_api_endpoints(schema: List[Dict], parent_path: str = "") -> List[Dict]:
    """Flatten the nested API schema structure into a list of endpoints."""
    endpoints = []
    
    for item in schema:
        if not isinstance(item, dict):
            continue
            
        current_path = parent_path + item.get('path', '')
        
        # Add current endpoint if it has info (HTTP methods)
        if 'info' in item and item['info']:
            endpoint = {
                'path': current_path,
                'methods': item['info'],
                'text': item.get('text', ''),
                'leaf': item.get('leaf', 0)
            }
            endpoints.append(endpoint)
        
        # Recursively process children
        if 'children' in item and item['children']:
            child_endpoints = flatten_api_endpoints(item['children'], current_path)
            endpoints.extend(child_endpoints)
    
    return endpoints


def convert_pbs_type_to_openapi(pbs_type: str, format_hint: str = None) -> Dict:
    """Convert PBS type definitions to OpenAPI schema types."""
    type_mapping = {
        'string': {'type': 'string'},
        'integer': {'type': 'integer'},
        'number': {'type': 'number'},
        'boolean': {'type': 'boolean'},
        'array': {'type': 'array'},
        'object': {'type': 'object'},
        'null': {'type': 'null'}
    }
    
    if pbs_type in type_mapping:
        schema = type_mapping[pbs_type].copy()
        
        # Add format if provided
        if format_hint:
            schema['format'] = format_hint
            
        return schema
    
    # Default to string for unknown types
    return {'type': 'string', 'description': f'Type: {pbs_type}'}


def convert_parameters_to_openapi(pbs_params: Dict) -> Dict:
    """Convert PBS parameter definitions to OpenAPI parameters."""
    if not pbs_params or not isinstance(pbs_params, dict) or 'properties' not in pbs_params:
        return {'type': 'object', 'properties': {}}
    
    properties = {}
    required = []
    
    for param_name, param_info in pbs_params['properties'].items():
        if not isinstance(param_info, dict):
            continue
            
        param_schema = convert_pbs_type_to_openapi(
            param_info.get('type', 'string'),
            param_info.get('format')
        )
        
        # Add description
        if 'description' in param_info:
            param_schema['description'] = param_info['description']
        
        # Add constraints (safely)
        for constraint in ['minLength', 'maxLength', 'minimum', 'maximum']:
            if constraint in param_info:
                try:
                    param_schema[constraint] = param_info[constraint]
                except:
                    pass
        
        # Handle pattern safely
        if 'pattern' in param_info:
            pattern = param_info['pattern']
            if isinstance(pattern, str):
                # Clean up regex pattern
                if pattern.startswith('/') and pattern.endswith('/'):
                    pattern = pattern[1:-1]
                elif pattern.startswith('"/') and pattern.endswith('/"'):
                    pattern = pattern[2:-2]
                try:
                    # Test if it's a valid regex
                    re.compile(pattern)
                    param_schema['pattern'] = pattern
                except:
                    # If invalid, skip the pattern
                    pass
        
        # Handle enums
        if 'enum' in param_info and isinstance(param_info['enum'], list):
            param_schema['enum'] = param_info['enum']
        
        # Handle default values
        if 'default' in param_info:
            param_schema['default'] = param_info['default']
        
        # Handle array items
        if param_info.get('type') == 'array' and 'items' in param_info:
            items_info = param_info['items']
            if isinstance(items_info, dict):
                param_schema['items'] = convert_pbs_type_to_openapi(
                    items_info.get('type', 'string')
                )
        
        properties[param_name] = param_schema
        
        # Add to required if not optional
        if not param_info.get('optional', False):
            required.append(param_name)
    
    result = {
        'type': 'object',
        'properties': properties
    }
    
    if required:
        result['required'] = required
    
    return result


def convert_endpoint_to_openapi(endpoint: Dict) -> Dict:
    """Convert a PBS endpoint to OpenAPI path item."""
    path_item = {}
    
    for method, method_info in endpoint['methods'].items():
        if not isinstance(method_info, dict):
            continue
            
        operation = {
            'summary': method_info.get('description', f'{method} {endpoint["path"]}'),
            'description': method_info.get('description', ''),
            'operationId': f"{method.lower()}_{endpoint['path'].replace('/', '_').replace('{', '').replace('}', '').strip('_')}",
            'tags': [get_tag_from_path(endpoint['path'])]
        }
        
        # Add parameters
        if 'parameters' in method_info and method_info['parameters']:
            # Path parameters
            path_params = re.findall(r'\{([^}]+)\}', endpoint['path'])
            parameters = []
            
            for param in path_params:
                parameters.append({
                    'name': param,
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'string'},
                    'description': f'The {param} parameter'
                })
            
            # Query/body parameters
            param_schema = convert_parameters_to_openapi(method_info['parameters'])
            
            if method.upper() in ['GET', 'DELETE']:
                # Add query parameters
                if param_schema.get('properties'):
                    for param_name, param_def in param_schema['properties'].items():
                        if param_name not in path_params:
                            param_obj = {
                                'name': param_name,
                                'in': 'query',
                                'required': param_name in param_schema.get('required', []),
                                'schema': param_def
                            }
                            if 'description' in param_def:
                                param_obj['description'] = param_def['description']
                            parameters.append(param_obj)
            else:
                # Add request body for POST/PUT methods
                if param_schema.get('properties'):
                    # Filter out path parameters from request body
                    body_properties = {k: v for k, v in param_schema['properties'].items() 
                                     if k not in path_params}
                    body_required = [r for r in param_schema.get('required', []) 
                                   if r not in path_params]
                    
                    if body_properties:
                        body_schema = {
                            'type': 'object',
                            'properties': body_properties
                        }
                        if body_required:
                            body_schema['required'] = body_required
                            
                        operation['requestBody'] = {
                            'required': bool(body_required),
                            'content': {
                                'application/json': {
                                    'schema': body_schema
                                }
                            }
                        }
            
            if parameters:
                operation['parameters'] = parameters
        
        # Add responses
        responses = {'200': {'description': 'Success'}}
        
        if 'returns' in method_info and method_info['returns']:
            returns_info = method_info['returns']
            if isinstance(returns_info, dict):
                response_schema = convert_returns_to_openapi_schema(returns_info)
                responses['200'] = {
                    'description': returns_info.get('description', 'Success'),
                    'content': {
                        'application/json': {
                            'schema': response_schema
                        }
                    }
                }
        
        # Add common error responses
        responses.update({
            '400': {'description': 'Bad Request'},
            '401': {'description': 'Unauthorized'},
            '403': {'description': 'Forbidden'},
            '404': {'description': 'Not Found'},
            '500': {'description': 'Internal Server Error'}
        })
        
        operation['responses'] = responses
        
        path_item[method.lower()] = operation
    
    return path_item


def convert_returns_to_openapi_schema(returns_info: Dict) -> Dict:
    """Convert PBS returns definition to OpenAPI schema."""
    if not isinstance(returns_info, dict):
        return {'type': 'string'}
    
    schema = convert_pbs_type_to_openapi(
        returns_info.get('type', 'object')
    )
    
    # Handle array returns
    if returns_info.get('type') == 'array' and 'items' in returns_info:
        items_info = returns_info['items']
        if isinstance(items_info, dict):
            schema['items'] = convert_returns_to_openapi_schema(items_info)
    
    # Handle object properties
    if returns_info.get('type') == 'object' and 'properties' in returns_info:
        properties = {}
        for prop_name, prop_info in returns_info['properties'].items():
            if isinstance(prop_info, dict):
                properties[prop_name] = convert_returns_to_openapi_schema(prop_info)
        if properties:
            schema['properties'] = properties
    
    # Add description
    if 'description' in returns_info:
        schema['description'] = returns_info['description']
    
    return schema


def create_openapi_spec(endpoints: List[Dict]) -> Dict:
    """Create the complete OpenAPI specification."""
    paths = {}
    
    for endpoint in endpoints:
        if not endpoint.get('methods'):
            continue
            
        path = endpoint['path']
        path_item = convert_endpoint_to_openapi(endpoint)
        
        if path_item:
            paths[path] = path_item
    
    # Get unique tags
    tags = set()
    for endpoint in endpoints:
        if endpoint.get('methods'):
            tag = get_tag_from_path(endpoint['path'])
            tags.add(tag)
    
    spec = {
        'openapi': '3.0.3',
        'info': {
            'title': 'Proxmox Backup Server API',
            'description': 'Proxmox Backup Server API Documentation',
            'version': '3.0.0',
            'contact': {
                'name': 'Proxmox Support',
                'url': 'https://www.proxmox.com'
            },
            'license': {
                'name': 'AGPL-3.0',
                'url': 'https://www.gnu.org/licenses/agpl-3.0.html'
            }
        },
        'servers': [
            {
                'url': 'https://{server}:8007',
                'description': 'Proxmox Backup Server',
                'variables': {
                    'server': {
                        'default': 'localhost',
                        'description': 'Proxmox Backup Server hostname or IP'
                    }
                }
            }
        ],
        'tags': [{'name': tag, 'description': f'{tag.title()} related operations'} 
                for tag in sorted(tags)],
        'paths': paths,
        'components': {
            'securitySchemes': {
                'ticketAuth': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'Authorization',
                    'description': 'Proxmox authentication ticket'
                },
                'csrfToken': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'CSRFPreventionToken',
                    'description': 'CSRF prevention token'
                }
            }
        },
        'security': [
            {
                'ticketAuth': [],
                'csrfToken': []
            }
        ]
    }
    
    return spec


def get_tag_from_path(path: str) -> str:
    """Extract tag name from API path."""
    parts = path.strip('/').split('/')
    if len(parts) > 0 and parts[0]:
        return parts[0]
    return 'default'


def main():
    """Main function to parse PBS API and generate OpenAPI spec."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(os.path.dirname(script_dir))
    
    js_file_path = os.path.join(workspace_root, 'proxmox-backup-server', 'apidoc.js')
    
    if not os.path.exists(js_file_path):
        print(f"Error: Could not find apidoc.js at {js_file_path}")
        return 1
    
    try:
        print("Extracting API schema from PBS apidoc.js...")
        schema = extract_api_schema_robust(js_file_path)
        
        print("Flattening API endpoints...")
        endpoints = flatten_api_endpoints(schema)
        print(f"Found {len(endpoints)} endpoints")
        
        print("Creating OpenAPI specification...")
        openapi_spec = create_openapi_spec(endpoints)
        
        # Create output directory
        pbs_dir = os.path.join(workspace_root, 'proxmox-backup-server')
        os.makedirs(pbs_dir, exist_ok=True)
        
        # Write JSON file
        json_file = os.path.join(pbs_dir, 'pbs-api.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
        
        print(f"OpenAPI JSON specification written to: {json_file}")
        
        # Also write YAML file
        try:
            import yaml
            yaml_file = os.path.join(pbs_dir, 'pbs-api.yaml')
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)
            print(f"OpenAPI YAML specification written to: {yaml_file}")
        except ImportError:
            print("PyYAML not installed, skipping YAML output. Install with: pip install PyYAML")
        
        print(f"\nSummary:")
        print(f"- Total endpoints: {len(endpoints)}")
        print(f"- Total paths: {len(openapi_spec['paths'])}")
        
        # Count operations
        total_operations = 0
        for path_item in openapi_spec['paths'].values():
            total_operations += len([k for k in path_item.keys() if k in ['get', 'post', 'put', 'delete', 'patch']])
        
        print(f"- Total operations: {total_operations}")
        print(f"- Tags: {len(openapi_spec['tags'])}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main()) 