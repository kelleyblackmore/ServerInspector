# Integration Tests

This directory contains a comprehensive multi-OS integration test suite for serverinspector.

## Overview

The test suite validates serverinspector functionality across 7 different Linux distributions:

- **Ubuntu 24.04** - apt/dpkg + systemd
- **Debian 12** - apt/dpkg + systemd  
- **Fedora 40** - dnf/rpm + systemd
- **CentOS Stream 9** - dnf/yum/rpm + systemd
- **Alpine 3.19** - apk + OpenRC
- **Arch Linux** - pacman + systemd
- **openSUSE Tumbleweed** - zypper/rpm + systemd

## Directory Structure

```
tests/integration/
├── Dockerfile.ubuntu         # Ubuntu test container
├── Dockerfile.debian         # Debian test container
├── Dockerfile.fedora         # Fedora test container
├── Dockerfile.centos         # CentOS test container
├── Dockerfile.alpine         # Alpine test container
├── Dockerfile.arch           # Arch Linux test container
├── Dockerfile.opensuse       # openSUSE test container
├── docker-compose.yml        # Container orchestration
├── run_tests.py             # Test runner script
├── configs/                 # Test configurations
│   ├── common-tests.yaml    # Tests for all distributions
│   ├── ubuntu-tests.yaml    # Ubuntu-specific tests
│   ├── debian-tests.yaml    # Debian-specific tests
│   ├── fedora-tests.yaml    # Fedora-specific tests
│   ├── centos-tests.yaml    # CentOS-specific tests
│   ├── alpine-tests.yaml    # Alpine-specific tests
│   ├── arch-tests.yaml      # Arch-specific tests
│   └── opensuse-tests.yaml  # openSUSE-specific tests
└── results/                 # Test result outputs
```

## Quick Start

### 1. Build and Start Containers

```bash
cd tests/integration
docker compose build
docker compose up -d
```

Wait for all containers to be healthy:
```bash
docker compose ps
```

### 2. Run Tests

Run all tests across all distributions:
```bash
./run_tests.py
```

Run tests for specific distributions:
```bash
./run_tests.py --distributions ubuntu debian fedora
```

List available distributions:
```bash
./run_tests.py --list
```

### 3. View Results

Results are saved in the `results/` directory with timestamps:
- `test_results_YYYYMMDD_HHMMSS.json`
- `test_results_YYYYMMDD_HHMMSS.yaml`

## Container Details

### SSH Access

All containers run SSH servers on mapped ports:
- **Ubuntu**: localhost:2201
- **Debian**: localhost:2202
- **Fedora**: localhost:2203
- **CentOS**: localhost:2204
- **Alpine**: localhost:2205
- **Arch**: localhost:2206
- **openSUSE**: localhost:2207

Credentials:
- **Root**: `root` / `testpass`
- **User**: `testuser` / `testpass`

### Network Configuration

- Network: `serverinspector-net` (172.20.0.0/16)
- Static IPs: 172.20.0.11 - 172.20.0.17
- All containers can communicate with each other

### Manual SSH Testing

```bash
# Test Ubuntu container
ssh -p 2201 testuser@localhost
# Password: testpass

# Test Debian container
ssh -p 2202 testuser@localhost

# etc...
```

## Test Configuration Files

### common-tests.yaml

Tests that work across all distributions:
- Basic system information (hostname, kernel, uptime)
- File system operations
- Process checks
- Network connectivity
- Standard UNIX commands

### Distribution-Specific Tests

Each distribution has its own test file validating:
- **Package manager** functionality (install detection, version queries)
- **Service manager** functionality (systemd or OpenRC)
- **Distribution-specific** files and configurations
- **Network services** (nginx/apache/httpd)
- **Port listening** checks

## What Gets Tested

### Package Managers (17 total)
- apt, dpkg (Ubuntu, Debian)
- dnf, yum, rpm (Fedora, CentOS, openSUSE)
- apk (Alpine)
- pacman (Arch)
- zypper (openSUSE)

### Service Managers
- systemd (Ubuntu, Debian, Fedora, CentOS, Arch, openSUSE)
- OpenRC (Alpine)

### Features Validated
- ✅ Package installation detection
- ✅ Package version queries
- ✅ Service status checks
- ✅ Service management commands
- ✅ Port listening detection
- ✅ File existence checks
- ✅ File content validation
- ✅ Process detection
- ✅ Network connectivity
- ✅ System information gathering

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker compose logs ubuntu
docker compose logs debian

# Rebuild containers
docker compose down
docker compose build --no-cache
docker compose up -d
```

### SSH connection refused
```bash
# Check if SSH is running in container
docker compose exec ubuntu systemctl status ssh

# Check port mapping
docker compose ps

# Wait for health checks
docker compose ps --format json | jq '.[].Health'
```

### Tests failing
```bash
# Run serverinspector manually against a container
serverinspector \
  --config configs/ubuntu-tests.yaml \
  --ssh-host localhost \
  --ssh-port 2201 \
  --ssh-user testuser \
  --ssh-password testpass \
  --format terminal

# Check container state
docker compose exec ubuntu systemctl status nginx
docker compose exec ubuntu apt list --installed
```

### Clean restart
```bash
# Stop and remove everything
docker compose down -v

# Rebuild from scratch
docker compose build --no-cache
docker compose up -d

# Wait for containers to be healthy
sleep 30

# Run tests
./run_tests.py
```

## Extending the Test Suite

### Adding a New Distribution

1. Create `Dockerfile.newdistro`:
```dockerfile
FROM newdistro:version
# Install SSH, package manager tools, test services
# Configure test data
```

2. Add to `docker-compose.yml`:
```yaml
newdistro:
  build:
    context: .
    dockerfile: Dockerfile.newdistro
  ports:
    - "2208:22"
  networks:
    serverinspector-net:
      ipv4_address: 172.20.0.18
```

3. Create `configs/newdistro-tests.yaml` with distribution-specific tests

4. Add to `DISTRIBUTIONS` dict in `run_tests.py`

### Adding New Tests

Edit the appropriate YAML config file:
```yaml
test_groups:
  - name: "My New Tests"
    tests:
      - name: "Test Name"
        type: command|file|service|package|port|process
        # test-specific parameters
        expected: value
        description: "What this test validates"
```

## CI/CD Integration

The test suite can be integrated into CI/CD pipelines:

```bash
#!/bin/bash
# CI test script
set -e

# Start containers
docker compose up -d

# Wait for health
timeout 60 bash -c 'until docker compose ps --format json | jq -e ".[] | select(.Health == \"healthy\")" > /dev/null 2>&1; do sleep 2; done'

# Run tests
./run_tests.py --distributions ubuntu debian fedora

# Check results
EXIT_CODE=$?

# Cleanup
docker compose down -v

exit $EXIT_CODE
```

## Performance

Expected test times (approximate):
- **Per distribution**: 30-60 seconds
- **All 7 distributions**: 4-7 minutes
- **Common tests only**: 15-30 seconds per distribution

Factors affecting speed:
- Container startup time
- SSH connection establishment
- Number of tests per distribution
- System resources (CPU, disk I/O)

## License

Same as serverinspector project.
