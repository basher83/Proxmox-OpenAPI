# Proxmox OpenAPI Project Roadmap

## Overview

This document tracks the development roadmap for the Proxmox OpenAPI specifications generator. Features are organized by priority and implementation complexity.

**Last Updated**: 2025-07-25  
**Status Legend**: ✅ Complete | ⚠️ In Progress | ❌ Not Started | 🚧 Blocked

---

## Current Status Summary

| Feature | Status | Priority | Target Release |
|---------|--------|----------|----------------|
| Unified Parser Framework | ✅ | High | v1.0 (Released) |
| CI/CD Pipeline | ⚠️ | High | v1.1 |
| Direct API Fetching | ❌ | Medium | v1.2 |
| Enhanced Validation | ❌ | Medium | v1.1 |
| Client Libraries | ❌ | Low | v1.3 |
| Docker Images | ❌ | Medium | v1.2 |

---

## Feature Details

### 1. Unified Parser Framework ✅

**Status**: Implemented in v1.0  
**Description**: Central parsing engine for both PVE and PBS APIs

#### Current Implementation

- ✅ Unified parser with file caching
- ✅ orjson optimization for performance
- ✅ Configuration-driven approach via APIConfig dataclass
- ✅ Standardized authentication schemes
- ✅ Consistent error handling

#### Future Enhancements (v1.1)

- [ ] Add streaming parser for large API docs
- [ ] Implement incremental parsing (parse only changed endpoints)
- [ ] Add parser plugins for custom transformations
- [ ] Support for OpenAPI extensions (x-* properties)
- [ ] Better handling of complex nested schemas

**Success Metrics**:

- Parse time < 5 seconds for full API
- Memory usage < 500MB
- 100% compatibility with existing specs

---

### 2. CI/CD Pipeline ⚠️

**Status**: Partially implemented  
**Priority**: High  
**Target**: v1.1 (Q3 2025)

#### Current State

