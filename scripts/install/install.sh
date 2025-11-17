#!/bin/bash
#
# serverinspector Universal Installer
# This script detects your operating system and installs serverinspector
# in the most appropriate way.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/kelleyblackmore/serverinspector/main/install.sh | bash
#   # or
#   wget -qO- https://raw.githubusercontent.com/kelleyblackmore/serverinspector/main/install.sh | bash

set -e
BOLD="\033[1m"
RESET="\033[0m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"

echo -e "${BOLD}serverinspector Installer${RESET}"
echo "Detecting system configuration..."

# Check for Docker
HAS_DOCKER=false
if command -v docker >/dev/null 2>&1; then
    HAS_DOCKER=true
    echo -e "• ${GREEN}Docker detected${RESET}"
else
    echo -e "• ${YELLOW}Docker not found${RESET}"
fi

# Check for Python
HAS_PYTHON=false
PYTHON_VERSION=""
if command -v python3 >/dev/null 2>&1; then
    HAS_PYTHON=true
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "• ${GREEN}$PYTHON_VERSION detected${RESET}"
elif command -v python >/dev/null 2>&1; then
    # Check if python is python3
    PY_VERSION=$(python --version 2>&1)
    if [[ $PY_VERSION == Python\ 3* ]]; then
        HAS_PYTHON=true
        PYTHON_VERSION=$PY_VERSION
        echo -e "• ${GREEN}$PYTHON_VERSION detected${RESET}"
    else
        echo -e "• ${YELLOW}$PY_VERSION detected (Python 3 required)${RESET}"
    fi
else
    echo -e "• ${YELLOW}Python not found${RESET}"
fi

# Check pipx
HAS_PIPX=false
if command -v pipx >/dev/null 2>&1; then
    HAS_PIPX=true
    echo -e "• ${GREEN}pipx detected${RESET}"
else
    echo -e "• ${YELLOW}pipx not found${RESET}"
fi

# Check pip
HAS_PIP=false
if command -v pip >/dev/null 2>&1; then
    HAS_PIP=true
    echo -e "• ${GREEN}pip detected${RESET}"
else
    echo -e "• ${YELLOW}pip not found${RESET}"
fi

# Detect OS
OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    # Detect distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        echo -e "• ${GREEN}Linux detected: $NAME${RESET}"
    else
        DISTRO="unknown"
        echo -e "• ${GREEN}Linux detected: unknown distribution${RESET}"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "• ${GREEN}macOS detected${RESET}"
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
    echo -e "• ${GREEN}Windows detected${RESET}"
else
    echo -e "• ${YELLOW}Unknown OS: $OSTYPE${RESET}"
fi

echo ""
echo -e "${BOLD}Installation Options:${RESET}"

# Determine preferred installation method
if [ "$HAS_DOCKER" = true ]; then
    PREFERRED="docker"
    echo -e "1. ${BOLD}Docker (Recommended)${RESET}: Isolated container with all dependencies"
elif [ "$HAS_PIPX" = true ]; then
    PREFERRED="pipx"
    echo -e "1. ${BOLD}pipx (Recommended)${RESET}: Isolated Python package installation"
elif [ "$HAS_PYTHON" = true ] && [ "$HAS_PIP" = true ]; then
    PREFERRED="pip"
    echo -e "1. ${BOLD}pip (Recommended)${RESET}: Python package installation"
else
    PREFERRED="source"
    echo -e "1. ${BOLD}Source (Recommended)${RESET}: Manual installation from source"
fi

# List other options based on what's available
if [ "$PREFERRED" != "docker" ] && [ "$HAS_DOCKER" = true ]; then
    echo "2. Docker: Isolated container with all dependencies"
fi

if [ "$PREFERRED" != "pipx" ] && [ "$HAS_PIPX" = true ]; then
    echo "2. pipx: Isolated Python package installation"
fi

if [ "$PREFERRED" != "pip" ] && [ "$HAS_PYTHON" = true ] && [ "$HAS_PIP" = true ]; then
    echo "3. pip: Python package installation"
fi

if [ "$PREFERRED" != "source" ]; then
    echo "4. Source: Manual installation from source"
fi

echo ""

read -p "Select installation method [1]: " CHOICE
CHOICE=${CHOICE:-1}

case $CHOICE in
    1)
        METHOD=$PREFERRED
        ;;
    2)
        if [ "$PREFERRED" = "docker" ]; then
            if [ "$HAS_PIPX" = true ]; then
                METHOD="pipx"
            elif [ "$HAS_PYTHON" = true ] && [ "$HAS_PIP" = true ]; then
                METHOD="pip"
            else
                METHOD="source"
            fi
        elif [ "$PREFERRED" = "pipx" ]; then
            if [ "$HAS_DOCKER" = true ]; then
                METHOD="docker"
            else
                METHOD="source"
            fi
        else
            if [ "$HAS_DOCKER" = true ]; then
                METHOD="docker"
            elif [ "$HAS_PIPX" = true ]; then
                METHOD="pipx"
            elif [ "$HAS_PYTHON" = true ] && [ "$HAS_PIP" = true ]; then
                METHOD="pip"
            else
                echo -e "${RED}Invalid selection.${RESET}"
                exit 1
            fi
        fi
        ;;
    3)
        if [ "$HAS_PIPX" = true ]; then
            METHOD="pipx"
        else
            METHOD="pip"
        fi
        ;;
    4)
        METHOD="source"
        ;;
    *)
        echo -e "${RED}Invalid selection.${RESET}"
        exit 1
        ;;
