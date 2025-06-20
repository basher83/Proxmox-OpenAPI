#!/usr/bin/env python3
"""
Unified parser for Proxmox API documentation.
Supports both PVE and PBS API parsing with comprehensive standardization.
Incorporates unified security schemes, server configuration, info sections, and error responses.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ProxmoxAPI(Enum):
    """Enum for different Proxmox API types."""

    PVE = "pve"
    PBS = "pbs"


@dataclass
class APIConfig:
    """Enhanced configuration for API parsing with standardized templates."""

    api_type: ProxmoxAPI
    title: str
    description: str
    version: str
    default_port: int
    server_path: str
    auth_schemes: Dict[str, Dict[str, Any]]
    tag_mapping: Dict[str, str]
    # Enhanced standardization fields
    contact_email: str = "support@proxmox.com"
    security_patterns: Optional[List[Dict[str, Any]]] = None
    enable_session_auth: bool = False


class UnifiedProxmoxParser:
    """Unified parser for Proxmox APIs with comprehensive standardization."""

    _file_cache: Dict[str, Tuple[str, float]] = {}  # {file_path: (content, mtime)}

    _API_SCHEMA_PATTERN = re.compile(r"(var|const|let)\s+apiSchema\s*=\s*\[")
    _REGEX_PATTERN = re.compile(r'"/[^"]*/"')
    _JS_SINGLE_QUOTE_KEY = re.compile(r"'([^']*)':")
    _JS_SINGLE_QUOTE_VALUE = re.compile(r": '([^']*)'")
    _JS_TRUE = re.compile(r"\btrue\b")
    _JS_FALSE = re.compile(r"\bfalse\b")
    _JS_NULL = re.compile(r"\bnull\b")
    _JS_TRAILING_COMMA = re.compile(r",(\s*[}\]])")
    _JS_UNDEFINED = re.compile(r"\bundefined\b")
    _PATH_PATTERN = re.compile(r'"path":\s*"([^"]+)"')
    _METHOD_PATTERN = re.compile(r'"(GET|POST|PUT|DELETE|PATCH)":\s*\{')
    _PATH_PARAMS_PATTERN = re.compile(r"\{([^}]+)\}")

    def __init__(self, config: APIConfig):
        self.config = config

    def extract_api_schema(self, js_file_path: str) -> List[Dict[str, Any]]:
        """Extract the API schema using multiple fallback methods with file caching."""
        file_path = Path(js_file_path).resolve()
        current_mtime = file_path.stat().st_mtime

        if str(file_path) in self._file_cache:
            cached_content, cached_mtime = self._file_cache[str(file_path)]
            if cached_mtime == current_mtime:
                content = cached_content
            else:
                with open(js_file_path, encoding="utf-8") as f:
                    content = f.read()
                self._file_cache[str(file_path)] = (content, current_mtime)
        else:
            with open(js_file_path, encoding="utf-8") as f:
                content = f.read()
            self._file_cache[str(file_path)] = (content, current_mtime)

        # Find the start and end of apiSchema (handle both var and const)
        start_match = self._API_SCHEMA_PATTERN.search(content)
        if not start_match:
            raise ValueError("Could not find apiSchema start")

        start_pos = start_match.end() - 1  # Include the opening bracket

        # Find the matching closing bracket
        bracket_count = 0
        end_pos = start_pos

        for i, char in enumerate(content[start_pos:], start_pos):
            if char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    end_pos = i + 1
                    break

        if bracket_count != 0:
            raise ValueError("Could not find apiSchema end")

        schema_str = content[start_pos:end_pos]

        # Try multiple parsing methods
        try:
            return self._parse_with_nodejs(schema_str)
        except Exception:
            try:
                return self._parse_with_python_fallback(schema_str)
            except Exception:
                return self._extract_basic_structure(content)

    def _parse_with_nodejs(self, schema_str: str) -> List[Dict[str, Any]]:
        """Try to parse using Node.js."""
        js_code = f"""
        const apiSchema = {schema_str};
        console.log(JSON.stringify(apiSchema, null, 2));
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(js_code)
            temp_file = f.name

        try:
            result = subprocess.run(["node", temp_file], capture_output=True, text=True)
            if result.returncode == 0:
                parsed_result = json.loads(result.stdout)
                return parsed_result if isinstance(parsed_result, list) else [parsed_result]
            else:
                raise Exception(f"Node.js error: {result.stderr}")
        finally:
            os.unlink(temp_file)

    def _parse_with_python_fallback(self, schema_str: str) -> List[Dict[str, Any]]:
        """Fallback parser using Python regex and string manipulation."""
        # Handle regex patterns - replace them with string placeholders
        regex_patterns = []
        pattern_counter = 0

        def replace_regex(match: Any) -> str:
            nonlocal pattern_counter
            pattern = match.group(0)
            placeholder = f'"__REGEX_PATTERN_{pattern_counter}__"'
            regex_patterns.append((placeholder, pattern))
            pattern_counter += 1
            return placeholder

        # Find and replace regex patterns
        schema_str = self._REGEX_PATTERN.sub(replace_regex, schema_str)

        # Basic JavaScript to JSON conversion using pre-compiled patterns
        schema_str = self._JS_SINGLE_QUOTE_KEY.sub(r'"\1":', schema_str)
        schema_str = self._JS_SINGLE_QUOTE_VALUE.sub(r': "\1"', schema_str)
        schema_str = self._JS_TRUE.sub("true", schema_str)
        schema_str = self._JS_FALSE.sub("false", schema_str)
        schema_str = self._JS_NULL.sub("null", schema_str)
        schema_str = self._JS_TRAILING_COMMA.sub(r"\1", schema_str)
        schema_str = self._JS_UNDEFINED.sub("null", schema_str)

        try:
            schema = json.loads(schema_str)

            # Restore regex patterns
            def restore_patterns(obj: Any) -> Any:
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

            restored_schema = restore_patterns(schema)
            if isinstance(restored_schema, list):
                return restored_schema
            else:
                return [restored_schema] if isinstance(restored_schema, dict) else []

        except json.JSONDecodeError:
            return self._extract_basic_structure(schema_str)

    def _extract_basic_structure(self, content: str) -> List[Dict[str, Any]]:
        """Extract basic structure when JSON parsing fails."""
        endpoints = []

        paths = self._PATH_PATTERN.findall(content)

        for path in paths:
            path_start = content.find(f'"path": "{path}"')
            if path_start == -1:
                continue

            obj_start = content.rfind("{", 0, path_start)
            bracket_count = 1
            obj_end = obj_start + 1

            for i in range(obj_start + 1, len(content)):
                if content[i] == "{":
                    bracket_count += 1
                elif content[i] == "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        obj_end = i + 1
                        break

            obj_content = content[obj_start:obj_end]
            methods = self._METHOD_PATTERN.findall(obj_content)

            if methods:
                endpoint = {
                    "path": path,
                    "methods": {
                        method: {"description": f"{method} {path}", "method": method}
                        for method in methods
                    },
                }
                endpoints.append(endpoint)

        return (
            [{"children": endpoints, "path": "/", "text": "root"}] if endpoints else []
        )

    def flatten_api_endpoints(
        self, schema: List[Dict[str, Any]], parent_path: str = ""
    ) -> List[Dict[str, Any]]:
        """Flatten the nested API schema structure."""
        endpoints = []

        for item in schema:
            if not isinstance(item, dict):
                continue

            current_path = parent_path + item.get("path", "")

            # Add current endpoint if it has info (HTTP methods)
            if "info" in item and item["info"]:
                endpoint = {
                    "path": current_path,
                    "methods": item["info"],
                    "text": item.get("text", ""),
                    "leaf": item.get("leaf", 0),
                }
                endpoints.append(endpoint)

            # Check for methods directly in the item
            method_keys = {"GET", "POST", "PUT", "DELETE", "PATCH"}
            direct_methods = {k: v for k, v in item.items() if k in method_keys}
            if direct_methods:
                endpoint = {
                    "path": current_path,
                    "methods": direct_methods,
                    "text": item.get("text", ""),
                    "leaf": item.get("leaf", 0),
                }
                endpoints.append(endpoint)

            # Recursively process children
            if "children" in item and item["children"]:
                child_endpoints = self.flatten_api_endpoints(
                    item["children"], current_path
                )
                endpoints.extend(child_endpoints)

        return endpoints

    def create_openapi_spec(self, endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create the complete OpenAPI specification with standardized components."""
        paths = {}

        for endpoint in endpoints:
            if not endpoint.get("methods"):
                continue

            path = endpoint["path"]
            path_item = self._convert_endpoint_to_openapi(endpoint)

            if path_item:
                paths[path] = path_item

        # Get unique tags
        tags = set()
        for endpoint in endpoints:
            if endpoint.get("methods"):
                tag = self._determine_tag(endpoint["path"])
                tags.add(tag)

        # Build standardized OpenAPI specification
        spec = {
            "openapi": "3.0.3",
            "info": self._build_standardized_info(),
            "servers": self._build_standardized_servers(),
            "tags": [
                {"name": tag, "description": f"{tag.title()} related operations"}
                for tag in sorted(tags)
            ],
            "paths": paths,
            "components": self._build_standardized_components(),
        }

        # Add standardized security
        if self.config.security_patterns:
            spec["security"] = self.config.security_patterns

        return spec

    def _build_standardized_info(self) -> Dict[str, Any]:
        """Build standardized info section based on completed template."""
        return {
            "title": self.config.title,
            "description": self.config.description,
            "version": self.config.version,
            "contact": {
                "name": "Proxmox Support",
                "url": "https://www.proxmox.com",
                "email": self.config.contact_email,
            },
            "license": {
                "name": "AGPL-3.0",
                "url": "https://www.gnu.org/licenses/agpl-3.0.html",
            },
        }

    def _build_standardized_servers(self) -> List[Dict[str, Any]]:
        """Build standardized server configuration using {host} variable."""
        api_name = (
            "Proxmox VE Server"
            if self.config.api_type == ProxmoxAPI.PVE
            else "Proxmox Backup Server"
        )

        return [
            {
                "url": f"https://{{host}}:{self.config.default_port}{self.config.server_path}",
                "description": api_name,
                "variables": {
                    "host": {
                        "default": "localhost",
                        "description": f"{api_name.split()[0]} {api_name.split()[1]} server hostname or IP address",
                    }
                },
            }
        ]

    def _build_standardized_components(self) -> Dict[str, Any]:
        """Build standardized components with unified security schemes and error schemas."""
        components = {
            "securitySchemes": self.config.auth_schemes,
            "schemas": self._get_standardized_schemas(),
        }

        return components

    def _get_standardized_schemas(self) -> Dict[str, Any]:
        """Get standardized schemas including error components and common data patterns."""
        schemas = {
            # Standard response schemas
            "ProxmoxError": {
                "type": "object",
                "description": "Standard Proxmox API error response",
                "properties": {
                    "data": {
                        "type": "object",
                        "nullable": True,
                        "description": "Additional error context data",
                    },
                    "errors": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Detailed error messages keyed by field or error type",
                    },
                    "message": {
                        "type": "string",
                        "description": "Human-readable error message",
                    },
                },
            },
            "ProxmoxTask": {
                "type": "object",
                "description": "Proxmox async task response",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "Task ID for tracking async operations",
                        "pattern": "^UPID:[^:]+:[0-9A-F]+:[^:]*:[^:]+:[^:]*:[^:]*:$",
                    }
                },
                "required": ["data"],
            },
            "ProxmoxSuccess": {
                "type": "object",
                "description": "Standard success response",
                "properties": {
                    "data": {"description": "Response data (varies by endpoint)"},
                    "success": {
                        "type": "boolean",
                        "description": "Operation success indicator",
                    },
                },
            },
            # Common identifier schemas
            "ProxmoxNodeId": {
                "type": "string",
                "description": "Proxmox node identifier following DNS hostname standards",
                "pattern": "^[a-zA-Z0-9]([a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?$",
                "minLength": 1,
                "maxLength": 63,
                "example": "pve-node-01",
            },
            "ProxmoxVmId": {
                "type": "integer",
                "description": "Virtual machine or container ID",
                "minimum": 1,
                "maximum": 999999999,
                "example": 100,
            },
            "ProxmoxStorageId": {
                "type": "string",
                "description": "Storage identifier",
                "pattern": "^[A-Za-z][A-Za-z0-9\\-\\_]+$",
                "minLength": 1,
                "maxLength": 64,
                "example": "local-lvm",
            },
            "ProxmoxEmail": {
                "type": "string",
                "description": "Email address format",
                "pattern": "^[^@]+@[^@]+$",
                "format": "email",
                "example": "admin@example.com",
            },
            "ProxmoxUserId": {
                "type": "string",
                "description": "User ID in format user@realm",
                "pattern": "^[^@]+@[^@]+$",
                "example": "admin@pve",
            },
            "ProxmoxResourceName": {
                "type": "string",
                "description": "General resource name following Proxmox naming conventions",
                "pattern": "^[A-Za-z0-9_][A-Za-z0-9._\\-]*$",
                "minLength": 1,
                "maxLength": 64,
                "example": "my-resource",
            },
        }

        # Add PBS-specific schemas if this is a PBS API
        if self.config.api_type == ProxmoxAPI.PBS:
            schemas.update(
                {
                    "ProxmoxSha256": {
                        "type": "string",
                        "description": "SHA256 hash for backup integrity verification",
                        "pattern": "^[a-f0-9]{64}$",
                        "minLength": 64,
                        "maxLength": 64,
                        "example": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    },
                    "ProxmoxBackupId": {
                        "type": "string",
                        "description": "Backup ID following PBS naming conventions",
                        "pattern": "^(?:[A-Za-z0-9_][A-Za-z0-9._\\-]*)$",
                        "example": "vm-100-disk-0",
                    },
                    "ProxmoxDatastoreName": {
                        "type": "string",
                        "description": "Datastore name in PBS",
                        "pattern": "^[A-Za-z0-9_][A-Za-z0-9._\\-]*$",
                        "minLength": 1,
                        "maxLength": 32,
                        "example": "backup-storage",
                    },
                }
            )

        return schemas

    def _get_standardized_error_responses(self) -> Dict[str, Any]:
        """Get standardized HTTP error responses."""
        return {
            "400": {
                "description": "Bad Request - Invalid input parameters or malformed request",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ProxmoxError"}
                    }
                },
            },
            "401": {
                "description": "Unauthorized - Authentication required or invalid credentials",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ProxmoxError"}
                    }
                },
            },
            "403": {
                "description": "Forbidden - Insufficient permissions for the requested operation",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ProxmoxError"}
                    }
                },
            },
            "404": {
                "description": "Not Found - Requested resource does not exist",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ProxmoxError"}
                    }
                },
            },
            "422": {
                "description": "Unprocessable Entity - Request is well-formed but contains semantic errors",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ProxmoxError"}
                    }
                },
            },
            "500": {
                "description": "Internal Server Error - Unexpected server error",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ProxmoxError"}
                    }
                },
            },
            "503": {
                "description": "Service Unavailable - Service temporarily unavailable",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ProxmoxError"}
                    }
                },
            },
        }

    def _convert_endpoint_to_openapi(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a Proxmox endpoint to OpenAPI path item with standardized responses."""
        path_item = {}

        for method, method_info in endpoint["methods"].items():
            if not isinstance(method_info, dict):
                continue

            operation = {
                "summary": method_info.get(
                    "description", f'{method} {endpoint["path"]}'
                ),
                "description": method_info.get("description", ""),
                "operationId": f"{method.lower()}_{endpoint['path'].replace('/', '_').replace('{', '').replace('}', '').strip('_')}",
                "tags": [self._determine_tag(endpoint["path"])],
            }

            # Add parameters
            parameters = []

            # Path parameters
            path_params = self._PATH_PARAMS_PATTERN.findall(endpoint["path"])
            for param in path_params:
                parameters.append(
                    {
                        "name": param,
                        "in": "path",
                        "required": True,
                        "schema": self._get_path_param_schema(param),
                        "description": f"The {param} parameter",
                    }
                )

            # Query/body parameters
            if "parameters" in method_info and method_info["parameters"]:
                param_schema = self._convert_parameters_to_openapi(
                    method_info["parameters"]
                )

                if method.upper() in ["GET", "DELETE"]:
                    # Add query parameters
                    if param_schema.get("properties"):
                        for param_name, param_def in param_schema["properties"].items():
                            if param_name not in path_params:
                                param_obj = {
                                    "name": param_name,
                                    "in": "query",
                                    "required": param_name
                                    in param_schema.get("required", []),
                                    "schema": param_def,
                                }
                                if "description" in param_def:
                                    param_obj["description"] = param_def["description"]
                                parameters.append(param_obj)
                else:
                    # Add request body for POST/PUT methods
                    if param_schema.get("properties"):
                        body_properties = {
                            k: v
                            for k, v in param_schema["properties"].items()
                            if k not in path_params
                        }
                        body_required = [
                            r
                            for r in param_schema.get("required", [])
                            if r not in path_params
                        ]

                        if body_properties:
                            body_schema = {
                                "type": "object",
                                "properties": body_properties,
                            }
                            if body_required:
                                body_schema["required"] = body_required

                            operation["requestBody"] = {
                                "required": bool(body_required),
                                "content": {
                                    "application/json": {"schema": body_schema}
                                },
                            }

            if parameters:
                operation["parameters"] = parameters

            # Add standardized responses
            operation["responses"] = self._build_operation_responses(method_info)

            # Add standardized security
            if self.config.security_patterns:
                operation["security"] = self.config.security_patterns

            path_item[method.lower()] = operation

        return path_item

    def _build_operation_responses(self, method_info: Dict[str, Any]) -> Dict[str, Any]:
        """Build standardized responses for an operation."""
        responses = {}

        # Success response
        if "returns" in method_info and method_info["returns"]:
            returns_info = method_info["returns"]
            if isinstance(returns_info, dict):
                response_schema = self._convert_returns_to_openapi_schema(returns_info)
                responses["200"] = {
                    "description": returns_info.get(
                        "description", "Successful operation"
                    ),
                    "content": {"application/json": {"schema": response_schema}},
                }
        else:
            responses["200"] = {
                "description": "Successful operation",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/ProxmoxSuccess"}
                    }
                },
            }

        # Add standardized error responses
        responses.update(self._get_standardized_error_responses())

        return responses

    def _get_path_param_schema(self, param_name: str) -> Dict[str, Any]:
        """Get appropriate schema for path parameters using standardized schemas."""
        # Map common path parameters to standardized schema references
        if param_name in ["vmid", "ctid"]:
            return {"$ref": "#/components/schemas/ProxmoxVmId"}
        elif param_name == "node":
            return {"$ref": "#/components/schemas/ProxmoxNodeId"}
        elif param_name == "storage":
            return {"$ref": "#/components/schemas/ProxmoxStorageId"}
        elif param_name == "userid":
            return {"$ref": "#/components/schemas/ProxmoxUserId"}
        elif (
            param_name in ["datastore", "store"]
            and self.config.api_type == ProxmoxAPI.PBS
        ):
            return {"$ref": "#/components/schemas/ProxmoxDatastoreName"}
        elif (
            param_name in ["backup-id", "backup_id"]
            and self.config.api_type == ProxmoxAPI.PBS
        ):
            return {"$ref": "#/components/schemas/ProxmoxBackupId"}
        elif (
            param_name in ["digest", "checksum"]
            and self.config.api_type == ProxmoxAPI.PBS
        ):
            return {"$ref": "#/components/schemas/ProxmoxSha256"}
        # Common resource names
        elif param_name in ["poolid", "realm", "group", "role"]:
            return {"$ref": "#/components/schemas/ProxmoxResourceName"}
        else:
            # Fallback to basic string type with description
            return {"type": "string", "description": f"The {param_name} parameter"}

    def _convert_parameters_to_openapi(self, pbs_params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert parameter definitions to OpenAPI parameters."""
        if (
            not pbs_params
            or not isinstance(pbs_params, dict)
            or "properties" not in pbs_params
        ):
            return {"type": "object", "properties": {}}

        properties = {}
        required = []

        for param_name, param_info in pbs_params["properties"].items():
            if not isinstance(param_info, dict):
                continue

            param_schema = self._build_param_schema(param_name, param_info)
            properties[param_name] = param_schema

            # Add to required if not optional
            if not param_info.get("optional", False):
                required.append(param_name)

        result = {"type": "object", "properties": properties}

        if required:
            result["required"] = required

        return result

    def _build_param_schema(self, param_name: str, param_info: Dict[str, Any]) -> Dict[str, Any]:
        """Build schema for a single parameter."""
        param_schema = self._convert_type_to_openapi(
            param_info.get("type", "string"),
            param_info.get("format") if param_info.get("format") else None,
            param_info,
        )

        # Add description
        if "description" in param_info:
            param_schema["description"] = param_info["description"]

        # Add constraints
        self._add_param_constraints(param_schema, param_info)

        # Handle pattern safely
        self._add_param_pattern(param_schema, param_info)

        # Handle enums
        if "enum" in param_info and isinstance(param_info["enum"], list):
            param_schema["enum"] = param_info["enum"]

        # Handle default values
        if "default" in param_info:
            param_schema["default"] = param_info["default"]

        # Handle array items
        self._add_array_items(param_schema, param_info)

        return param_schema

    def _add_param_constraints(self, param_schema: Dict[str, Any], param_info: Dict[str, Any]) -> None:
        """Add parameter constraints to schema."""
        for constraint in ["minLength", "maxLength", "minimum", "maximum"]:
            if constraint in param_info:
                try:
                    param_schema[constraint] = param_info[constraint]
                except (ValueError, TypeError):
                    pass

    def _add_param_pattern(self, param_schema: Dict[str, Any], param_info: Dict[str, Any]) -> None:
        """Add pattern constraint to schema."""
        if "pattern" in param_info:
            pattern = param_info["pattern"]
            if isinstance(pattern, str):
                if pattern.startswith("/") and pattern.endswith("/"):
                    pattern = pattern[1:-1]
                elif pattern.startswith('"/') and pattern.endswith('/"'):
                    pattern = pattern[2:-2]
                try:
                    re.compile(pattern)
                    param_schema["pattern"] = pattern
                except re.error:
                    pass

    def _add_array_items(self, param_schema: Dict[str, Any], param_info: Dict[str, Any]) -> None:
        """Add array items schema."""
        if param_info.get("type") == "array" and "items" in param_info:
            items_info = param_info["items"]
            if isinstance(items_info, dict):
                param_schema["items"] = self._convert_type_to_openapi(
                    items_info.get("type", "string"),
                    items_info.get("format") if items_info.get("format") else None,
                    items_info,
                )

    def _convert_type_to_openapi(
        self,
        pbs_type: str,
        format_hint: Optional[str] = None,
        param_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Convert type definitions to OpenAPI schema types, using standardized schemas where possible."""
        # Check if we can use a standardized schema reference
        if param_info:
            standardized_ref = self._get_standardized_schema_ref(param_info)
            if standardized_ref:
                return standardized_ref

        type_mapping = {
            "string": {"type": "string"},
            "integer": {"type": "integer"},
            "number": {"type": "number"},
            "boolean": {"type": "boolean"},
            "array": {"type": "array"},
            "object": {"type": "object"},
            "null": {"type": "null"},
        }

        if pbs_type in type_mapping:
            schema = type_mapping[pbs_type].copy()
            if format_hint:
                schema["format"] = format_hint
            return schema

        return {"type": "string", "description": f"Type: {pbs_type}"}

    def _get_standardized_schema_ref(self, param_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get standardized schema reference if parameter matches common patterns."""
        param_type = param_info.get("type", "string")
        pattern = param_info.get("pattern", "")
        description = param_info.get("description", "").lower()

        # Node identifier pattern
        if pattern == "^[a-zA-Z0-9]([a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?$":
            return {"$ref": "#/components/schemas/ProxmoxNodeId"}

        # Email pattern
        if pattern == "^[^@]+@[^@]+$":
            if "user" in description or "email" in description:
                return (
                    {"$ref": "#/components/schemas/ProxmoxUserId"}
                    if "user" in description
                    else {"$ref": "#/components/schemas/ProxmoxEmail"}
                )

        # VM ID pattern
        if (
            param_type == "integer"
            and param_info.get("minimum") == 1
            and param_info.get("maximum", 0) > 100000
        ):
            return {"$ref": "#/components/schemas/ProxmoxVmId"}

        # SHA256 pattern (PBS specific)
        if pattern == "^[a-f0-9]{64}$" and self.config.api_type == ProxmoxAPI.PBS:
            return {"$ref": "#/components/schemas/ProxmoxSha256"}

        # Resource name patterns
        if pattern in [
            "^[A-Za-z0-9_][A-Za-z0-9._\\-]*$",
            "^(?:[A-Za-z0-9_][A-Za-z0-9._\\-]*)$",
        ]:
            if self.config.api_type == ProxmoxAPI.PBS and (
                "datastore" in description or "store" in description
            ):
                return {"$ref": "#/components/schemas/ProxmoxDatastoreName"}
            elif self.config.api_type == ProxmoxAPI.PBS and "backup" in description:
                return {"$ref": "#/components/schemas/ProxmoxBackupId"}
            elif "storage" in description:
                return {"$ref": "#/components/schemas/ProxmoxStorageId"}
            else:
                return {"$ref": "#/components/schemas/ProxmoxResourceName"}

        return {}

    def _convert_returns_to_openapi_schema(self, returns_info: Dict[str, Any]) -> Dict[str, Any]:
        """Convert returns definition to OpenAPI schema."""
        if not isinstance(returns_info, dict):
            return {"type": "string"}

        schema = self._convert_type_to_openapi(
            returns_info.get("type", "object"),
            returns_info.get("format") if returns_info.get("format") else None,
            returns_info,
        )

        # Handle array returns
        if returns_info.get("type") == "array" and "items" in returns_info:
            items_info = returns_info["items"]
            if isinstance(items_info, dict):
                schema["items"] = self._convert_returns_to_openapi_schema(items_info)

        # Handle object properties
        if returns_info.get("type") == "object" and "properties" in returns_info:
            properties = {}
            for prop_name, prop_info in returns_info["properties"].items():
                if isinstance(prop_info, dict):
                    properties[prop_name] = self._convert_returns_to_openapi_schema(
                        prop_info
                    )
            if properties:
                schema["properties"] = properties

        # Add description
        if "description" in returns_info:
            schema["description"] = returns_info["description"]

        return schema

    def _determine_tag(self, path: str) -> str:
        """Determine the OpenAPI tag from the path."""
        parts = path.strip("/").split("/")
        if len(parts) > 0 and parts[0]:
            return self.config.tag_mapping.get(parts[0], parts[0].title())
        return "Default"


def get_pve_config() -> APIConfig:
    """Get standardized configuration for PVE API."""
    return APIConfig(
        api_type=ProxmoxAPI.PVE,
        title="Proxmox VE API",
        description="""Complete Proxmox Virtual Environment API specification for managing virtualized infrastructure.

This specification covers all aspects of Proxmox VE management including:
- **Virtual Machine Management**: Create, configure, and manage VMs
- **Container Management**: LXC container lifecycle management
- **Storage Management**: Configure and manage storage backends
- **Network Configuration**: Virtual networks and firewall rules
- **Cluster Operations**: Multi-node cluster management
- **User Management**: Authentication, authorization, and access control
- **Backup & Restore**: Data protection and recovery
- **Monitoring**: System status and performance metrics

The API supports both token-based authentication and session-based authentication with CSRF protection.""",
        version="8.0.0",
        default_port=8006,
        server_path="/api2/json",
        auth_schemes={
            "ProxmoxApiToken": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "API token authentication. Format: PVEAPIToken=USER@REALM!TOKENID=UUID",
            },
            "ProxmoxSessionCookie": {
                "type": "apiKey",
                "in": "cookie",
                "name": "PVEAuthCookie",
                "description": "Session cookie authentication obtained from /access/ticket",
            },
            "ProxmoxCSRFToken": {
                "type": "apiKey",
                "in": "header",
                "name": "CSRFPreventionToken",
                "description": "CSRF prevention token required for state-changing operations when using cookie auth",
            },
        },
        tag_mapping={
            "nodes": "Nodes",
            "cluster": "Cluster",
            "access": "Access Control",
            "storage": "Storage",
            "pools": "Resource Pools",
            "version": "System Info",
        },
        contact_email="support@proxmox.com",
        security_patterns=[
            {"ProxmoxApiToken": []},
            {"ProxmoxSessionCookie": [], "ProxmoxCSRFToken": []},
        ],
        enable_session_auth=True,
    )


def get_pbs_config() -> APIConfig:
    """Get standardized configuration for PBS API."""
    return APIConfig(
        api_type=ProxmoxAPI.PBS,
        title="Proxmox Backup Server API",
        description="""Complete Proxmox Backup Server API specification for comprehensive data protection and backup management.

This specification covers all aspects of Proxmox Backup Server operations including:
- **Backup Operations**: Create, manage, and monitor backup jobs
- **Data Store Management**: Configure and manage backup storage
- **Access Control**: User authentication and authorization
- **Sync & Replication**: Cross-site backup synchronization
- **Prune & GC**: Automated cleanup and garbage collection
- **Encryption**: Client-side encryption and key management
- **Monitoring**: Backup status and performance tracking
- **Configuration**: Server and client configuration management

The API supports token-based authentication with CSRF protection for secure backup operations.""",
        version="3.0.0",
        default_port=8007,
        server_path="",
        auth_schemes={
            "ProxmoxApiToken": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "API token authentication. Format: PBSAPIToken=USER@REALM!TOKENID=UUID",
            },
            "ProxmoxCSRFToken": {
                "type": "apiKey",
                "in": "header",
                "name": "CSRFPreventionToken",
                "description": "CSRF prevention token required for state-changing operations",
            },
        },
        tag_mapping={
            "access": "Access Control",
            "admin": "Administration",
            "backup": "Backup Operations",
            "config": "Configuration",
            "datastore": "Data Store Management",
            "status": "Status & Monitoring",
        },
        contact_email="support@proxmox.com",
        security_patterns=[{"ProxmoxApiToken": [], "ProxmoxCSRFToken": []}],
        enable_session_auth=False,
    )


def main() -> int:
    """Main function to parse API and generate OpenAPI spec."""
    if len(sys.argv) < 4:
        print("Usage: python unified_parser.py <api_type> <input_js_file> <output_dir>")
        print("  api_type: 'pve' or 'pbs'")
        print("  input_js_file: path to apidoc.js file")
        print("  output_dir: directory to write output files")
        return 1

    api_type_str = sys.argv[1].lower()
    js_file_path = sys.argv[2]
    output_dir = sys.argv[3]

    if api_type_str not in ["pve", "pbs"]:
        print("Error: api_type must be 'pve' or 'pbs'")
        return 1

    if not os.path.exists(js_file_path):
        print(f"Error: Could not find input file {js_file_path}")
        return 1

    # Get configuration
    config = get_pve_config() if api_type_str == "pve" else get_pbs_config()
    parser = UnifiedProxmoxParser(config)

    try:
        print(f"Extracting API schema from {js_file_path}...")
        schema = parser.extract_api_schema(js_file_path)

        print("Flattening API endpoints...")
        endpoints = parser.flatten_api_endpoints(schema)
        print(f"Found {len(endpoints)} endpoints")

        print("Creating OpenAPI specification...")
        openapi_spec = parser.create_openapi_spec(endpoints)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Write JSON file
        json_file = os.path.join(output_dir, f"{api_type_str}-api.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

        print(f"OpenAPI JSON specification written to: {json_file}")

        # Also write YAML file if PyYAML is available
        try:
            import yaml

            yaml_file = os.path.join(output_dir, f"{api_type_str}-api.yaml")
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(openapi_spec, f, default_flow_style=False, allow_unicode=True)
            print(f"OpenAPI YAML specification written to: {yaml_file}")
        except ImportError:
            print(
                "PyYAML not installed, skipping YAML output. Install with: pip install PyYAML"
            )

        print("\nSummary:")
        print(f"- Total endpoints: {len(endpoints)}")
        print(f"- Total paths: {len(openapi_spec['paths'])}")

        # Count operations
        total_operations = 0
        for path_item in openapi_spec["paths"].values():
            total_operations += len(
                [
                    k
                    for k in path_item.keys()
                    if k in ["get", "post", "put", "delete", "patch"]
                ]
            )

        print(f"- Total operations: {total_operations}")
        print(f"- Tags: {len(openapi_spec['tags'])}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
