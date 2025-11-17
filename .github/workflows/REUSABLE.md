# Reusable Workflows and Composite Pipelines

This document explains how to use and create reusable workflows in GitHub Actions.

## Overview

**Reusable workflows** allow you to call entire workflow files from other workflows, enabling:
- ✅ DRY principle (Don't Repeat Yourself)
- ✅ Centralized logic that can be updated in one place
- ✅ Complex multi-stage pipelines
- ✅ Conditional execution based on previous job results
- ✅ Passing data between workflows via inputs/outputs

## Reusable Workflow Files

### `reusable-test.yml`
**Purpose:** Run tests with configurable Python version and OS

**Inputs:**
- `python-version` (string): Python version (default: '3.11')
- `os` (string): Operating system (default: 'ubuntu-latest')
- `upload-coverage` (boolean): Upload to Codecov (default: true)

**Outputs:**
- `coverage-percent`: Test coverage percentage

**Usage:**
```yaml
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.12'
      os: ubuntu-latest
      upload-coverage: true
```

### `reusable-security.yml`
**Purpose:** Run security scans (bandit, safety, pip-audit)

**Inputs:**
- `severity-threshold` (string): Minimum severity (default: 'HIGH')
- `upload-sarif` (boolean): Upload to GitHub Security (default: true)

**Outputs:**
- `vulnerabilities-found`: Number of vulnerabilities detected

**Usage:**
```yaml
jobs:
  security:
    uses: ./.github/workflows/reusable-security.yml
    with:
      severity-threshold: 'MEDIUM'
```

### `reusable-build.yml`
**Purpose:** Build PyInstaller executable for specific platform

**Inputs:**
- `os` (string, required): Target OS (ubuntu-latest, windows-latest, macos-latest)
- `python-version` (string): Python version (default: '3.11')

**Outputs:**
- `artifact-name`: Name of uploaded artifact

**Usage:**
```yaml
jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      os: windows-latest
```

## Release Pipeline Architecture

The `release.yml` workflow orchestrates all reusable workflows into a complete release pipeline:

```
release.yml (Master Orchestrator)
├── test-matrix (parallel)
│   ├── Test Ubuntu + Python 3.10
│   ├── Test Ubuntu + Python 3.11
│   ├── Test Ubuntu + Python 3.12
│   ├── Test Windows + Python 3.10
│   ├── ... (9 total combinations)
│   └── Test macOS + Python 3.12
│
├── coverage (after test-matrix)
│   └── Upload coverage to Codecov
│
├── security (parallel with tests)
│   └── Run security scans
│
├── security-gate (after security)
│   └── Fail if vulnerabilities > threshold
│
├── build-linux (after tests + security-gate)
├── build-windows (after tests + security-gate)
├── build-macos (after tests + security-gate)
│
├── sbom (after tests + security-gate)
│   └── Generate Software Bill of Materials
│
├── build-package (after tests + security-gate)
│   └── Build Python wheel/sdist
│
├── create-release (after all builds + sbom)
│   └── Create GitHub Release with all artifacts
│
├── publish-pypi (after release, if not prerelease)
│   └── Publish to PyPI
│
└── publish-test-pypi (after release, always)
    └── Publish to Test PyPI
```

## How to Call Reusable Workflows

### Basic Call
```yaml
jobs:
  my-job:
    uses: ./.github/workflows/reusable-test.yml
```

### With Inputs
```yaml
jobs:
  my-job:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.12'
      os: ubuntu-latest
```

### With Matrix Strategy
```yaml
jobs:
  test-matrix:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ['3.10', '3.11', '3.12']
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: ${{ matrix.python }}
      os: ${{ matrix.os }}
```

### Accessing Outputs
```yaml
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
  
  check-coverage:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Check coverage
        run: |
          echo "Coverage: ${{ needs.test.outputs.coverage-percent }}"
```

### Conditional Execution Based on Output
```yaml
jobs:
  security:
    uses: ./.github/workflows/reusable-security.yml
  
  security-gate:
    needs: security
    runs-on: ubuntu-latest
    steps:
      - name: Fail if too many vulnerabilities
        run: |
          if [ "${{ needs.security.outputs.vulnerabilities-found }}" -gt 10 ]; then
            exit 1
          fi
  
  deploy:
    needs: security-gate  # Only runs if security-gate passes
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

## Creating Your Own Reusable Workflow

### Template
```yaml
name: Reusable - My Task

on:
  workflow_call:
    inputs:
      my-input:
        description: 'Description of input'
        required: true
        type: string
      optional-input:
        description: 'Optional input'
        required: false
        type: boolean
        default: false
    outputs:
      my-output:
        description: 'Description of output'
        value: ${{ jobs.my-job.outputs.result }}
    secrets:
      my-secret:
        description: 'Required secret'
        required: true

jobs:
  my-job:
    runs-on: ubuntu-latest
    outputs:
      result: ${{ steps.step1.outputs.value }}
    
    steps:
      - name: Do something
        id: step1
        run: |
          echo "value=success" >> $GITHUB_OUTPUT
```

### Key Points
1. **Trigger:** Must use `on: workflow_call`
2. **Inputs:** Define with `type` (string, number, boolean)
3. **Outputs:** Reference job outputs via `jobs.<job-id>.outputs.<output-name>`
4. **Secrets:** Can be passed from calling workflow
5. **Location:** Must be in `.github/workflows/` directory
6. **Path:** Reference with `./.github/workflows/filename.yml`

## Advanced Patterns

### Sequential Pipeline with Gates
```yaml
jobs:
  stage1:
    uses: ./.github/workflows/test.yml
  
  gate1:
    needs: stage1
    runs-on: ubuntu-latest
    steps:
      - run: echo "Gate check"
  
  stage2:
    needs: gate1
    uses: ./.github/workflows/build.yml
  
  gate2:
    needs: stage2
    runs-on: ubuntu-latest
    steps:
      - run: echo "Final gate"
  
  deploy:
    needs: gate2
    uses: ./.github/workflows/deploy.yml
```

### Parallel Execution with Merge
```yaml
jobs:
  test-backend:
    uses: ./.github/workflows/test-backend.yml
  
  test-frontend:
    uses: ./.github/workflows/test-frontend.yml
  
  integration:
    needs: [test-backend, test-frontend]
    uses: ./.github/workflows/integration-tests.yml
```

### Dynamic Matrix from Output
```yaml
jobs:
  discover:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - id: set-matrix
        run: |
          echo 'matrix=["3.10","3.11","3.12"]' >> $GITHUB_OUTPUT
  
  test:
    needs: discover
    strategy:
      matrix:
        python-version: ${{ fromJson(needs.discover.outputs.matrix) }}
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: ${{ matrix.python-version }}
```

## Benefits

### 1. **Maintainability**
Update logic once, applies everywhere:
```yaml
# Before: Logic duplicated in 5 workflows
# After: Logic in one reusable workflow, called by 5 workflows
```

### 2. **Consistency**
All workflows use same test/build/deploy logic:
```yaml
# test.yml, pr.yml, release.yml all call reusable-test.yml
```

### 3. **Composability**
Build complex pipelines from simple components:
```yaml
# release.yml = test + security + build + deploy
# pr.yml = test + security
# nightly.yml = test + integration + performance
```

### 4. **Flexibility**
Customize behavior via inputs without changing core logic:
```yaml
# Development: upload-coverage: false
# Production: upload-coverage: true
```

## Common Use Cases

### PR Validation
```yaml
# .github/workflows/pr.yml
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
  security:
    uses: ./.github/workflows/reusable-security.yml
```

### Nightly Builds
```yaml
# .github/workflows/nightly.yml
jobs:
  test-all-versions:
    strategy:
      matrix:
        python: ['3.8', '3.9', '3.10', '3.11', '3.12', '3.13']
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: ${{ matrix.python }}
```

### Release Process
```yaml
# .github/workflows/release.yml (see full example above)
# Orchestrates: test → security → build → package → publish
```

## Limitations

1. **Nesting Depth:** Max 4 levels of reusable workflow calls
2. **Same Repository:** Reusable workflows must be in same repo (or public repos)
3. **No Dynamic Paths:** Cannot compute workflow path dynamically
4. **Environment Variables:** Not passed automatically, use inputs/secrets

## Troubleshooting

### "Workflow not found"
```yaml
# ❌ Wrong
uses: reusable-test.yml

# ✅ Correct
uses: ./.github/workflows/reusable-test.yml
```

### "Required input not provided"
```yaml
# ❌ Missing required input
uses: ./.github/workflows/reusable-build.yml

# ✅ Provide required input
uses: ./.github/workflows/reusable-build.yml
with:
  os: ubuntu-latest
```

### "Cannot access output"
```yaml
# ❌ Wrong job reference
echo ${{ needs.wrong-job-name.outputs.value }}

# ✅ Use exact job ID from workflow
echo ${{ needs.test.outputs.coverage-percent }}
```

## Best Practices

1. **Keep workflows focused:** One reusable workflow = one responsibility
2. **Use descriptive names:** `reusable-test.yml` not `workflow1.yml`
3. **Document inputs/outputs:** Clear descriptions help users
4. **Provide defaults:** Make inputs optional when sensible
5. **Output useful data:** Return info for downstream decisions
6. **Version carefully:** Changes affect all callers
7. **Test thoroughly:** Bugs impact multiple workflows

## Migration Path

### Before (Duplicated Logic)
```yaml
# test.yml
jobs:
  test:
    steps:
      - checkout
      - setup python
      - run tests
      - upload coverage

# pr.yml
jobs:
  test:
    steps:
      - checkout
      - setup python
      - run tests
      # Copy-pasted, can drift
```

### After (Reusable)
```yaml
# reusable-test.yml
on: workflow_call
jobs:
  test:
    steps: [...]

# test.yml
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml

# pr.yml
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml
```

## See Also

- [GitHub Docs: Reusing workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [GitHub Docs: Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Example: release.yml](./release.yml) - Full orchestration example
