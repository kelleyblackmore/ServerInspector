#!/bin/bash
#
# Format Python code to match the style requirements
#

set -e

echo "🔍 Formatting Python code..."

# Check if formatters are installed
if ! command -v black &> /dev/null || ! command -v isort &> /dev/null; then
    echo "Installing code formatters..."
    pip install black isort
fi

# Format the code
echo "Running Black formatter..."
black .

echo "Running isort formatter..."
isort --profile black .

echo "✅ Code formatting complete!" 