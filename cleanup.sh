#!/bin/bash
#
# ServerInspect Repository Cleanup Script
#

set -e

echo "🧹 Cleaning up ServerInspect repository..."

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# Remove virtual environments
echo "Removing virtual environments..."
rm -rf venv/
rm -rf .venv/
rm -rf .venv~/
rm -rf ENV/

# Remove test cache
echo "Removing test cache..."
rm -rf .pytest_cache/
rm -rf .coverage
rm -rf coverage.xml
rm -rf htmlcov/

# Remove IDE files
echo "Removing IDE files..."
rm -rf .idea/
rm -rf .vscode/

# Remove temporary files
echo "Removing temporary files..."
find . -name "*.swp" -delete
find . -name "*.swo" -delete
find . -name "*~" -delete
find . -name ".DS_Store" -delete
find . -name "Thumbs.db" -delete

# Remove Replit specific files (if you don't need them)
echo "Removing Replit specific files..."
rm -f replit.nix
rm -f .replit
rm -rf .pythonlibs/

# Remove lock files
echo "Removing lock files..."
rm -f uv.lock

echo "✅ Cleanup complete!"
echo ""
echo "NOTE: If you want to keep some of these files, you should edit this script"
echo "      before running it again, or restore them from version control." 