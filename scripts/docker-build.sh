#!/bin/bash
# Build the serverinspector Docker image

set -e

# Create config directory if it doesn't exist
mkdir -p config

# Copy the example config file if it doesn't exist
if [ ! -f config/docker-example.yaml ]; then
    echo "Copying example configuration to config/docker-example.yaml"
    cp -n config/docker-example.yaml config/ 2>/dev/null || true
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

echo "Building serverinspector Docker image..."
docker build -t serverinspector:latest -f docker/Dockerfile .

echo "Successfully built serverinspector Docker image"
echo "You can now use it with commands like:"
echo "  docker run serverinspector check file /etc/hosts --exists"
echo "  docker run -v $(pwd)/config:/config serverinspector run /config/docker-example.yaml"
echo ""
echo "For more information, see docker/README-docker.md"
