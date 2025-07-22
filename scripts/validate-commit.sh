#!/bin/bash

# Git Commit Validation Script
# Automates the pre-commit validation workflow defined in docs/GIT_COMMIT_WORKFLOW.md

set -e  # Exit on any error

echo "🔍 Running Git commit validation workflow..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_status $RED "❌ Error: Not in a Git repository"
    exit 1
fi

print_status $BLUE "📂 Repository: $(basename "$(git rev-parse --show-toplevel)")"
print_status $BLUE "🌿 Branch: $(git branch --show-current)"

# 1. Check if .gitmessage template exists
echo ""
print_status $BLUE "🎯 Checking for Git message template..."
if [ -f ".gitmessage" ]; then
    print_status $GREEN "✅ Found .gitmessage template"
    
    # Check if git is configured to use it
    if git config commit.template | grep -q ".gitmessage"; then
        print_status $GREEN "✅ Git configured to use template"
    else
        print_status $YELLOW "⚠️  Configuring Git to use template..."
        git config commit.template .gitmessage
        print_status $GREEN "✅ Git template configured"
    fi
else
    print_status $YELLOW "⚠️  No .gitmessage template found (optional)"
fi

# 2. Code Quality Checks
echo ""
print_status $BLUE "🧹 Running code quality checks..."

# Check for Python files
if find . -name "*.py" -not -path "./.*" | head -1 | read; then
    # Ruff linting
    if command_exists ruff; then
        print_status $BLUE "  📊 Running ruff linting..."
        if ruff check .; then
            print_status $GREEN "  ✅ Ruff linting passed"
        else
            print_status $RED "  ❌ Ruff linting failed"
            exit 1
        fi
    else
        print_status $YELLOW "  ⚠️  Ruff not found, skipping linting"
    fi

    # Ruff formatting check
    if command_exists ruff; then
        print_status $BLUE "  🎨 Checking ruff formatting..."
        if ruff format . --check --diff; then
            print_status $GREEN "  ✅ Ruff formatting passed"
        else
            print_status $RED "  ❌ Ruff formatting failed"
            print_status $YELLOW "  💡 Run 'ruff format .' to fix formatting"
            exit 1
        fi
    else
        print_status $YELLOW "  ⚠️  Ruff not found, skipping formatting check"
    fi

    # MyPy type checking
    if command_exists mypy; then
        print_status $BLUE "  🔍 Running mypy type checking..."
        if mypy . 2>/dev/null; then
            print_status $GREEN "  ✅ MyPy type checking passed"
        else
            print_status $YELLOW "  ⚠️  MyPy found type issues (warnings only)"
        fi
    else
        print_status $YELLOW "  ⚠️  MyPy not found, skipping type checking"
    fi
else
    print_status $BLUE "  📝 No Python files found, skipping Python-specific checks"
fi

# 3. Test execution
echo ""
print_status $BLUE "🧪 Running tests..."
if [ -d "tests" ] || find . -path "./.venv" -prune -o -name "test_*.py" -print -o -name "*_test.py" -print | head -1 | read; then
    if command_exists pytest; then
        print_status $BLUE "  🎯 Running pytest..."
        if pytest --tb=short -q; then
            print_status $GREEN "  ✅ All tests passed"
        else
            print_status $RED "  ❌ Tests failed"
            exit 1
        fi
    elif command_exists python; then
        print_status $BLUE "  🐍 Running Python tests..."
        if python -m unittest discover -s tests -p "test_*.py" 2>/dev/null; then
            print_status $GREEN "  ✅ All tests passed"
        else
            print_status $YELLOW "  ⚠️  No tests found or test runner unavailable"
        fi
    else
        print_status $YELLOW "  ⚠️  No test runner found, skipping tests"
    fi
else
    print_status $BLUE "  📝 No tests found, skipping test execution"
fi

# 4. Security validation for dependency changes
echo ""
print_status $BLUE "🔒 Checking for dependency changes..."

# Check if dependency files have been modified
DEPS_CHANGED=false
if git diff --cached --name-only 2>/dev/null | grep -q -E "(pyproject\.toml|requirements.*\.txt|Pipfile|package\.json|yarn\.lock|Cargo\.toml)"; then
    DEPS_CHANGED=true
    print_status $YELLOW "  📦 Dependency files modified"
elif git diff --name-only 2>/dev/null | grep -q -E "(pyproject\.toml|requirements.*\.txt|Pipfile|package\.json|yarn\.lock|Cargo\.toml)"; then
    DEPS_CHANGED=true
    print_status $YELLOW "  📦 Dependency files modified (unstaged)"
fi

if [ "$DEPS_CHANGED" = true ]; then
    print_status $BLUE "  🛡️  Running security validation..."
    
    # Python dependency security
    if [ -f "pyproject.toml" ]; then
        if command_exists safety; then
            print_status $BLUE "    🔍 Running safety check..."
            if safety check; then
                print_status $GREEN "    ✅ No known security vulnerabilities"
            else
                print_status $RED "    ❌ Security vulnerabilities detected!"
                print_status $YELLOW "    💡 Review and fix security issues before committing"
                exit 1
            fi
        else
            print_status $YELLOW "    ⚠️  Safety not installed, install with: pip install safety"
            print_status $YELLOW "    💡 Security validation recommended for dependency changes"
        fi
    fi
    
    # Node.js dependency security
    if [ -f "package.json" ]; then
        if command_exists npm; then
            print_status $BLUE "    🔍 Running npm audit..."
            if npm audit --audit-level=high; then
                print_status $GREEN "    ✅ No high-severity vulnerabilities"
            else
                print_status $RED "    ❌ High-severity vulnerabilities detected!"
                exit 1
            fi
        else
            print_status $YELLOW "    ⚠️  npm not found, skipping Node.js security check"
        fi
    fi
else
    print_status $GREEN "  ✅ No dependency changes detected"
fi

# 5. Check for staged changes
echo ""
print_status $BLUE "📝 Checking staged changes..."
if git diff --cached --quiet; then
    print_status $YELLOW "  ⚠️  No staged changes found"
    print_status $BLUE "  💡 Use 'git add <files>' to stage changes before committing"
else
    STAGED_FILES=$(git diff --cached --name-only | wc -l | tr -d ' ')
    print_status $GREEN "  ✅ ${STAGED_FILES} file(s) staged for commit"
    
    print_status $BLUE "  📋 Staged files:"
    git diff --cached --name-only | sed 's/^/    - /'
fi

# 6. Commit message validation (if committing)
if [ "$1" = "--commit" ]; then
    echo ""
    print_status $BLUE "💬 Ready to commit with template..."
    print_status $BLUE "  💡 Remember to follow conventional commit format:"
    print_status $BLUE "     <type>(<scope>): <subject>"
    print_status $BLUE "     "
    print_status $BLUE "     <body>"
    print_status $BLUE "     "
    print_status $BLUE "     <footer>"
    echo ""
    
    git commit
else
    echo ""
    print_status $GREEN "🎉 All validations passed!"
    print_status $BLUE "💡 Ready to commit. Use one of:"
    print_status $BLUE "   • $0 --commit  (commits with template)"
    print_status $BLUE "   • git commit   (opens editor with template)"
    print_status $BLUE "   • git commit -m \"<message>\"  (inline message)"
fi

echo ""
print_status $GREEN "✨ Validation complete! Happy committing! ✨"
