# ServerInspect

A Python-based server inspection and testing tool, similar to InSpec, Goss, and ServerSpec. This tool allows you to define, run, and report on server tests and audits.

## Features

- Define tests in YAML configuration files
- Run tests on local or remote systems via SSH
- Multiple output formats (JSON, YAML, HTML, terminal)
- Collect and report detailed system information
- Extensible architecture for adding new test types and collectors

## Supported Test Types

- File tests (existence, permissions, content)
- Service tests (running status, enabled status)
- Process tests (running status, instance count)
- Command tests (exit status, output content)
- Package tests (installation status, version)

## Installation

### Using Pip (Recommended)

```bash
# Install from PyPI
pip install serverinspect
```

### Development Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/ServerInspector.git
   cd ServerInspector
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode
   ```bash
   pip install -e .
   ```

### From Source

1. Clone the repository
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the setup script:
   ```bash
   python -m pip install .
   ```

### Build a Standalone Executable

To build a standalone executable that can be distributed without Python:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the build script:
   ```bash
   python build_executable.py
   ```

3. The executable will be created in the `dist` directory

## Usage

### Command Aliases

The tool can be run using either:
- `serverinspect` - Full name
- `si` - Short alias

Both commands provide the same functionality.

### Basic Commands

```bash
# Show help
serverinspect --help
# or
si --help

# Run tests from a configuration file
serverinspect run examples/basic_test.yaml
# or
si run examples/basic_test.yaml

# Run tests on a remote server via SSH
serverinspect run examples/ssh_test.yaml --host example.com --username user --key-file ~/.ssh/id_rsa
# or
si run examples/ssh_test.yaml --host example.com --username user --key-file ~/.ssh/id_rsa

# Collect and display system information
serverinspect system-info --output-format terminal
# or
si system-info --output-format terminal

# Perform a quick check
serverinspect check file /etc/hosts --exists
# or
si check file /etc/hosts --exists

# Export results to different formats
serverinspect run examples/basic_test.yaml --output-format json --output-file results.json
serverinspect run examples/basic_test.yaml --output-format html --output-file report.html
```

### Example Test Configuration

```yaml
---
# General information
title: Basic Server Test
description: Tests basic server functionality and configuration

# Test definitions
tests:
  - name: Check if /etc/hosts exists
    type: file
    path: /etc/hosts
    exists: true
    
  - name: Check if sshd service is running
    type: service
    service: sshd
    running: true
    enabled: true
    
  - name: Check if date command works
    type: command
    command: date
    exit_status: 0
```

## Architecture

ServerInspect has a modular architecture:

- **Runners**: Execute tests on local or remote systems
- **Test Types**: Different types of tests (file, service, command, etc.)
- **Formatters**: Output formats for test results (JSON, YAML, HTML, terminal)
- **Collectors**: Gather system information

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.