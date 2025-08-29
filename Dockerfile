# Use Python 3.11 slim image for better Python support
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    git \
    vim \
    tree \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt* ./

# Install Python dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy all files from current directory to container
COPY . .

# Set permissions for all files
RUN chmod -R 755 /app

# Create a script to read from all paths
RUN echo '#!/bin/bash' > /usr/local/bin/read-all-paths.sh && \
    echo 'find /app -type f -exec echo "=== {} ===" \; -exec cat {} \; -exec echo "" \;' >> /usr/local/bin/read-all-paths.sh && \
    chmod +x /usr/local/bin/read-all-paths.sh

# Expose port for Python applications
EXPOSE 8080

# Default command to read all paths
CMD ["/usr/local/bin/read-all-paths.sh"]
