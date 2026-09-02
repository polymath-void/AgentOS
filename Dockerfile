# Base Image: Minimal Debian-based glibc environment for manylinux wheel compatibility
FROM python:3.10-slim-bullseye

# Environment Variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /app

# Upgrade pip to ensure proper manylinux wheel resolution
RUN pip install --upgrade pip

# Copy dependency configuration and install
COPY pyproject.toml .
RUN pip install .

# Copy the AgentOS ecosystem files
COPY agentos/ ./agentos/
COPY tests/ ./tests/

# Expose ports for WebRTC (UDP) and ZeroMQ (TCP) if not using host networking
EXPOSE 5555/tcp 5556/tcp 5557/tcp 5558/tcp 8765/tcp
EXPOSE 20000-20100/udp

# Execution Command
CMD ["python", "agentos/orchestration/kernel.py"]
