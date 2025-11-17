# serverinspector Makefile
# Handles dependencies, testing, and building

.PHONY: all install dev-install clean test build-exe build-windows build-linux build-macos run help docker-build install-linux test-linux clean-build

# Default target
all: help

# Project settings
PROJECT_NAME = serverinspector
DOCKER_IMAGE = $(PROJECT_NAME)-builder
INSTALL_DIR = /usr/local/bin
CONFIG_DIR = /etc/serverinspector

# Installation
install:
	@echo "Installing $(PROJECT_NAME)..."
	pip install -e .

dev-install:
	@echo "Installing $(PROJECT_NAME) in development mode with testing dependencies..."
	pip install -e ".[dev,test]"

# Dependencies
deps:
	@echo "Installing runtime dependencies..."
	pip install click rich pyyaml jinja2 paramiko psutil

dev-deps: deps
	@echo "Installing development dependencies..."
	pip install pytest pytest-cov flake8 pylint pyinstaller

# Testing
test:
	@echo "Running tests..."
	pytest

lint:
	@echo "Running linters..."
	flake8 $(PROJECT_NAME)
	pylint $(PROJECT_NAME)

# Clean build directories
clean-build:
	@echo "Cleaning build directories..."
	rm -rf dist/$(PROJECT_NAME)* build/$(PROJECT_NAME)* *.spec

# Building
build-exe: clean-build
	@echo "Building executable for current platform..."
	docker run --rm -v $(PWD):/app -w /app $(DOCKER_IMAGE) --platform linux

build-windows: clean-build
	@echo "Building Windows executable..."
	docker run --rm -v $(PWD):/app -w /app $(DOCKER_IMAGE) --platform windows

build-linux: clean-build
	@echo "Building Linux executable..."
	docker run --rm -v $(PWD):/app -w /app $(DOCKER_IMAGE) --platform linux

build-macos: clean-build
	@echo "Building macOS executable..."
	docker run --rm -v $(PWD):/app -w /app $(DOCKER_IMAGE) --platform macos

# Docker build setup
docker-build:
	@echo "Building Docker image for cross-platform builds..."
	docker build -t $(DOCKER_IMAGE) -f docker/Dockerfile.build .
	@echo "Docker image built successfully. You can now use:"
	@echo "  make build-windows  - Build Windows executable"
	@echo "  make build-linux    - Build Linux executable"
	@echo "  make build-macos    - Build macOS executable"

# Running
run:
	@echo "Running $(PROJECT_NAME)..."
	python src/main.py

# Install Linux executable
install-linux:
	@echo "Installing $(PROJECT_NAME) Linux executable..."
	@if [ ! -f dist/serverinspector-linux-x86_64 ]; then \
		echo "Linux executable not found. Run 'make build-linux' first."; \
		exit 1; \
	fi
	@echo "Installing to $(INSTALL_DIR)/serverinspector..."
	sudo install -m 755 dist/serverinspector-linux-x86_64 $(INSTALL_DIR)/serverinspector
	@echo "Creating config directory at $(CONFIG_DIR)..."
	sudo mkdir -p $(CONFIG_DIR)
	@if [ -d examples ]; then \
		echo "Copying example configurations..."; \
		sudo cp -r examples/* $(CONFIG_DIR)/; \
	fi
	@echo "Installation complete. You can now run 'serverinspector' from anywhere."

# Test the installed Linux executable
test-linux:
	@echo "Testing the installed Linux executable..."
	@if ! command -v serverinspector >/dev/null 2>&1; then \
		echo "serverinspector executable not found in PATH. Run 'make install-linux' first."; \
		exit 1; \
	fi
	@echo "Running basic tests..."
	serverinspector --version
	serverinspector --help
	@echo "Testing example configuration..."
	@if [ -f "serverinspector-test.yaml" ]; then \
		serverinspector run --config serverinspector-test.yaml --dry-run; \
	else \
		echo "No test configuration found. Create a serverinspector-test.yaml file for complete testing."; \
	fi
	@echo "Test complete."

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf build/ dist/ *.spec __pycache__/ .pytest_cache/ .coverage htmlcov/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	docker rmi $(DOCKER_IMAGE) 2>/dev/null || true

# Uninstall
uninstall-linux:
	@echo "Uninstalling $(PROJECT_NAME) Linux executable..."
	sudo rm -f $(INSTALL_DIR)/serverinspector
	@echo "Would you like to remove the configuration directory at $(CONFIG_DIR)? [y/N] "
	@read -r response; \
	if [ "$$response" = "y" ] || [ "$$response" = "Y" ]; then \
		sudo rm -rf $(CONFIG_DIR); \
		echo "Configuration directory removed."; \
	else \
		echo "Configuration directory preserved."; \
	fi
	@echo "Uninstallation complete."

# Help
help:
	@echo "$(PROJECT_NAME) Makefile"
	@echo "---------------------"
	@echo "Available targets:"
	@echo "  make install      - Install the package"
	@echo "  make dev-install  - Install the package in development mode"
	@echo "  make deps         - Install runtime dependencies"
	@echo "  make dev-deps     - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make docker-build - Build Docker image for cross-platform builds"
	@echo "  make clean-build  - Clean build directories"
	@echo "  make build-exe    - Build executable for current platform"
	@echo "  make build-windows - Build Windows executable"
	@echo "  make build-linux   - Build Linux executable"
	@echo "  make build-macos   - Build macOS executable"
	@echo "  make install-linux - Install Linux executable to $(INSTALL_DIR)"
	@echo "  make test-linux   - Test the installed Linux executable"
	@echo "  make uninstall-linux - Uninstall the Linux executable"
	@echo "  make run          - Run the application"
	@echo "  make clean        - Clean up build artifacts"
	@echo "  make help         - Show this help message"
