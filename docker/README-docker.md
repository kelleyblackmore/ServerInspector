# ServerInspect Docker Usage

This document explains how to use ServerInspect with Docker for simplified deployment.

## About This Container

This Docker container is designed to run ServerInspect without
installing it on your system. The container:

1. Automatically removes any references to the deprecated `test_types` module
2. Uses the new `checkers` module instead
3. Sets up the Python environment correctly to run ServerInspect

## Quick Start

```bash
# Run the included quick-start script
./scripts/docker-run.sh

# Or run a specific command
./scripts/docker-run.sh run /config/simple-test.yaml
```

### Using Docker directly

```bash
# Build the image
docker build -t serverinspect .

# Run the simple test
docker run serverinspect run /config/simple-test.yaml

# Get system information
docker run serverinspect system-info

# Run in interactive mode
docker run -it serverinspect shell
```

### Using Docker Compose

```bash
# Build and run with docker-compose
docker-compose build
docker-compose run serverinspect run /config/simple-test.yaml

# Run with a custom configuration file
docker-compose run -v $(pwd)/my-checks.yaml:/config/my-checks.yaml \
serverinspect run /config/my-checks.yaml
```

## Accessing Host System

The container is configured to access parts of the host system through mounted volumes:

- `/host/etc` - Host's `/etc` directory (read-only)
- `/host/var/log` - Host's log files (read-only)
- `/host/proc` - Host's process information (read-only)

For file checks against the host system, prefix paths with
`/host` in your configuration files:

```yaml
checks:
  - name: Check Host Password File
    type: file
    path: /host/etc/passwd
    exists: true
```

## Using Configuration Files

1. Create a `config` directory in your project
2. Place your YAML configuration files in this directory
3. They will be available at `/config` inside the container

Example:

```bash
# Use with absolute paths to avoid Docker volume mounting issues
docker run -v $(pwd)/config:/config serverinspect run /config/docker-example.yaml
```

## Available Commands

The container supports the following commands:

```bash
# Run checks from a configuration file
docker run serverinspect run /config/my-config.yaml

# Get system information
docker run serverinspect system-info

# Initialize a new configuration file (outputs to current directory)
docker run -v $(pwd):/output serverinspect init

# Start an interactive shell
docker run -it serverinspect shell
```

## Pre-built Example

A Docker example configuration file is included in the container at
`/config/simple-test.yaml`:

```bash
# Run the included sample test
docker run serverinspect run /config/simple-test.yaml
```

## Extending the Container

To create a custom container with your own configuration files:

```dockerfile
FROM serverinspect:latest

# Add your configuration files
COPY my-config.yaml /config/

# Set a default command
CMD ["run", "/config/my-config.yaml"]
```

## Troubleshooting

- **File not found errors**: When mounting volumes, make sure you're using
  absolute paths:

  ```bash
  # WRONG: May not work in all environments
  docker run -v ./config:/config serverinspect ...

  # RIGHT: Use absolute paths
  docker run -v $(pwd)/config:/config serverinspect ...
  ```

- **Permission issues**: If you encounter permission problems, you may need to:

  ```bash
  # Give read permissions to files
  chmod -R o+r config/
  ```

- **Adding tools**: If you need additional system tools:

  ```bash
  docker run -it serverinspect shell
  apt-get update && apt-get install -y <package-name>
  ```
