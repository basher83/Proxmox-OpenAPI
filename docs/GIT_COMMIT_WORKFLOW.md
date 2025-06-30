# Git Commit Workflow Rules

This document establishes the comprehensive Git commit workflow for the Proxmox-OpenAPI project, ensuring quality, security, and consistency across all contributions.

## 📋 Overview

Every commit must follow this workflow to maintain code quality, security standards, and clear project history. This combines conventional commits, security validation, atomic changes, and pre-commit quality gates.

## 🔄 Complete Workflow

### 1. Pre-Commit Validation

#### 🧹 Code Quality Checks
```bash
# Run linting
ruff check .

# Run formatting  
black .

# Run type checking
mypy .

# Run tests (if applicable)
pytest
```

#### 🔒 Security Validation (for dependency changes)
```bash
# For Python dependencies
safety check

# Or use MCP security tools for comprehensive scan
# (Recommended for dependency updates)
```

#### 📊 Performance Validation (for perf changes)
- Document before/after metrics
- Include benchmark results in commit message

### 2. Atomic Commit Strategy

#### ✅ One Logical Change Per Commit
- **Good**: `fix(deps): update requests to secure version 2.32.4`
- **Bad**: `fix(deps): update requests and add new API feature`

#### 📂 Separate Commits By Type
1. **Dependencies**: `fix(deps)` or `chore(deps)`
2. **Features**: `feat(scope)`
3. **Bug fixes**: `fix(scope)`
4. **Documentation**: `docs(scope)`
5. **Refactoring**: `refactor(scope)`
6. **Tests**: `test(scope)`

### 3. Commit Message Format

#### 🎯 Use Project Template
The project includes a `.gitmessage` template. Git is configured to use it automatically:

```bash
# Check if template exists
ls -la .gitmessage

# Commit (opens editor with template)
git commit
```

#### 📝 Conventional Commits Structure
```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 🏷️ Commit Types
| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(api): add PVE 8.0 endpoint support` |
| `fix` | Bug fix | `fix(parser): handle missing schema fields` |
| `docs` | Documentation | `docs: update installation guide` |
| `style` | Code formatting | `style: apply black formatting` |
| `refactor` | Code restructuring | `refactor(utils): extract common functions` |
| `perf` | Performance improvement | `perf(parser): optimize regex compilation` |
| `test` | Test additions/fixes | `test(api): add validation test cases` |
| `chore` | Build/tooling | `chore(deps): update development dependencies` |
| `ci` | CI/CD changes | `ci: add security scanning workflow` |
| `build` | Build system | `build: update packaging configuration` |
| `revert` | Revert previous commit | `revert: undo API breaking change` |

#### 🎯 Project-Specific Scopes
| Scope | Description | Example |
|-------|-------------|---------|
| `api` | API related changes | `feat(api): add new endpoint` |
| `pve` | Proxmox VE specific | `fix(pve): correct VM schema` |
| `pbs` | Proxmox Backup Server | `feat(pbs): add datastore API` |
| `spec` | OpenAPI specifications | `docs(spec): update API documentation` |
| `parser` | Parser/generator scripts | `fix(parser): handle edge cases` |
| `schema` | Schema definitions | `feat(schema): add validation rules` |
| `validation` | Validation logic | `test(validation): add schema tests` |
| `deps` | Dependencies | `chore(deps): update security packages` |

### 4. Message Quality Standards

#### 📏 Subject Line Rules
- **Imperative mood**: "Add feature" not "Added feature"
- **No capitalization**: "add feature" not "Add feature"
- **No period**: "add feature" not "add feature."
- **≤50 characters**: Keep it concise
- **Clear and specific**: Describe the change precisely

#### 📄 Body Guidelines
- **Wrap at 72 characters**
- **Explain WHAT and WHY**, not how
- **Use imperative mood**
- **Separate paragraphs with blank lines**
- **Include context for complex changes**

#### 🏁 Footer Requirements
- **Breaking changes**: Start with `BREAKING CHANGE:`
- **Issue references**: `Fixes #123`, `Closes #456`, `Refs #789`
- **Security notes**: `Addresses CVE-2023-XXXX`
- **Performance data**: `Improves performance by 15%`

### 5. Security-Specific Requirements

#### 🛡️ Dependency Security Validation
For all `fix(deps)` or `chore(deps)` commits:

```bash
# Run security scan
safety check

# Document results in commit message
```

**Required in commit message:**
```
fix(deps): update requests to secure version 2.32.4

Update requests from 2.28.0 to 2.32.4 to fix security vulnerabilities.
This addresses known CVEs in the HTTP library that could lead to
request smuggling attacks.

Security validation:
- requests 2.32.4: secure and up to date
- urllib3 2.5.0: secure and up to date
- No known vulnerabilities detected

Fixes #123
```