esac

echo ""
echo -e "${BOLD}Installing serverinspector via $METHOD...${RESET}"

case $METHOD in
    docker)
        echo "Creating installation directory..."
        INSTALL_DIR="$HOME/serverinspector"
        mkdir -p "$INSTALL_DIR"
        cd "$INSTALL_DIR"

        echo "Downloading Dockerfile and supporting files..."
        curl -sSL https://raw.githubusercontent.com/kelleyblackmore/serverinspector/main/Dockerfile -o Dockerfile
        curl -sSL https://raw.githubusercontent.com/kelleyblackmore/serverinspector/main/scripts/docker-run.sh -o docker-run.sh
        chmod +x docker-run.sh
        mkdir -p config

        echo "Building Docker image..."
        docker build -t serverinspector .

        echo "Creating wrapper script..."
        cat > serverinspector << 'EOL'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
docker run -v "$SCRIPT_DIR/config:/config" \
           -v /etc:/host/etc:ro \
           -v /var/log:/host/var/log:ro \
           -v /proc:/host/proc:ro \
           serverinspector "$@"
EOL
        chmod +x serverinspector

        # Add to PATH if possible
        if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
            echo "Adding to PATH..."
            ln -sf "$INSTALL_DIR/serverinspector" "$HOME/.local/bin/serverinspector"
        fi

        echo -e "${GREEN}${BOLD}Installation successful!${RESET}"
        echo ""
        echo "You can now use serverinspector with:"
        echo -e "  ${BLUE}$INSTALL_DIR/serverinspector run /config/example.yaml${RESET}"

        if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
            echo -e "  or simply: ${BLUE}serverinspector run /config/example.yaml${RESET}"
        fi
        ;;

    pipx)
        echo "Installing serverinspector via pipx..."
        if [ "$HAS_PIPX" = true ]; then
            # Check if we're already in the repository
            if [ -f "pyproject.toml" ] && [ -d "src/serverinspector" ]; then
                echo "Detected existing repository."

                echo "Fixing package configuration..."
                # Remove test_types reference from pyproject.toml
                sed -i '/test_types/d' pyproject.toml

                # Make sure the directory exists to avoid the error
                mkdir -p src/serverinspector/test_types

                echo "Installing with pipx..."
                pipx install .
            else
                # Create temporary directory
                TEMP_DIR=$(mktemp -d)
                cd "$TEMP_DIR"

                echo "Cloning repository to modify configuration..."
                if command -v git >/dev/null 2>&1; then
                    git clone https://github.com/kelleyblackmore/serverinspector.git .
                else
                    if command -v curl >/dev/null 2>&1; then
                        curl -sSL https://github.com/kelleyblackmore/serverinspector/archive/main.tar.gz -o serverinspector.tar.gz
                    elif command -v wget >/dev/null 2>&1; then
                        wget -q https://github.com/kelleyblackmore/serverinspector/archive/main.tar.gz -O serverinspector.tar.gz
                    else
                        echo -e "${RED}Error: Neither git, curl, nor wget found. Cannot download source.${RESET}"
                        exit 1
                    fi

                    tar xzf serverinspector.tar.gz --strip-components=1
                    rm serverinspector.tar.gz
                fi

                echo "Fixing package configuration..."
                # Remove test_types reference from pyproject.toml
                sed -i '/test_types/d' pyproject.toml

                # Make sure the directory exists to avoid the error
                mkdir -p src/serverinspector/test_types

                echo "Installing with pipx..."
                pipx install .

                # Clean up
                cd - > /dev/null
                rm -rf "$TEMP_DIR"
            fi

            echo -e "${GREEN}${BOLD}Installation successful!${RESET}"
            echo ""
            echo "You can now use serverinspector with:"
            echo -e "  ${BLUE}serverinspector --help${RESET}"
        else
            echo -e "${RED}Error: pipx not found. Installing pipx first...${RESET}"
            if [ "$HAS_PIP" = true ]; then
                pip install --user pipx
                echo -e "${YELLOW}Adding pipx to your PATH...${RESET}"
                python3 -m pipx ensurepath
                echo -e "${GREEN}pipx installed.${RESET} Please restart your terminal and run this installer again."
            else
                echo -e "${RED}Error: Neither pipx nor pip found. Cannot proceed with pipx installation.${RESET}"
            fi
            exit 1
        fi
        ;;

    pip)
        echo "Installing serverinspector via pip..."
        if [ "$HAS_PIP" = true ]; then
            # Check if we're already in the repository
            if [ -f "pyproject.toml" ] && [ -d "src/serverinspector" ]; then
                echo "Detected existing repository."

                echo "Fixing package configuration..."
                # Remove test_types reference from pyproject.toml
                sed -i '/test_types/d' pyproject.toml

                # Make sure the directory exists to avoid the error
                mkdir -p src/serverinspector/test_types

                echo "Installing with pip..."
                pip install --user .
            else
                # Create temporary directory
                TEMP_DIR=$(mktemp -d)
                cd "$TEMP_DIR"

                echo "Cloning repository to modify configuration..."
                if command -v git >/dev/null 2>&1; then
                    git clone https://github.com/kelleyblackmore/serverinspector.git .
                else
                    if command -v curl >/dev/null 2>&1; then
                        curl -sSL https://github.com/kelleyblackmore/serverinspector/archive/main.tar.gz -o serverinspector.tar.gz
                    elif command -v wget >/dev/null 2>&1; then
                        wget -q https://github.com/kelleyblackmore/serverinspector/archive/main.tar.gz -O serverinspector.tar.gz
                    else
                        echo -e "${RED}Error: Neither git, curl, nor wget found. Cannot download source.${RESET}"
                        exit 1
                    fi

                    tar xzf serverinspector.tar.gz --strip-components=1
                    rm serverinspector.tar.gz
                fi

                echo "Fixing package configuration..."
                # Remove test_types reference from pyproject.toml
                sed -i '/test_types/d' pyproject.toml

                # Make sure the directory exists to avoid the error
                mkdir -p src/serverinspector/test_types

                echo "Installing with pip..."
                pip install --user .

                # Clean up
                cd - > /dev/null
                rm -rf "$TEMP_DIR"
            fi

            echo -e "${GREEN}${BOLD}Installation successful!${RESET}"
            echo ""
            echo "You can now use serverinspector with:"
            echo -e "  ${BLUE}serverinspector --help${RESET}"
        else
            echo -e "${RED}Error: pip not found. Cannot install via pip.${RESET}"
            exit 1
        fi
        ;;

    source)
        echo "Installing from source..."
        INSTALL_DIR="$HOME/serverinspector"
        mkdir -p "$INSTALL_DIR"
        cd "$INSTALL_DIR"

        echo "Downloading source code..."
        if command -v git >/dev/null 2>&1; then
            git clone https://github.com/kelleyblackmore/serverinspector.git .
        else
            if command -v curl >/dev/null 2>&1; then
                curl -sSL https://github.com/kelleyblackmore/serverinspector/archive/main.tar.gz -o serverinspector.tar.gz
            elif command -v wget >/dev/null 2>&1; then
                wget -q https://github.com/kelleyblackmore/serverinspector/archive/main.tar.gz -O serverinspector.tar.gz
            else
                echo -e "${RED}Error: Neither git, curl, nor wget found. Cannot download source.${RESET}"
                exit 1
            fi

            tar xzf serverinspector.tar.gz --strip-components=1
            rm serverinspector.tar.gz
        fi

        # Create virtualenv if available
        if [ "$HAS_PYTHON" = true ]; then
            if command -v python3 -m venv >/dev/null 2>&1; then
                echo "Creating virtual environment..."
                python3 -m venv venv
                . venv/bin/activate
                pip install .

                cat > serverinspector << 'EOL'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/venv/bin/python" -m serverinspector.cli "$@"