- ✅ Weekly automated runs via GitHub Actions
- ✅ Manual workflow dispatch
- ✅ Basic validation steps
- ❌ No automatic PR creation
- ❌ Read-only permissions (can't commit)
- ❌ No failure notifications

#### Implementation Plan

1. **Phase 1: Auto-commit capability** (2 weeks)
   - [ ] Add write permissions to workflow
   - [ ] Implement git commit automation
   - [ ] Add commit signing

2. **Phase 2: PR Automation** (1 week)
   - [ ] Create PR when specs change
   - [ ] Add diff summary in PR description
   - [ ] Auto-assign reviewers

3. **Phase 3: Enhanced Monitoring** (1 week)
   - [ ] Add Slack/Discord notifications
   - [ ] Implement failure recovery
   - [ ] Add performance metrics tracking

**Success Criteria**:

- Zero manual intervention required
- < 10 minute total pipeline time
- Automatic rollback on validation failure

---

### 3. Direct API Fetching ❌

**Status**: Not started  
**Priority**: Medium  
**Target**: v1.2 (Q4 2025)

#### Objective

Parse API specifications directly from live Proxmox instances instead of downloaded files

#### Implementation Strategy

1. **Discovery Phase** (2 weeks)
   - [ ] Research Proxmox API viewer endpoints
   - [ ] Test authentication methods
   - [ ] Document API versioning approach

2. **Core Implementation** (3 weeks)
   - [ ] Add API client with auth support
   - [ ] Implement streaming fetch
   - [ ] Add version detection
   - [ ] Cache management for API responses

3. **Integration** (1 week)
   - [ ] Update unified parser to accept URLs
   - [ ] Add CLI flags for direct fetch
   - [ ] Update documentation

**Technical Requirements**:

- Support both PVE and PBS endpoints
- Handle SSL certificates properly
- Implement retry logic
- Support proxy configurations

---

### 4. Enhanced Validation ❌

**Status**: Not started  
**Priority**: Medium  
**Target**: v1.1 (Q3 2025)

#### Current Validation

- ✅ Basic OpenAPI 3.0.3 schema validation
- ✅ File size checks
- ❌ No semantic validation
- ❌ No backwards compatibility checks

#### Enhancement Plan

1. **Semantic Validation** (2 weeks)
   - [ ] Validate all $ref references
   - [ ] Check parameter consistency
   - [ ] Verify response schema completeness
   - [ ] Validate example data

2. **Compatibility Checking** (1 week)
   - [ ] Detect breaking changes
   - [ ] Generate compatibility report
   - [ ] Version comparison tools

3. **Quality Metrics** (1 week)
   - [ ] API coverage report
   - [ ] Documentation completeness
   - [ ] Schema complexity analysis

**Deliverables**:

- Comprehensive validation report
- Breaking change detection
- Quality score (0-100)

---

### 5. Client Libraries ❌

**Status**: Not started  
**Priority**: Low  
**Target**: v1.3 (Q1 2026)

#### Planned Languages

1. **Python** (Primary)
   - [ ] Type-safe client with Pydantic
   - [ ] Async/await support
   - [ ] Comprehensive examples

2. **Go** (Secondary)
   - [ ] Generated structs
   - [ ] HTTP client integration
   - [ ] Error handling

3. **TypeScript** (Tertiary)
   - [ ] Full type definitions
   - [ ] React hooks
   - [ ] Node.js and browser support

#### Implementation Approach

- Use OpenAPI Generator
- Custom templates for better ergonomics
- Automated testing against real APIs
- Published to respective package managers

---

### 6. Docker Images ❌

**Status**: Not started  
**Priority**: Medium  
**Target**: v1.2 (Q4 2025)

#### Container Strategy

1. **Base Image** (`proxmox-openapi:latest`)
   - [ ] Python 3.13 + UV
   - [ ] Node.js 20 LTS
   - [ ] All dependencies pre-installed
   - [ ] Multi-arch support (amd64, arm64)

2. **CLI Image** (`proxmox-openapi:cli`)
   - [ ] Minimal runtime
   - [ ] Pre-generated specs included
   - [ ] Auto-update capability

3. **Development Image** (`proxmox-openapi:dev`)
   - [ ] Full development environment
   - [ ] VS Code dev container support
   - [ ] Pre-configured Git hooks

**Usage Examples**:

```bash
# Generate specs
docker run proxmox-openapi generate --api pve

# Validate specs
docker run proxmox-openapi validate /specs/pve-api.yaml

# Development
docker run -it -v $(pwd):/workspace proxmox-openapi:dev
```

---

## Release Timeline

> **Note**: As of July 2025, we are adjusting our timeline to align with current development progress.

### v1.1 - Q3 2025 (Target: September 2025)

- ⚠️ CI/CD Pipeline completion
- ❌ Enhanced Validation
- 🔧 Parser framework improvements

### v1.2 - Q4 2025 (Target: December 2025)

- ❌ Direct API Fetching
- ❌ Docker Images
- 🔧 Performance optimizations

### v1.3 - Q1 2026 (Target: March 2026)

- ❌ Client Libraries (Python, Go, TypeScript)
- 🔧 Documentation improvements
- 🔧 Community contributions

---

## Contributing

To contribute to any of these features:

1. Check the issue tracker for related discussions
2. Comment on the feature you'd like to work on
3. Follow the [contribution guidelines](./docs/GIT_COMMIT_WORKFLOW.md)
4. Submit PRs against the `feature/*` branches

---

## Metrics & Success Criteria

### Performance Targets

- Generation time: < 10s for both APIs
- Memory usage: < 1GB peak
- Docker image size: < 500MB

### Quality Targets

- 100% OpenAPI spec compliance
- Zero validation errors
- > 90% test coverage

### Adoption Targets
>
- > 100 GitHub stars
- > 10 active contributors
- Integration with major Proxmox tools

---

## Dependencies & Blockers

### External Dependencies

- Proxmox API stability
- OpenAPI specification updates
- Container registry availability

### Known Blockers

- GitHub Actions permissions for auto-commit
- Proxmox API authentication for direct fetch
- Package manager accounts for client libraries

---

## Questions or Feedback?

- Open an issue for feature requests
- Join discussions in the issue tracker
- Contact: [basher83](https://github.com/basher83)
