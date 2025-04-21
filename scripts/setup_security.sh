#!/bin/bash
# Setup script for security tools in ServerInspect

set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}Setting up security tools for ServerInspect${RESET}"
echo "=========================================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found.${RESET}"
    exit 1
fi

# Install pre-commit and security tools
echo -e "Installing pre-commit and security tools..."
pipx install pre-commit detect-secrets bandit safety

# Install pre-commit hooks
echo -e "Installing pre-commit hooks..."
pre-commit install

# Generate or update secrets baseline
if [ ! -f .secrets.baseline ]; then
    echo -e "Generating secrets baseline..."
    detect-secrets scan > .secrets.baseline
    echo -e "${YELLOW}Please review .secrets.baseline and commit it to your repository.${RESET}"
else
    echo -e "Updating secrets baseline..."
    # Remove old baseline and create a new one
    rm .secrets.baseline
    detect-secrets scan > .secrets.baseline
fi

# Run initial pre-commit checks
echo -e "Running initial pre-commit checks..."
pre-commit run --all-files || {
    echo -e "${YELLOW}Some pre-commit checks failed. Please fix the issues before committing.${RESET}"
}

echo ""
echo -e "${GREEN}${BOLD}Security tools setup complete!${RESET}"
echo ""
echo "You can now:"
echo "  • Commit code with automatic security checks"
echo "  • Run 'safety check' to scan dependencies"
echo "  • Run 'bandit -r src/' to manually scan code"
echo ""
echo -e "${YELLOW}Note: Remember to add .secrets.baseline to your git repository.${RESET}"
