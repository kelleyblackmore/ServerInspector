# serverinspector Docker Files

This directory contains Docker-related files for building and running serverinspector in containers.

## Files

- **Dockerfile** - Main Dockerfile for running serverinspector
- **Dockerfile.build** - Multi-platform build environment for creating executables
- **docker-compose.yml** - Docker Compose configuration for easy deployment
- **README-docker.md** - Detailed Docker usage documentation

## Quick Start

### Build the Docker Image

```bash
docker build -t serverinspector:latest -f docker/Dockerfile .
```

Or use the convenience script:

```bash
bash scripts/docker-build.sh
```

### Run with Docker

```bash
# Run a test configuration
docker run -v $(pwd)/config:/config serverinspector run /config/example.yaml

# Collect system information
docker run serverinspector system-info

# Perform a quick check
docker run serverinspector check file /etc/hosts --exists
```

### Using Docker Compose

```bash
docker-compose -f docker/docker-compose.yml up
```

## Documentation

For complete Docker usage instructions, see [README-docker.md](README-docker.md).
