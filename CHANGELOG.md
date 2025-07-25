# Changelog

All notable changes to the Proxmox OpenAPI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI/CD Pipeline Enhancement (ROADMAP v1.1 feature completed)
  - Automatic PR creation for API specification updates
  - Performance metrics tracking for generation times
  - GitHub Issues creation on workflow failures
  - Parallel processing workflow for improved performance
  - Detailed change summaries with endpoint diffs
  - Configurable PR creation for manual runs

## [1.1.1] - 2025-07-25

### Added
- Comprehensive ROADMAP.md with feature tracking and implementation plans
- Enhanced Renovate configuration for better dependency management
  - Semantic commits and dependency dashboard
  - Automerge for dev dependencies and GitHub Actions
  - Vulnerability alerts with security labels

### Changed
- Updated README.md to reference new ROADMAP document
- Corrected CHANGELOG dates to match actual repository history

### Removed
- Removed all Dagger references and implementation strategy
- Simplified containerization approach to use Docker/Docker Compose

## [1.1.0] - 2025-07-25

### Added
- Claude AI development configuration (.claude directory)
- MCP (Model Context Protocol) server integrations for enhanced development
- Serena project configuration
- Pre/post tool use hooks for enhanced safety and efficiency
- Performance guide documentation (docs/performance-guide.md)
- Infisical configuration for secret management
- Environment configuration (.envrc) for GitHub token management

### Changed
- Updated Python dependency to version 3.13
- Updated devcontainer to mcr.microsoft.com/devcontainers/universal:v3
- Enhanced devcontainer with modern tooling and VS Code extensions
- Simplified CI/CD workflow and fixed validation errors
- Refactored scripts to output directly to target directories

### Fixed
- Fixed null type handling in parser with clarifying documentation
- Regenerated API specifications with validation fixes
- Cleaned up development artifacts and duplicate files

## [1.0.0] - 2025-06-11

### Added
- Unified parser for both PVE and PBS APIs with file caching (40-60% performance improvement)
- Regex pattern pre-compilation (10-20% performance improvement)
- Comprehensive OpenAPI 3.0.3 specification generation
- Support for Proxmox Virtual Environment (PVE) API
- Support for Proxmox Backup Server (PBS) API
- JSON and YAML output formats
- Automated validation with openapi-spec-validator
- GitHub Actions workflow for weekly automated updates
- Detailed documentation and performance tracking

### Technical Details
- PVE API: ~385 endpoints, ~687 operations, 3.8MB JSON output
- PBS API: ~233 endpoints, ~348 operations, 1.1MB JSON output
- Python 3.9+ with UV package manager
- Ruff for code formatting and linting
- MyPy for type checking

[Unreleased]: https://github.com/basher83/Proxmox-OpenAPI/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/basher83/Proxmox-OpenAPI/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/basher83/Proxmox-OpenAPI/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/basher83/Proxmox-OpenAPI/releases/tag/v1.0.0