# ServerInspect Installation Guide

This document explains the various ways to install ServerInspect.

## Quick Installation

### Linux/macOS

Run this command in your terminal:

```bash
curl -sSL https://raw.githubusercontent.com/kelleyblackmore/ServerInspector/main/\
install.sh | bash
```

or

```bash
wget -qO- https://raw.githubusercontent.com/kelleyblackmore/ServerInspector/main/\
install.sh | bash
```

### Windows

1. Download the [install.bat](https://tinyurl.com/serverinspector) file
ServerInspector/main/install.bat>) file
2. Right-click and select "Run as administrator" (recommended but not required)
3. Follow the prompts to install

## Installation Methods

The installer offers multiple installation methods based on your system:

### Docker Installation (Recommended if available)

Installs ServerInspect as a Docker container:

- Provides an isolated environment
- Includes all dependencies
- Consistent experience across platforms
- Can inspect the host system through volume mounts

### pipx Installation (Recommended for Python users)

Installs ServerInspect in an isolated Python environment:

- Uses pipx to install from GitHub
- Creates an isolated environment for ServerInspect
- Avoids dependency conflicts with other packages
- Makes command-line tools available globally
- Requires Python 3.6+

### Python Package Installation

Installs ServerInspect as a Python package:

- Uses pip to install directly from GitHub
- Requires Python 3.10 or newer
- Integrates with your existing Python environment

### Executable Installation

Downloads a standalone executable:

- No dependencies required (except on Windows)
- Simple to use
- Easy to add to PATH

### Source Installation

Installs from source code:

- Most flexible option
- Can be customized for your environment
- Creates a virtual environment if possible

## Manual Installation

If the installers don't work for your system, you can install manually:

### Docker Manual Installation

```bash
# Clone the repository
git clone https://github.com/kelleyblackmore/ServerInspector.git
cd ServerInspector

# Build the Docker image
docker build -t serverinspect .

# Run ServerInspect
docker run -v "$(pwd)/config:/config" \
           -v /etc:/host/etc:ro \
           -v /var/log:/host/var/log:ro \
           -v /proc:/host/proc:ro \
           serverinspect run /config/example.yaml
```

### pipx Manual Installation (Recommended for Python users)

```bash
# Install pipx if not already installed
pip install --user pipx
python -m pipx ensurepath

# Install ServerInspect with pipx
pipx install git+https://github.com/kelleyblackmore/ServerInspector.git

# Run ServerInspect
serverinspect --help
```

### Python Manual Installation

```bash
# Install from GitHub
pip install git+https://github.com/kelleyblackmore/ServerInspector.git

# Or clone and install
git clone https://github.com/kelleyblackmore/ServerInspector.git
cd ServerInspector
pip install .
```

## Troubleshooting

### Docker Installation Issues

- **Docker not running**: Make sure the Docker service is running
- **Permission errors**: You may need to run Docker commands with `sudo`
- **Missing volumes**: Check that the host directories exist

### pipx Installation Issues

- **pipx not found**: Install with `pip install --user pipx` then
  `python -m pipx ensurepath`
- **Python version**: pipx requires Python 3.6+
- **PATH issues**: Make sure `~/.local/bin` is in your PATH

### Python Installation Issues

- **Python version**: ServerInspect requires Python 3.10+
- **Permission errors**: Try installing with `--user` flag
- **Missing dependencies**: Check error messages for missing packages

### Windows Issues

- **Execution policy**: You may need to change PowerShell execution policy
- **PATH issues**: Add installation directory to your PATH manually
- **Admin rights**: Some installation methods may require admin rights
