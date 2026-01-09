# CI/CD Pipeline Integration Guide: Mutation Testing, Code Quality, and Dependency Management

This guide provides a comprehensive, repository-agnostic approach to integrating mutation testing, code quality checks, and dependency management into your CI/CD pipeline using GitHub Actions.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Integration Steps](#integration-steps)
5. [Code Quality Checks](#code-quality-checks)
6. [Dependency Management](#dependency-management)
7. [Mutation Testing Integration](#mutation-testing-integration)
8. [GitHub Pages Deployment](#github-pages-deployment)
9. [Reusable Actions](#reusable-actions)
10. [Configuration Examples](#configuration-examples)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This integration provides:

- **Parallel Code Quality Checks**: UV lock validation, Ruff linting/formatting, and Gitleaks security scanning
- **Dependency Management**: Automated lock file validation using `uv`
- **Mutation Testing**: Parallel mutation testing per module using Cosmic-Ray
- **Automated Reporting**: HTML reports deployed to GitHub Pages
- **Reusable Components**: Composite actions for common operations

### Pipeline Flow

```
┌─────────────────────────────────────┐
│  Code Quality Checks (Parallel)     │
│  - UV Lock Check                    │
│  - Ruff Lint                        │
│  - Ruff Format                      │
│  - Gitleaks Scan                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Unit Tests                         │
│  (Depends on all quality checks)   │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌──────────────┐  ┌──────────────────┐
│  Deployment  │  │ Mutation Testing  │
│              │  │ (Parallel)        │
└──────────────┘  └─────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Aggregate &      │
                   │ Deploy Reports   │
                   └──────────────────┘
```

---

## Architecture

### Key Components

1. **Reusable Composite Actions**: Common setup and testing logic
2. **Matrix Strategy**: Parallel execution for mutation testing
3. **Artifact Management**: Storage and retrieval of test results
4. **Dynamic Module Detection**: Automatic discovery of modules to test

### Directory Structure

```
.github/
├── workflows/
│   └── ci.yml                    # Main CI/CD pipeline
├── actions/
│   ├── setup-python-uv/
│   │   └── action.yml           # Python + UV setup action
│   └── mutation-test-module/
│       └── action.yml           # Mutation testing action
└── scripts/
    └── detect-modules.py         # Module detection script
```

---

## Prerequisites

### Required Tools

- **Python 3.8+**: For running tests and mutation testing
- **UV**: Fast Python package manager (installed automatically)
- **Cosmic-Ray**: Mutation testing framework
- **Ruff**: Fast Python linter and formatter
- **Gitleaks**: Secret scanning tool
- **Pytest**: Testing framework

### Repository Requirements

- GitHub repository with Actions enabled
- Python project with test suite
- `requirements.txt` or `pyproject.toml` for dependencies
- Test files following naming convention (e.g., `test_*.py`)

---

## Integration Steps

### Step 1: Create Reusable Actions

#### 1.1 Setup Python and UV Action

Create `.github/actions/setup-python-uv/action.yml`:

```yaml
name: 'Setup Python and UV'
description: 'Sets up Python and installs UV package manager'
inputs:
  python-version:
    description: 'Python version to use'
    required: false
    default: '3.10'
runs:
  using: 'composite'
  steps:
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}

    - name: Install uv
      shell: bash
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
        echo "$HOME/.local/bin" >> $GITHUB_PATH
        uv --version
```

#### 1.2 Mutation Test Module Action

Create `.github/actions/mutation-test-module/action.yml`:

```yaml
name: 'Mutation Test Module'
description: 'Run mutation testing on a single Python module using cosmic-ray'
inputs:
  module:
    description: 'Module name or path'
    required: true
  module-path:
    description: 'Path to module file (e.g., src/module.py)'
    required: true
  test-path:
    description: 'Path to test directory or file'
    required: true
  python-version:
    description: 'Python version to use'
    required: false
    default: '3.10'
outputs:
  database-path:
    description: 'Path to the SQLite database file'
    value: ${{ steps.init-db.outputs.database-path }}
  report-path:
    description: 'Path to the HTML report'
    value: ${{ steps.generate-report.outputs.report-path }}
runs:
  using: 'composite'
  steps:
    - name: Setup Python and UV
      uses: ./.github/actions/setup-python-uv
      with:
        python-version: ${{ inputs.python-version }}

    - name: Install dependencies
      shell: bash
      run: |
        uv pip install --system -r requirements.txt
        uv pip install --system cosmic-ray pytest

    - name: Generate cosmic-ray config
      id: config
      shell: bash
      run: |
        config_file="cosmic-ray-${{ inputs.module }}.toml"
        cat > "$config_file" << EOF
        [cosmic-ray]
        module-path = "${{ inputs.module-path }}"
        timeout = 10.0
        excluded-modules = []
        test-command = "pytest ${{ inputs.test-path }} -p no:cov"
        
        [cosmic-ray.distributor]
        name = "local"
        EOF
        echo "config-path=$config_file" >> $GITHUB_OUTPUT

    - name: Initialize cosmic-ray database
      id: init-db
      shell: bash
      run: |
        db_file="db-${{ inputs.module }}.sqlite"
        cosmic-ray init "${{ steps.config.outputs.config-path }}" "$db_file"
        echo "database-path=$db_file" >> $GITHUB_OUTPUT

    - name: Run baseline tests
      shell: bash
      continue-on-error: true
      run: |
        cosmic-ray baseline "${{ steps.config.outputs.config-path }}" || true

    - name: Execute mutation testing
      shell: bash
      continue-on-error: true
      run: |
        cosmic-ray exec "${{ steps.config.outputs.config-path }}" "${{ steps.init-db.outputs.database-path }}"

    - name: Generate HTML report
      id: generate-report
      shell: bash
      run: |
        mkdir -p "mutation-reports/${{ inputs.module }}"
        cr-html "${{ steps.init-db.outputs.database-path }}" > "mutation-reports/${{ inputs.module }}/report.html"
        echo "report-path=mutation-reports/${{ inputs.module }}/report.html" >> $GITHUB_OUTPUT
```

### Step 2: Create Module Detection Script

Create `.github/scripts/detect-modules.py`:

```python
#!/usr/bin/env python3
"""
Detect Python modules for mutation testing.

Adapt this script to your project structure:
- Change SOURCE_DIR to your source directory (e.g., 'src', 'lib', 'app')
- Modify the detection logic based on your module organization
"""

import json
import os
import sys
from pathlib import Path

# CONFIGURATION: Adjust these for your project
SOURCE_DIR = "app"  # Change to 'src', 'lib', or your source directory
EXCLUDE_PATTERNS = ["__init__.py", "__pycache__", "test_", "tests/"]


def detect_modules(source_dir=SOURCE_DIR):
    """Detect Python modules in the source directory."""
    source_path = Path(source_dir)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Directory {source_dir} does not exist")
    
    modules = []
    
    # Find all Python files recursively
    for py_file in source_path.rglob("*.py"):
        # Skip excluded patterns
        if any(pattern in str(py_file) for pattern in EXCLUDE_PATTERNS):
            continue
        
        # Get relative path from source directory
        rel_path = py_file.relative_to(source_path)
        
        # Convert to module path format (e.g., "module" or "subpackage/module")
        module_path = str(rel_path.with_suffix("")).replace("/", ".")
        modules.append({
            "name": py_file.stem,
            "path": str(py_file),
            "module_path": module_path
        })
    
    # Sort for consistent output
    modules.sort(key=lambda x: x["module_path"])
    
    return modules


if __name__ == "__main__":
    try:
        modules = detect_modules()
        # Output as JSON array for GitHub Actions
        print(json.dumps(modules, indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"Error detecting modules: {e}", file=sys.stderr)
        sys.exit(1)
```

### Step 3: Create Main CI/CD Workflow

Create `.github/workflows/ci.yml` with the following structure:

```yaml
name: CI/CD Pipeline

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main, master]

jobs:
  # Code Quality Checks - Run in parallel
  uv-lock-check:
    name: UV Lock Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-uv
        with:
          python-version: '3.10'
      - run: uv lock --check
        shell: bash

  ruff-check:
    name: Ruff Lint Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-uv
      - run: uv tool run ruff check .
        shell: bash

  ruff-format-check:
    name: Ruff Format Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-uv
      - run: uv tool run ruff format --check .
        shell: bash

  gitleaks-check:
    name: Gitleaks Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - run: |
          wget -q -O /tmp/gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.24.2/gitleaks_8.24.2_linux_x64.tar.gz
          tar -xzf /tmp/gitleaks.tar.gz -C /tmp
          sudo mv /tmp/gitleaks /usr/local/bin/
          gitleaks detect --source . --verbose --no-git
        shell: bash

  # Unit Tests - Depends on code quality checks
  unit-tests:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: [uv-lock-check, ruff-check, ruff-format-check, gitleaks-check]
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-uv
      - run: |
          uv pip install --system -r requirements.txt
          pytest --cov=. --cov-report=xml
        shell: bash
      # Add coverage upload, test result upload, etc.

  # Mutation Testing Setup
  mutation-setup:
    name: Mutation Testing Setup
    runs-on: ubuntu-latest
    needs: unit-tests
    outputs:
      modules: ${{ steps.detect.outputs.modules }}
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-uv
      - name: Install dependencies
        run: |
          uv pip install --system -r requirements.txt
          uv pip install --system cosmic-ray
        shell: bash
      - name: Detect modules
        id: detect
        run: |
          python .github/scripts/detect-modules.py > modules.json
          modules=$(cat modules.json)
          echo "modules=$modules" >> $GITHUB_OUTPUT
        shell: bash

  # Parallel Mutation Testing
  mutation-test:
    name: Mutation Test - ${{ matrix.module.name }}
    runs-on: ubuntu-latest
    needs: mutation-setup
    strategy:
      matrix:
        module: ${{ fromJson(needs.mutation-setup.outputs.modules) }}
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/mutation-test-module
        with:
          module: ${{ matrix.module.name }}
          module-path: ${{ matrix.module.module_path }}
          test-path: "tests"  # Adjust to your test directory
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: mutation-${{ matrix.module.name }}
          path: |
            db-${{ matrix.module.name }}.sqlite
            mutation-reports/${{ matrix.module.name }}/
          retention-days: 30

  # Aggregate Mutation Results
  mutation-aggregate:
    name: Aggregate Mutation Results
    runs-on: ubuntu-latest
    needs: mutation-test
    if: always()
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python-uv
      - run: uv pip install --system cosmic-ray
        shell: bash
      - uses: actions/download-artifact@v4
        with:
          pattern: mutation-*
          merge-multiple: true
          path: .
      - name: Generate summary
        run: |
          echo "=== Mutation Testing Status ===" > mutation-summary.txt
          for db_file in $(find . -name "db-*.sqlite" -type f); do
            module=$(basename "$db_file" | sed 's/db-\(.*\)\.sqlite/\1/')
            echo "Module: $module" >> mutation-summary.txt
            cr-report "$db_file" --show-pending >> mutation-summary.txt
          done
        shell: bash
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: mutation-reports-all
          path: |
            mutation-reports/
            mutation-summary.txt
            db-*.sqlite
          retention-days: 30

  # Deploy to GitHub Pages
  deployment:
    name: Deploy Mutation Reports
    runs-on: ubuntu-latest
    needs: mutation-aggregate
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    permissions:
      contents: read
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    concurrency:
      group: "pages"
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: mutation-reports-all
          path: mutation-reports
      - name: Create index page
        run: |
          mkdir -p pages
          # Generate index.html with links to all reports
          # (See full implementation in Configuration Examples)
        shell: bash
      - uses: actions/configure-pages@v5
        with:
          enablement: true
      - uses: actions/upload-pages-artifact@v3
        with:
          path: 'pages'
      - uses: actions/deploy-pages@v4
        id: deployment
```

---

## Code Quality Checks

### UV Lock Check

Validates that `uv.lock` is up-to-date with `pyproject.toml` or `requirements.txt`.

**Configuration:**
- Requires `pyproject.toml` or `uv.lock` file
- Can be skipped if not using UV: Add `if: false` to the job

**Customization:**
```yaml
- name: Run uv-lock check
  run: |
    uv lock --check
    # Or for specific files:
    uv lock --check --locked-file uv.lock
```

### Ruff Lint Check

Fast Python linter using Ruff.

**Configuration:**
- Create `ruff.toml` or `pyproject.toml` with `[tool.ruff]` section
- Adjust rules in configuration file

**Customization:**
```yaml
- name: Run ruff check
  run: |
    uv tool run ruff check . --config ruff.toml
    # Or with specific rules:
    uv tool run ruff check . --select E,F,W
```

### Ruff Format Check

Validates code formatting.

**Configuration:**
- Uses same configuration as Ruff lint
- Can auto-fix: Remove `--check` flag

**Customization:**
```yaml
- name: Run ruff format check
  run: |
    uv tool run ruff format --check .
    # To auto-fix (not recommended in CI):
    # uv tool run ruff format .
```

### Gitleaks Security Scan

Scans for secrets and credentials in code.

**Configuration:**
- Create `.gitleaksignore` to exclude files
- Adjust sensitivity in configuration

**Customization:**
```yaml
- name: Run gitleaks
  run: |
    gitleaks detect --source . --verbose --no-git --config .gitleaks.toml
```

---

## Dependency Management

### UV Package Manager

UV is a fast Python package manager that replaces pip and pip-tools.

**Setup:**
- Automatically installed by `setup-python-uv` action
- Works with `requirements.txt` or `pyproject.toml`

**Lock File Management:**
```bash
# Generate/update lock file
uv lock

# Install from lock file
uv sync

# Install system-wide (for CI)
uv pip install --system -r requirements.txt
```

### Integration with Existing Pipelines

If you're using `pip` or `poetry`:

**For pip:**
```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install cosmic-ray pytest
```

**For poetry:**
```yaml
- name: Install Poetry
  uses: snok/install-poetry@v1
- name: Install dependencies
  run: poetry install
```

---

## Mutation Testing Integration

### Cosmic-Ray Setup

Cosmic-Ray is a mutation testing framework for Python.

**Installation:**
```bash
pip install cosmic-ray
# Or with UV:
uv pip install cosmic-ray
```

**Key Commands:**
- `cosmic-ray init`: Initialize database
- `cosmic-ray baseline`: Run baseline tests
- `cosmic-ray exec`: Execute mutations
- `cr-report`: Generate text reports
- `cr-html`: Generate HTML reports

### Module Detection Strategy

**Option 1: Flat Structure** (`src/module.py`)
```python
SOURCE_DIR = "src"
# Detects: module.py → module
```

**Option 2: Package Structure** (`src/package/module.py`)
```python
SOURCE_DIR = "src"
# Detects: package/module.py → package.module
```

**Option 3: Multiple Source Directories**
```python
SOURCE_DIRS = ["src", "lib", "app"]
# Iterate over multiple directories
```

### Test Command Configuration

**Disable Coverage:**
```yaml
test-command: "pytest tests -p no:cov"
```

**Module-Specific Tests:**
```yaml
test-command: "pytest tests/test_module.py -p no:cov"
```

**With Test Markers:**
```yaml
test-command: "pytest tests -m unit -p no:cov"
```

### Timeout Configuration

Adjust timeout based on test suite size:

```toml
[cosmic-ray]
timeout = 10.0  # Seconds per mutation
```

For large test suites, increase timeout:
```toml
timeout = 30.0
```

---

## GitHub Pages Deployment

### Automatic Enablement

The workflow attempts to enable GitHub Pages automatically:

```yaml
- name: Enable GitHub Pages
  uses: actions/github-script@v7
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    script: |
      # Check and enable Pages if needed
      # (See full implementation in workflow)
```

### Index Page Generation

Create an index page linking to all module reports:

```bash
cat > pages/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <title>Mutation Testing Reports</title>
</head>
<body>
  <h1>Mutation Testing Reports</h1>
  <!-- Links to module reports -->
</body>
</html>
EOF
```

### Manual Setup (If Automatic Fails)

1. Go to repository **Settings** → **Pages**
2. Set **Source** to **GitHub Actions**
3. Save settings

---

## Reusable Actions

### Benefits

- **DRY Principle**: Avoid code duplication
- **Consistency**: Same setup across all jobs
- **Maintainability**: Update once, apply everywhere
- **Reusability**: Use across multiple workflows

### Creating Composite Actions

**Structure:**
```yaml
name: 'Action Name'
description: 'Action description'
inputs:
  input-name:
    description: 'Input description'
    required: true
outputs:
  output-name:
    description: 'Output description'
    value: ${{ steps.step-id.outputs.output-name }}
runs:
  using: 'composite'
  steps:
    - name: Step name
      shell: bash
      run: |
        # Commands here
```

### Best Practices

1. **Keep actions focused**: One action, one purpose
2. **Use inputs/outputs**: Make actions configurable
3. **Document thoroughly**: Clear descriptions and examples
4. **Test independently**: Verify actions work in isolation

---

## Configuration Examples

### Example 1: Standard Python Package

**Structure:**
```
project/
├── src/
│   └── package/
│       ├── __init__.py
│       ├── module1.py
│       └── module2.py
├── tests/
│   ├── test_module1.py
│   └── test_module2.py
└── pyproject.toml
```

**Configuration:**
```python
# detect-modules.py
SOURCE_DIR = "src/package"
```

```yaml
# mutation-test-module action
module-path: "src/package/${{ inputs.module }}.py"
test-path: "tests"
```

### Example 2: Django Project

**Structure:**
```
project/
├── app/
│   ├── models.py
│   ├── views.py
│   └── utils.py
├── tests/
│   ├── test_models.py
│   └── test_views.py
└── requirements.txt
```

**Configuration:**
```python
# detect-modules.py
SOURCE_DIR = "app"
EXCLUDE_PATTERNS = ["__init__.py", "migrations/", "management/"]
```

```yaml
# mutation-test-module action
module-path: "app/${{ inputs.module }}.py"
test-command: "python manage.py test app.tests.test_${{ inputs.module }}"
```

### Example 3: FastAPI Application

**Structure:**
```
project/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   └── utils.py
├── tests/
│   └── test_*.py
└── requirements.txt
```

**Configuration:**
```python
# detect-modules.py
SOURCE_DIR = "app"
```

```yaml
# mutation-test-module action
module-path: "app/${{ inputs.module }}.py"
test-command: "pytest tests/test_${{ inputs.module }}.py -p no:cov"
```

### Example 4: Monorepo Structure

**Structure:**
```
monorepo/
├── services/
│   ├── service1/
│   │   └── src/
│   └── service2/
│       └── src/
└── shared/
    └── lib/
```

**Configuration:**
```python
# detect-modules.py
SOURCE_DIRS = ["services/service1/src", "services/service2/src", "shared/lib"]

def detect_modules():
    modules = []
    for source_dir in SOURCE_DIRS:
        # Detect modules in each directory
        # Prefix with service name for uniqueness
        pass
    return modules
```

---

## Troubleshooting

### Common Issues

#### 1. "GitHub Pages not enabled"

**Solution:**
- Enable Pages manually in repository settings
- Or ensure workflow has `pages: write` permission
- Check that `enablement: true` is set in `configure-pages`

#### 2. "Module not found" in mutation testing

**Solution:**
- Verify module path in cosmic-ray config
- Check that module detection script finds the module
- Ensure module is importable (check PYTHONPATH)

#### 3. "Baseline tests failing"

**Solution:**
- Disable coverage plugin: `-p no:cov`
- Increase timeout in cosmic-ray config
- Check that test command runs successfully locally

#### 4. "UV lock check failing"

**Solution:**
- Run `uv lock` locally to update lock file
- Commit updated `uv.lock` file
- Or skip UV lock check if not using UV

#### 5. "Artifact not found"

**Solution:**
- Ensure artifact upload happens before download
- Check artifact names match exactly
- Verify `if: always()` is set for artifact uploads

### Debugging Tips

1. **Enable Debug Logging:**
```yaml
- name: Debug
  run: |
    echo "::debug::Variable value: ${{ variable }}"
    echo "Modules: ${{ needs.mutation-setup.outputs.modules }}"
```

2. **Check Artifact Contents:**
```yaml
- name: List artifacts
  run: |
    ls -la
    find . -name "*.sqlite"
    cat mutation-summary.txt
```

3. **Test Locally:**
```bash
# Test module detection
python .github/scripts/detect-modules.py

# Test mutation testing
cosmic-ray init config.toml db.sqlite
cosmic-ray baseline config.toml
cosmic-ray exec config.toml db.sqlite
cr-report db.sqlite --show-pending
```

---

## Best Practices

### 1. Incremental Integration

- Start with code quality checks
- Add unit tests
- Integrate mutation testing last
- Test each component independently

### 2. Performance Optimization

- Use matrix strategy for parallel execution
- Set appropriate timeouts
- Cache dependencies when possible
- Limit mutation testing to changed modules

### 3. Reporting

- Generate HTML reports for visual inspection
- Deploy to GitHub Pages for easy access
- Include summaries in PR comments
- Store artifacts for historical comparison

### 4. Maintenance

- Keep actions updated
- Review and update dependencies regularly
- Monitor workflow execution times
- Adjust timeouts based on project growth

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cosmic-Ray Documentation](https://cosmic-ray.readthedocs.io/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)

---

## Summary

This guide provides a complete, repository-agnostic approach to integrating:

✅ **Code Quality Checks**: UV lock, Ruff lint/format, Gitleaks  
✅ **Dependency Management**: UV-based dependency validation  
✅ **Mutation Testing**: Parallel module testing with Cosmic-Ray  
✅ **Automated Reporting**: GitHub Pages deployment  
✅ **Reusable Components**: Composite actions for common operations  

The integration is designed to be:
- **Flexible**: Adaptable to any Python project structure
- **Scalable**: Handles projects of any size
- **Maintainable**: Uses reusable actions and clear structure
- **Comprehensive**: Covers all aspects of CI/CD pipeline

Follow the step-by-step instructions, adapt the configuration examples to your project structure, and you'll have a robust CI/CD pipeline with mutation testing integrated.

