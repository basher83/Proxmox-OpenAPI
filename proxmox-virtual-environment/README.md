# Proxmox VE API OpenAPI Specification

> 📖 **Main Documentation**: See the [main README](../README.md) for complete project overview and both PVE/PBS specifications.

This directory contains a complete OpenAPI 3.0.3 specification for the Proxmox Virtual Environment API, automatically generated from the official Proxmox API documentation.

## 📊 Specification Overview

- **Total Endpoints**: 385 unique API paths
- **Total Operations**: 687 HTTP operations (GET, POST, PUT, DELETE)
- **OpenAPI Version**: 3.0.3
- **Generated From**: Proxmox VE API Viewer documentation
- **Available Formats**: JSON and YAML

## 📄 Available Files

### **Primary Specifications**

- `pve-api.json` - **1.8MB** comprehensive JSON specification
- `pve-api.yaml` - **1.2MB** comprehensive YAML specification

### **Generation Scripts**

- `generate_openapi.py` - Main OpenAPI specification generator
- `convert_to_yaml.py` - JSON to YAML converter
- Various analysis and parsing scripts

## Roadmap

- [ ] **Direct API Fetching** - Pull from [PVE API Viewer](https://pve.proxmox.com/pve-docs/api-viewer/index.html) instead of working from downloaded files
- [ ] **Unified Parser Framework** - Use standardized `generate_openapi.py` across both APIs to reduce code duplication
- [ ] **Enhanced Validation** - More comprehensive OpenAPI spec validation
- [ ] **Client Libraries** - Pre-generated clients in multiple languages

## 🎯 Coverage

The specification covers all aspects of Proxmox VE management:

- **Virtual Machine Management**: Create, configure, and manage VMs
- **Container Management**: LXC container lifecycle management
- **Storage Management**: Configure and manage storage backends
- **Network Configuration**: Virtual networks and firewall rules
- **Cluster Operations**: Multi-node cluster management
- **User Management**: Authentication, authorization, and access control
- **Backup & Restore**: Data protection and recovery
- **Monitoring**: System status and performance metrics

## 📈 Statistics by Category

| Category       | Operations |
| -------------- | ---------- |
| Nodes          | 394        |
| Cluster        | 226        |
| Access Control | 58         |
| Resource Pools | 5          |
| Storage        | 4          |

## 🔧 HTTP Methods Distribution

| Method | Count |
| ------ | ----- |
| GET    | 338   |
| DELETE | 139   |
| POST   | 163   |
| PUT    | 47    |

## 🔑 Authentication

The API supports multiple authentication methods:

- **API Token Authentication**: `PVEAPIToken=USER@REALM!TOKENID=UUID`
- **Session Cookie**: Obtained via `/access/ticket` endpoint
- **CSRF Protection**: Required for state-changing operations

## 🚀 Usage

### JSON Format

```bash
# Use the JSON specification
curl -H "Content-Type: application/json" \
     -d @pve-api.json \
     https://editor.swagger.io
```

### YAML Format

```bash
# Use the YAML specification (more readable)
cat pve-api.yaml
```

### Code Generation

```bash
# Generate client code using OpenAPI Generator
openapi-generator-cli generate \
  -i pve-api.yaml \
  -g python \
  -o ./proxmox-client
```

## 🔄 File Formats Comparison

| Format | Size  | Readability      | Usage                      |
| ------ | ----- | ---------------- | -------------------------- |
| JSON   | 1.8MB | Machine-friendly | API tools, code generation |
| YAML   | 1.2MB | Human-friendly   | Documentation, editing     |

## 🛠️ Development

### Requirements

- Python 3.8+
- [UV](https://github.com/astral-sh/uv) (recommended) or PyYAML for YAML conversion

### Generate New Specification

```bash
cd scripts/pve
python3 generate_openapi.py
python3 convert_to_yaml.py
# Files will be generated as pve-api.json and pve-api.yaml
```

## 📝 License

This specification is generated from official Proxmox VE documentation and follows the same licensing terms.

## 🤝 Contributing

1. Ensure compatibility with official Proxmox VE API
2. Validate against MCP specification
3. Test both JSON and YAML formats
4. Update verification documentation

## Sources

[PBS API Viewer](https://pbs.proxmox.com/docs/api-viewer/index.html)
[PVE API Viewer](https://pve.proxmox.com/pve-docs/api-viewer/index.html)

---

**Generated**: 2025-06-10  
**Proxmox Version**: 8.0.0  
**Specification Status**: ✅ Production Ready
