#!/bin/bash
# Install the package in development mode

set -e

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install the package in development mode
echo "Installing ServerInspect in development mode..."
pip install -e .

echo "Installation complete."
echo "To activate the virtual environment, run: source venv/bin/activate"
echo "Then you can run 'serverinspect' commands." 