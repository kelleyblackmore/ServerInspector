# ServerInspect - Ready-to-use container
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    procps \
    iproute2 \
    net-tools \
    iputils-ping \
    curl \
    wget \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files (only copying what exists)
COPY pyproject.toml ./
COPY README.md* ./
# LICENSE is optional
COPY LICENSE* ./
COPY src/ ./src/
COPY examples/ ./examples/

# Create config directory and a simple test file
RUN mkdir -p /config && \
    echo '---\nname: Simple Test\nchecks:\n  - name: Test Environment\n    type: command\n    command: "hostname"\n    exit_code: 0\nreport:\n  format: text\n  output: stdout' > /config/simple-test.yaml

# Modify pyproject.toml to remove test_types reference
RUN sed -i '/test_types/d' pyproject.toml

# Install serverinspect dependencies directly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir click>=8.1.0 jinja2>=3.1.0 paramiko>=3.1.0 \
    psutil>=5.9.0 pyyaml>=6.0.0 rich>=12.0.0

# Set up Python path to find the package
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Create volume for configs
VOLUME /config

# Create entrypoint script
RUN echo '#!/bin/sh\n\
if [ "$1" = "shell" ]; then\n\
  exec /bin/bash\n\
elif [ -z "$1" ]; then\n\
  echo "ServerInspect Container"\n\
  echo "Usage:"\n\
  echo "  docker run serverinspect run /config/FILE.yaml     # Run checks from a config file"\n\
  echo "  docker run serverinspect system-info               # Get system information"\n\
  echo "  docker run serverinspect shell                     # Start interactive shell"\n\
  echo ""\n\
  echo "Available commands:"\n\
  python -m serverinspect.cli --help\n\
else\n\
  exec python -m serverinspect.cli "$@"\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
