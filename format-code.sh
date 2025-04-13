#!/bin/bash
#
# Format Python code to match the style requirements
#

set -e

echo "🔍 Formatting Python code with Black..."

# Check if Black is installed
if ! command -v black &> /dev/null; then
    echo "Installing Black code formatter..."
    pipx install black
fi

# Run Black on the code
black .

echo "✅ Code formatting complete!" 