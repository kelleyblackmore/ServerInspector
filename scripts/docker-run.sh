#!/bin/bash
# Quick start script for ServerInspect Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if the image exists, build if needed
if ! docker image inspect serverinspect:latest &>/dev/null; then
    echo "ServerInspect image not found, building..."
    docker build -t serverinspect:latest -f docker/Dockerfile .
fi

# Ensure config directory exists
mkdir -p config

# Check if we have an example config
if [ ! -f "config/example.yaml" ]; then
    echo "Creating example configuration in config/example.yaml"
    cat > config/example.yaml << EOL
---
name: Basic System Check
description: Basic checks to validate system configuration

checks:
  - name: Check System Hostname
    type: command
    command: hostname
    exit_code: 0

  - name: Check OS Information
    type: file
    path: /etc/os-release
    exists: true

  - name: Check Kernel Version
    type: command
    command: uname -r
    exit_code: 0

  - name: Check Root Directory Permissions
    type: command
    command: ls -ld /
    exit_code: 0
    contains: "drwxr-xr-x"

report:
  title: "Basic System Check Results"
  format: text
  output: stdout
EOL
fi

# If no arguments provided, run the example
if [ $# -eq 0 ]; then
    echo "Running ServerInspect with example configuration"
    docker run -v "$(pwd)"/config:/config \
               -v /etc:/host/etc:ro \
               -v /var/log:/host/var/log:ro \
               -v /proc:/host/proc:ro \
               serverinspect run /config/example.yaml
else
    # Otherwise pass arguments to serverinspect
    docker run -v "$(pwd)"/config:/config \
               -v /etc:/host/etc:ro \
               -v /var/log:/host/var/log:ro \
               -v /proc:/host/proc:ro \
               serverinspect "$@"
fi
