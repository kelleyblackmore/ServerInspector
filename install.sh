#!/bin/bash
#
# ServerInspect Installation Script
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/yourusername/ServerInspector/main/install.sh | bash
#

set -e

# Text formatting
BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RESET="\033[0m"

# Default values
VERSION="latest"
INSTALL_DIR="$HOME/.local/bin"
GITHUB_REPO="yourusername/ServerInspector"

echo -e "${BOLD}${BLUE}ServerInspect Installer${RESET}"
echo "This script will install ServerInspect to your system."
echo ""

# Detect OS type
echo -e "${BOLD}Detecting operating system...${RESET}"
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "Linux detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "macOS detected"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
    echo "Windows detected"
else
    echo -e "${BOLD}${RED}Unsupported operating system: $OSTYPE${RESET}"
    echo "Please download the appropriate binary from the GitHub releases page."
    exit 1
fi

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${BOLD}Creating installation directory: $INSTALL_DIR${RESET}"
    mkdir -p "$INSTALL_DIR"
fi

# Make sure installation directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "${BOLD}${YELLOW}Warning: $INSTALL_DIR is not in your PATH.${RESET}"
    echo "Adding it to your shell configuration..."
    
    # Detect shell and update configuration
    SHELL_CONFIG=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_CONFIG="$HOME/.profile"
    else
        echo -e "${BOLD}${YELLOW}Could not find shell configuration file.${RESET}"
        echo "Please add the following line to your shell configuration file:"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\""
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        echo "Updating $SHELL_CONFIG..."
        echo "" >> "$SHELL_CONFIG"
        echo "# Added by ServerInspect installer" >> "$SHELL_CONFIG"
        echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG"
        echo -e "${GREEN}Shell configuration updated.${RESET}"
        echo "Please run 'source $SHELL_CONFIG' to update your current session."
    fi
fi

# Download the latest release
if [ "$VERSION" = "latest" ]; then
    RELEASE_URL="https://api.github.com/repos/$GITHUB_REPO/releases/latest"
    echo -e "${BOLD}Fetching latest release...${RESET}"
    
    if command -v curl &> /dev/null; then
        VERSION=$(curl -s $RELEASE_URL | grep -o '"tag_name": "[^"]*' | cut -d'"' -f4)
    elif command -v wget &> /dev/null; then
        VERSION=$(wget -q -O- $RELEASE_URL | grep -o '"tag_name": "[^"]*' | cut -d'"' -f4)
    else
        echo -e "${BOLD}${RED}Error: Neither curl nor wget is installed.${RESET}"
        exit 1
    fi
    
    if [ -z "$VERSION" ]; then
        echo -e "${BOLD}${RED}Error: Could not determine latest version.${RESET}"
        echo "Please specify a version manually or check your internet connection."
        exit 1
    fi
    
    echo "Latest version: $VERSION"
fi

# Prepare download URL
BASE_URL="https://github.com/$GITHUB_REPO/releases/download/$VERSION"
if [ "$OS" = "linux" ]; then
    BINARY_URL="$BASE_URL/serverinspect-linux"
    BINARY_NAME="serverinspect"
elif [ "$OS" = "macos" ]; then
    BINARY_URL="$BASE_URL/serverinspect-macos"
    BINARY_NAME="serverinspect"
elif [ "$OS" = "windows" ]; then
    BINARY_URL="$BASE_URL/serverinspect-windows.exe"
    BINARY_NAME="serverinspect.exe"
fi

# Download the binary
echo -e "${BOLD}Downloading ServerInspect $VERSION for $OS...${RESET}"
if command -v curl &> /dev/null; then
    curl -L -o "$INSTALL_DIR/$BINARY_NAME" "$BINARY_URL"
elif command -v wget &> /dev/null; then
    wget -O "$INSTALL_DIR/$BINARY_NAME" "$BINARY_URL"
else
    echo -e "${BOLD}${RED}Error: Neither curl nor wget is installed.${RESET}"
    exit 1
fi

# Make binary executable
if [ "$OS" != "windows" ]; then
    chmod +x "$INSTALL_DIR/$BINARY_NAME"
fi

# Create si alias
if [ "$OS" != "windows" ]; then
    ln -sf "$INSTALL_DIR/$BINARY_NAME" "$INSTALL_DIR/si"
else
    cp "$INSTALL_DIR/$BINARY_NAME" "$INSTALL_DIR/si.exe"
fi

# Add shell aliases
if [ -n "$SHELL_CONFIG" ]; then
    echo "Adding shell aliases..."
    echo "# ServerInspect aliases" >> "$SHELL_CONFIG"
    echo "alias si='$INSTALL_DIR/si'" >> "$SHELL_CONFIG"
    echo "alias serverinspect='$INSTALL_DIR/serverinspect'" >> "$SHELL_CONFIG"
fi

echo -e "${BOLD}${GREEN}ServerInspect has been successfully installed!${RESET}"
echo ""
echo "You can now run it using one of these commands:"
echo "  serverinspect --help"
echo "  si --help"
echo ""
echo -e "${YELLOW}Note: You may need to restart your terminal or run 'source $SHELL_CONFIG' to use the command.${RESET}" 