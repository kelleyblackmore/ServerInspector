# ServerInspect Scripts

This directory contains utility scripts for building, installing, and running ServerInspect.

## Directory Structure

### build/
Build and development scripts:
- `build_executable.py` - Build standalone executables for different platforms
- `cleanup.sh` - Clean up build artifacts and temporary files
- `format-code.sh` - Format code using code formatters

### install/
Installation scripts for various platforms:
- `install.sh` - Universal installation script for Unix-like systems
- `install.bat` - Installation script for Windows
- `install-dev.sh` - Development environment setup script
- `test-install.sh` - Test installation verification script

## Other Scripts

- `docker-build.sh` - Build Docker image for ServerInspect
- `docker-run.sh` - Quick start script for running ServerInspect in Docker
- `setup_security.sh` - Security configuration setup script

## Usage

Most scripts can be run directly from the project root:

```bash
# Build executable
python scripts/build/build_executable.py

# Install for development
bash scripts/install/install-dev.sh

# Build Docker image
bash scripts/docker-build.sh
```

For detailed installation instructions, see [../docs/INSTALL.md](../docs/INSTALL.md).