#### 🚨 Security Fix Format
```
fix(security): patch XSS vulnerability in API response

Sanitize user input in API error messages to prevent XSS attacks.
Input is now properly escaped before inclusion in JSON responses.

BREAKING CHANGE: Error message format has changed
Security: Fixes potential XSS vulnerability
Closes #456
```

### 6. Quality Gates

#### ❌ Commit Blockers
- **Failing tests**: All tests must pass
- **Linting errors**: Code must pass ruff/black checks
- **Security vulnerabilities**: Dependencies must be secure
- **Non-conventional messages**: Must follow template format
- **Mixed changes**: No unrelated changes in single commit

#### ✅ Commit Requirements
- **All validations pass**: Code quality, tests, security
- **Atomic changes**: Single logical modification
- **Conventional format**: Proper type, scope, and structure
- **Clear documentation**: What, why, and impact explained
- **Security validation**: For dependency/security changes

### 7. Examples

#### 🌟 Excellent Commits

```
feat(api): add support for Proxmox VE 8.0 API endpoints

Add new API endpoints for container and VM management introduced
in Proxmox VE 8.0. This includes support for advanced networking
configurations and improved backup scheduling options.

The implementation follows the existing pattern and maintains
backward compatibility with previous API versions.

Fixes #42
```

```
fix(deps): update insecure packages to latest secure versions

- Update orjson from >=3.8.0 to >=3.10.18 (fixes security vulnerabilities)
- Update requests from >=2.28.0 to >=2.32.4 (fixes security vulnerabilities)
- Apply security updates to both enhanced and all dependency groups

Security scan results:
- orjson 3.10.18: secure and up to date
- requests 2.32.4: secure and up to date
- All other dependencies confirmed secure

Addresses multiple CVEs in JSON parsing and HTTP handling.
```

```
perf(parser): optimize regex compilation for 20% performance improvement

Pre-compile frequently used regex patterns instead of compiling
them on each invocation. This reduces parser initialization time
from 150ms to 120ms in benchmarks.

Benchmark results:
- Before: 150ms average initialization
- After: 120ms average initialization  
- Improvement: 20% faster startup time

No functional changes to parsing logic.
```

#### ❌ Poor Commits

```
# Too vague
fix: stuff

# Mixed changes  
feat: add new API and fix dependencies and update docs

# Non-conventional format
Fixed the thing that was broken

# Missing security validation
fix(deps): update packages
```

### 8. Automation Tools

#### 🔧 Recommended Setup
```bash
# Configure git to use the message template
git config commit.template .gitmessage

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

#### 📝 Quick Validation Script
```bash
#!/bin/bash
# validate-commit.sh

echo "🔍 Running pre-commit validation..."

# Code quality
echo "📊 Checking code quality..."
ruff check . || exit 1
black . --check || exit 1

# Tests
echo "🧪 Running tests..."
pytest || exit 1

# Security (for dependency changes)
if git diff --cached --name-only | grep -q "pyproject.toml\|requirements"; then
    echo "🔒 Checking dependency security..."
    safety check || echo "⚠️  Security check recommended for dependency changes"
fi

echo "✅ All validations passed!"
```

### 9. Enforcement

#### 🤖 Automated Checks
- **CI/CD Pipeline**: Validates commit message format
- **GitHub Actions**: Runs security scans on dependency changes
- **Pre-commit Hooks**: Enforces code quality standards

#### 👥 Human Review
- **Pull Request Reviews**: Check adherence to workflow
- **Security Reviews**: Required for security-related commits
- **Architecture Reviews**: Required for significant changes

### 10. Migration Guide

#### 🔄 Adopting These Rules
1. **Review existing commits**: Understand current patterns
2. **Install tools**: Set up linting, formatting, security scanning
3. **Configure git**: Use the `.gitmessage` template
4. **Practice**: Start with small commits following the format
5. **Team training**: Ensure all contributors understand the workflow

#### 📚 Resources
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Security Best Practices](https://owasp.org/www-community/controls/Static_Code_Analysis)
- [Git Best Practices](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project)

---

## 🎯 Quick Reference

### Commit Checklist
- [ ] Code quality checks pass (ruff, black, mypy)
- [ ] Tests pass (if applicable)
- [ ] Security scan complete (for dependency changes)
- [ ] Single logical change (atomic commit)
- [ ] Conventional commit format used
- [ ] Clear subject line (≤50 chars, imperative, no capital/period)
- [ ] Informative body (what/why, wrapped at 72 chars)
- [ ] Appropriate footer (breaking changes, issues, security notes)
- [ ] Security validation documented (for security/dependency changes)

### Command Quick Reference
```bash
# Validate
ruff check . && black . && pytest

# Security check
safety check

# Commit with template
git commit

# Verify
git log --oneline -1
```

This workflow ensures every commit maintains the highest standards of quality, security, and documentation for the Proxmox-OpenAPI project.
