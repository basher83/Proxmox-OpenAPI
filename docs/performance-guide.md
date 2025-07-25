# Proxmox OpenAPI Performance Guide

## Overview

This guide documents the performance characteristics of the Proxmox OpenAPI parser and tracks optimization efforts. The parser processes large JavaScript API documentation files (3.5MB for PVE, 1.4MB for PBS) to generate OpenAPI specifications.

## Current Performance Metrics

### Baseline Performance

- **PVE API Generation**: ~0.68 seconds (385 endpoints, 687 operations)
- **PBS API Generation**: ~0.47 seconds (233 endpoints, 348 operations)
- **Memory Usage**: ~50-100MB peak
- **File Sizes**:
  - PVE apidoc.js: 3.5MB (59,148 lines)
  - PBS apidoc.js: 1.4MB (28,079 lines)
  - Generated PVE JSON: 3.8MB
  - Generated PBS JSON: 1.1MB

## Implemented Optimizations

### ✅ 1. File Content Caching (40-60% improvement)

**Status**: Implemented in `scripts/unified_parser.py`

The parser caches file contents with modification time checking:

- First run: Normal performance (cache miss)
- Subsequent runs: 40-60% faster (cache hit)
- Automatic invalidation when files change
- Minimal memory overhead (~7MB for both files)

### ✅ 2. Regex Pattern Compilation (10-20% improvement)

**Status**: Implemented in `scripts/unified_parser.py`

All frequently used regex patterns are pre-compiled as class attributes:

```python
_API_SCHEMA_PATTERN = re.compile(r"(var|const|let)\s+apiSchema\s*=\s*\[")
_REGEX_PATTERN = re.compile(r'"/[^"]*/"')
_JS_SINGLE_QUOTE_KEY = re.compile(r"'([^']*)':")
# ... and more
```

### ✅ 3. Code Deduplication (Maintenance improvement)

**Status**: Partially implemented via `unified_parser.py`

The unified parser reduces code duplication between PVE and PBS generators:

- Shared parsing logic
- Configuration-driven differences
- Standardized error handling

## Pending Optimizations

### 🟡 1. String Processing Optimization (5-10% potential)

**Priority**: Medium | **Effort**: Medium

Multiple regex substitutions on large strings could be combined:

- Current: 7+ sequential regex operations
- Proposed: Single-pass processing or combined patterns
- Impact: Reduced string allocations and processing time

### 🟡 2. Subprocess Optimization (5-15% potential)

**Priority**: Low | **Effort**: High

Node.js parsing currently uses temporary files:

- Current: Write to temp file → spawn Node.js → read result
- Proposed: Use stdin/stdout or pure Python parsing
- Impact: Eliminate file I/O and process spawn overhead

### ✅ 3. JSON Serialization with orjson (3% improvement)

**Status**: Implemented in all generators

While orjson provides 96% faster JSON serialization, the overall impact is limited because JSON writing represents only ~3% of total generation time:

- JSON serialization time: ~0.11s → ~0.004s 
- Total generation time: ~3.5s
- Actual improvement: ~3% (0.1s saved)
- Implementation: Automatic fallback to standard json if orjson unavailable

## Performance Testing

### Running Benchmarks

```bash
# Time a single generation
time uv run python scripts/pve/generate_openapi.py

# Test cache effectiveness (run twice)
uv run python scripts/pve/generate_openapi.py && \
time uv run python scripts/pve/generate_openapi.py

# Memory profiling
/usr/bin/time -v uv run python scripts/pve/generate_openapi.py
```

### Validation

Always verify optimizations maintain correctness:

```bash
# Generate before optimization
cp proxmox-virtual-environment/pve-api.json pve-api-before.json

# Apply optimization and regenerate
uv run python scripts/pve/generate_openapi.py

# Compare outputs
diff pve-api-before.json proxmox-virtual-environment/pve-api.json
```

## Memory Optimization Strategies

### Current Memory Usage

- Peak: ~50-100MB
- Dominated by: File content and parsed JSON structures
- Cache overhead: ~7MB per cached file

### Potential Improvements

1. **Streaming Parser**: Process without loading entire file
2. **Incremental Processing**: Only parse changed endpoints
3. **Memory-mapped Files**: For very large inputs

## Best Practices for New Optimizations

1. **Measure First**: Profile before optimizing
2. **Maintain Correctness**: All optimizations must produce identical output
3. **Document Changes**: Update this guide with results
4. **Consider Trade-offs**: Balance speed, memory, and code complexity

## Historical Performance Improvements

| Date | Optimization | Impact | Notes |
|------|--------------|--------|-------|
| 2024 | File Caching | 40-60% faster | Second+ runs only |
| 2024 | Regex Compilation | 10-20% faster | All runs |
| 2024 | Unified Parser | Maintainability | Reduced duplication |
| 2025 | orjson Serialization | ~3% faster | All runs, optional dependency |

## Future Considerations

### Short-term Goals (1-3 months)

- [ ] Implement string processing optimization
- [x] Adopt orjson for JSON serialization ✅
- [ ] Add performance regression tests

### Long-term Vision (6+ months)

- [ ] Pure Python parser (eliminate Node.js dependency)
- [ ] Incremental generation (only changed endpoints)
- [ ] Parallel processing for multiple APIs

## Monitoring and Metrics

### Key Performance Indicators

- Generation time (seconds)
- Memory usage (MB)
- Cache hit rate (%)
- File I/O operations

### CI/CD Integration

Consider adding performance benchmarks to CI:

```yaml
- name: Performance Benchmark
  run: |
    time uv run python scripts/pve/generate_openapi.py
    time uv run python scripts/pbs/generate_openapi.py
```

## Troubleshooting Performance Issues

### Slow Generation

1. Check cache is working: Look for "Using cached content" in logs
2. Verify regex patterns are pre-compiled
3. Monitor disk I/O and CPU usage
4. Check for memory pressure/swapping

### High Memory Usage

1. Clear file cache between runs if needed
2. Consider processing APIs sequentially, not in parallel
3. Monitor for memory leaks in long-running processes

### Cache Misses

1. Verify file modification times are stable
2. Check filesystem supports precise timestamps
3. Ensure consistent file paths (no symlink variations)

## Contributing Performance Improvements

When submitting performance optimizations:

1. Include benchmark results (before/after)
2. Verify output remains identical
3. Document any trade-offs
4. Update this guide with findings

---

*Last Updated: January 2025*
*Maintained in: `/docs/performance-guide.md`*
