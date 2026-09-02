# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Set the working directory in the container
WORKDIR /app

# Copy the source code into the container
COPY src/ /app/src/

# Expose the default mesh network port
EXPOSE 5000

# Run the neural agent engine when the container launches
CMD ["python", "src/main.py"]