EOL
                chmod +x serverinspector

                # Add to PATH if possible
                if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
                    echo "Adding to PATH..."
                    ln -sf "$INSTALL_DIR/serverinspector" "$HOME/.local/bin/serverinspector"
                fi

                echo -e "${GREEN}${BOLD}Installation successful!${RESET}"
                echo ""
                echo "You can now use serverinspector with:"
                echo -e "  ${BLUE}$INSTALL_DIR/serverinspector --help${RESET}"

                if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
                    echo -e "  or simply: ${BLUE}serverinspector --help${RESET}"
                fi
            else
                echo "Installing dependencies..."
                pip install -r requirements.txt

                echo -e "${GREEN}${BOLD}Installation successful!${RESET}"
                echo ""
                echo "You can now use serverinspector by navigating to:"
                echo -e "  ${BLUE}cd $INSTALL_DIR${RESET}"
                echo "And running:"
                echo -e "  ${BLUE}python -m serverinspector.cli --help${RESET}"
            fi
        else
            echo -e "${YELLOW}Warning: Python not found. Manual setup required.${RESET}"
            echo "Please install Python 3.10 or later and then run:"
            echo -e "  ${BLUE}cd $INSTALL_DIR${RESET}"
            echo -e "  ${BLUE}pip install -r requirements.txt${RESET}"
        fi
        ;;
esac
