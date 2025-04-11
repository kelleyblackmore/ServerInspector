# ServerInspect Makefile
# Handles dependencies, testing, and building

.PHONY: all install dev-install clean test build-exe run help docker-build

# Default target
all: help

# Project settings
PROJECT_NAME = serverinspect
PYTHON = python3
PIP = pip3
PYTEST = pytest
PYINSTALLER = pyinstaller

# Installation
install:
	@echo "Installing $(PROJECT_NAME)..."
	$(PIP) install -e .

dev-install:
	@echo "Installing $(PROJECT_NAME) in development mode with testing dependencies..."
	$(PIP) install -e ".[dev,test]"
	@echo "You might need to install additional system dependencies:"
	@echo "  apt-get install python3-dev (for PyInstaller)"

# Dependencies
deps:
	@echo "Installing runtime dependencies..."
	$(PIP) install click rich pyyaml jinja2 paramiko psutil

dev-deps: deps
	@echo "Installing development dependencies..."
	$(PIP) install pytest pytest-cov flake8 pylint pyinstaller

# Testing
test:
	@echo "Running tests..."
	$(PYTEST)

lint:
	@echo "Running linters..."
	flake8 $(PROJECT_NAME)
	pylint $(PROJECT_NAME)

# Building
build-exe:
	@echo "Building executable with PyInstaller..."
	@if ! which $(PYINSTALLER) > /dev/null; then \
		echo "PyInstaller not found. Installing..."; \
		$(PIP) install pyinstaller; \
	fi
	# Try to install required development libraries if they're missing
	@if [ -f /etc/apt/sources.list ]; then \
		echo "Debian/Ubuntu system detected. Installing Python dev packages if missing..."; \
		sudo apt-get update || true; \
		sudo apt-get install -y python3-dev || true; \
	fi
	$(PYINSTALLER) serverinspect.spec --clean

# Docker build (more reliable for executable creation)
docker-build:
	@echo "Building executable with Docker (more reliable)..."
	docker build -t $(PROJECT_NAME)-builder -f Dockerfile.build .
	docker run --rm -v $(PWD)/dist:/output $(PROJECT_NAME)-builder cp -r /app/dist/* /output/
	@echo "Executable created in ./dist directory"

# Running
run:
	@echo "Running $(PROJECT_NAME)..."
	$(PYTHON) main.py

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf build/ dist/ *.spec __pycache__/ .pytest_cache/ .coverage htmlcov/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

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
	@echo "  make build-exe    - Build standalone executable with PyInstaller"
	@echo "  make docker-build - Build executable using Docker (more reliable)"
	@echo "  make run          - Run the application"
	@echo "  make clean        - Clean up build artifacts"
	@echo "  make help         - Show this help message"