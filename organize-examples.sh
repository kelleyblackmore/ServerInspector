#!/bin/bash
#
# Script to organize ServerInspect examples
#

set -e

echo "📂 Organizing example files..."

# Create subdirectories
mkdir -p examples/configs
mkdir -p examples/results
mkdir -p examples/templates

# Move configuration examples
mv examples/basic_test.yaml examples/configs/
mv examples/comprehensive_test.yaml examples/configs/
mv examples/ssh_test.yaml examples/configs/
mv examples/variable_test.yaml examples/configs/
mv examples/system_info.yaml examples/configs/

# Move results
mv examples/results.json examples/results/
mv examples/results.yaml examples/results/

echo "✅ Examples organized!" 