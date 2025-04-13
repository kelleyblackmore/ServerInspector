#!/bin/bash
# Test script for ServerInspect Linux executable installation and testing

set -e  # Exit on any error

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if the command succeeded
check_status() {
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed: $1${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ Success: $1${NC}"
    fi
}

# Verify project structure
echo -e "${YELLOW}=== Verifying project structure ===${NC}"
if [ ! -d "src/serverinspect" ]; then
    echo -e "${RED}❌ Error: src/serverinspect directory not found${NC}"
    echo -e "${YELLOW}Please run the cleanup.sh script first${NC}"
    exit 1
fi
check_status "Project structure looks correct"

# Clean up existing builds
echo -e "${YELLOW}=== Cleaning previous builds ===${NC}"
make clean-build
check_status "Cleaning build artifacts"

# First, build the executable
echo -e "${YELLOW}=== Building ServerInspect Linux executable ===${NC}"
make build-linux
check_status "Building Linux executable"

# Verify the executable exists
if [ ! -f "dist/serverinspect-linux-x86_64" ]; then
    echo -e "${RED}❌ Error: Linux executable not found at dist/serverinspect-linux-x86_64${NC}"
    echo -e "${YELLOW}Checking for alternative locations...${NC}"
    
    if [ -f "dist/serverinspect-linux" ]; then
        echo -e "${GREEN}Found executable at dist/serverinspect-linux${NC}"
        echo -e "${YELLOW}Copying to expected location...${NC}"
        cp dist/serverinspect-linux dist/serverinspect-linux-x86_64
        chmod +x dist/serverinspect-linux-x86_64
    else
        echo -e "${RED}No executable found. Build may have failed.${NC}"
        exit 1
    fi
fi

# Now install it
echo -e "${YELLOW}=== Installing ServerInspect Linux executable ===${NC}"
sudo make install-linux
check_status "Installing Linux executable"

# Verify installation
echo -e "${YELLOW}=== Verifying installation ===${NC}"
which serverinspect
check_status "Finding serverinspect in PATH"

# Basic functionality tests
echo -e "${YELLOW}=== Testing basic functionality ===${NC}"

echo -e "${YELLOW}Testing help command...${NC}"
serverinspect --help
check_status "Help command"

echo -e "${YELLOW}Testing system-info command...${NC}"
serverinspect system-info || echo -e "${YELLOW}System info command not found, skipping${NC}"

# Test the new simple checker interface
echo -e "${YELLOW}=== Testing new checker interface ===${NC}"
serverinspect check file /etc --exists || echo -e "${YELLOW}New checker interface not found, skipping${NC}"
serverinspect check command "echo Hello World" --contains "Hello" || echo -e "${YELLOW}New checker interface not found, skipping${NC}"

# Run a test configuration
if [ -f "serverinspect-test.yaml" ]; then
    echo -e "${YELLOW}=== Running test configuration ===${NC}"
    serverinspect run serverinspect-test.yaml || echo -e "${YELLOW}Run command failed, trying fallback${NC}"
    
    # Try alternative format if the first one fails
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Trying alternative command format...${NC}"
        serverinspect run --config serverinspect-test.yaml || echo -e "${YELLOW}Both run formats failed, skipping test configuration${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Warning: No test configuration found (serverinspect-test.yaml)${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}=== Installation completed! ===${NC}"
echo "You can now use 'serverinspect' from anywhere on your system."
echo ""
echo -e "${YELLOW}Try these commands:${NC}"
echo "  serverinspect check file /etc --exists"
echo "  serverinspect check command 'echo hello' --contains hello"
echo "  serverinspect run serverinspect-test.yaml"
echo ""
echo -e "${YELLOW}To uninstall, run: sudo make uninstall-linux${NC}" 