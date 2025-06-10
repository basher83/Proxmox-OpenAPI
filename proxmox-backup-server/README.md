# Proxmox Backup Server API OpenAPI Specification

> 📖 **Main Documentation**: See the [main README](../README.md) for complete project overview and both PVE/PBS specifications.

This directory contains a complete OpenAPI 3.0.3 specification for the Proxmox Backup Server API, automatically generated from the official Proxmox PBS API documentation.

## 📊 Specification Overview

- **Total Endpoints**: 233 unique API paths
- **Total Operations**: 348 HTTP operations (GET, POST, PUT, DELETE)
- **OpenAPI Version**: 3.0.3
- **Generated From**: Proxmox Backup Server API Viewer documentation
- **Available Formats**: JSON and YAML
- **Default Port**: 8007

## 📄 Available Files

### **Primary Specifications**

- `pbs-api.json` - **1.1MB** comprehensive JSON specification
- `pbs-api.yaml` - **821KB** comprehensive YAML specification

### **Generation Scripts**

- `parse_pbs_api_robust.py` - Main robust parser script
- `parse_pbs_api.py` - Alternative parser script
- `convert_to_yaml.py` - JSON to YAML converter

### **Documentation**

- `README.md` - This documentation file

## 🎯 Coverage

The specification covers all aspects of Proxmox Backup Server management:

- **Backup Management**: Create, monitor, and manage backup jobs
- **Datastore Management**: Configure and manage backup storage
- **Access Control**: User authentication and authorization
- **Tape Operations**: Physical tape backup and restore
- **Sync Operations**: Remote synchronization and replication
- **Restore Operations**: Data recovery and file-level restore
- **Administration**: System configuration and monitoring
- **Namespace Management**: Organize backups in hierarchical namespaces

## 📈 Statistics by Category

| Category       | Operations |
| -------------- | ---------- |
| Access Control | ~45        |
| Admin          | ~25        |
| Backup         | ~35        |
| Config         | ~15        |
| Nodes          | ~85        |
| Status         | ~20        |
| Tape           | ~75        |
| Others         | ~48        |

## 🔧 HTTP Methods Distribution

| Method | Count |
| ------ | ----- |
| GET    | ~175  |
| POST   | ~105  |
| PUT    | ~45   |
| DELETE | ~23   |

## 🔑 Authentication

The PBS API supports multiple authentication methods:

- **API Token Authentication**: Header-based token authentication
- **Session Cookie**: Obtained via `/access/ticket` endpoint
- **CSRF Protection**: Required for state-changing operations
- **Role-Based Access**: Granular permissions including:
  - `DatastoreAdmin`, `DatastoreReader`, `DatastoreBackup`
  - `TapeAdmin`, `TapeOperator`, `TapeReader`
  - `RemoteAdmin`, `RemoteSyncOperator`

## 🚀 Usage

### JSON Format

```bash
# Use the JSON specification
curl -H "Content-Type: application/json" \
     -d @pbs-api.json \
     https://editor.swagger.io
```

### YAML Format

```bash
# Use the YAML specification (more readable)
cat pbs-api.yaml
```

### Code Generation

```bash
# Generate client code using OpenAPI Generator
openapi-generator-cli generate \
  -i pbs-api.yaml \
  -g python \
  -o ./pbs-client
```

### Direct API Usage

```bash
# Example: Get PBS version
curl -k -H "Authorization: PBSAPIToken=USER@REALM!TOKENID=UUID" \
     https://your-pbs-server:8007/api2/json/version

# Example: List datastores
curl -k -H "Authorization: PBSAPIToken=USER@REALM!TOKENID=UUID" \
     https://your-pbs-server:8007/api2/json/admin/datastore
```

## 🔄 File Formats Comparison

| Format | Size  | Readability      | Usage                      |
| ------ | ----- | ---------------- | -------------------------- |
| JSON   | 1.1MB | Machine-friendly | API tools, code generation |
| YAML   | 821KB | Human-friendly   | Documentation, editing     |

## 🛠️ Development

### Requirements

- Python 3.8+
- [UV](https://github.com/astral-sh/uv) (recommended) or PyYAML for YAML conversion
- Node.js (optional, for enhanced JavaScript parsing)

### Generate New Specification

```bash
# Run the robust parser
cd scripts/pbs
python3 parse_pbs_api_robust.py

# Convert to YAML (if needed)
python3 convert_to_yaml.py
```

## 🔍 API Tags

The specification organizes endpoints into 13 functional categories:

- **access** - Authentication and user management
- **admin** - Administrative operations
- **backup** - Backup operations and jobs
- **config** - Configuration management
- **nodes** - Node-specific operations
- **status** - System status and monitoring
- **tape** - Tape device and media management
- **ping** - Connectivity testing
- **pull** - Pull-based synchronization
- **push** - Push-based synchronization
- **reader** - Backup reading operations
- **version** - Version information
- **default** - Root-level operations

## 📦 Server Configuration

```yaml
servers:
  - url: https://{server}:8007
    description: Proxmox Backup Server
    variables:
      server:
        default: localhost
        description: PBS hostname or IP address
```

## 📝 License

This specification is generated from official Proxmox Backup Server documentation and follows the same AGPL-3.0 licensing terms.

## 🤝 Contributing

1. Ensure compatibility with official Proxmox Backup Server API
2. Validate OpenAPI specification syntax
3. Test both JSON and YAML formats
4. Update documentation as needed

## 🔗 Related Resources

- [Proxmox Backup Server Documentation](https://pbs.proxmox.com/docs/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Proxmox VE API Specification](../PVE/) - Related PVE API spec

---

**Generated**: 2025-06-10  
**PBS Version**: 3.0.0  
**Specification Status**: ✅ Production Ready
