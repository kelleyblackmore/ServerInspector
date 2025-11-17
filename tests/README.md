# serverinspector Tests

This directory contains the test suite for serverinspector.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared pytest fixtures and configuration
├── unit/                       # Unit tests for individual modules
│   ├── test_config.py         # Configuration loading and validation tests ✅
│   ├── test_result_types.py   # Result types and status handling tests  
│   ├── test_checkers.py       # Checker modules tests
│   ├── test_runners.py        # Runner modules tests
│   ├── test_formatters.py     # Output formatter tests ✅
│   └── test_core.py           # Core serverinspector functionality tests ✅
└── integration/                # Multi-OS integration tests
    ├── run_tests.py           # Integration test runner
    ├── docker-compose.yml     # Container orchestration
    └── configs/               # Test configurations for each OS
```

## Running Tests

### Run All Unit Tests

```bash
pytest tests/unit/
```

### Run Specific Test File

```bash
pytest tests/unit/test_config.py -v
```

### Run With Coverage

```bash
pytest tests/unit/ --cov=src/serverinspector --cov-report=html
```

### Run Integration Tests

```bash
cd tests/integration
./run_tests.py
```

## Current Test Coverage

### Working Unit Tests (✅ = All Passing)

- ✅ **test_config.py** - 11/11 tests passing (79% code coverage)
  - Configuration file loading
  - YAML validation
  - Variable substitution
  - Backward compatibility

- ✅ **test_formatters.py** - 10/10 tests passing  
  - JSON formatter (100% coverage)
  - YAML formatter (100% coverage)
  - Terminal formatter (50% coverage)

- ✅ **test_core.py** - 6/6 tests passing (90% code coverage)
  - serverinspector initialization
  - Test execution flow
  - Output handling

- ✅ **test_result_types.py** - 8/8 tests passing (67% code coverage)
  - ResultStatus enum
  - TestResult dataclass
  - Error code categories
  - FileCheckResult helpers

- ✅ **test_checkers.py** - 7/7 tests passing (77% coverage of checker factory)
  - Checker factory function
  - All checker types (command, file, service, process, package, port)

- ✅ **test_runners.py** - 9/9 tests passing (92% coverage of local runner)
  - Local runner
  - SSH runner factory
  - Command execution

### Test Statistics

- **Total Tests**: 53
- **Passing**: 53 (100%)
- **Overall Coverage**: 24% of codebase
- **Core Modules Coverage**: 67-100%

## Adding New Tests

1. Create a new test file in `tests/unit/` with the naming convention `test_<module>.py`
2. Import the module you want to test
3. Use pytest class-based tests or functions
4. Use fixtures from `conftest.py` for common test setup

Example:

```python
"""
Unit tests for my new module
"""
import pytest
from serverinspector.mymodule import MyClass


class TestMyClass:
    """Test MyClass functionality."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        obj = MyClass()
        result = obj.do_something()
        
        assert result is not None
```

## Test Requirements

Install test dependencies:

```bash
pip install -e ".[test]"
```

This installs:
- pytest
- pytest-cov

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Release builds

## Coverage Goals

- **Target**: 70%+ code coverage
- **Current**: 24% overall, 67-100% on core modules
- **Next Focus**: Checkers, CLI, system collectors

The high-value core modules (config, core, formatters, runners) have excellent coverage (67-100%).
Lower coverage areas are in specialized checkers and CLI which are tested via integration tests.

## Contributing

When adding new features:
1. Write unit tests first (TDD)
2. Ensure tests pass locally
3. Aim for >80% coverage of new code
4. Update this README if adding new test categories
