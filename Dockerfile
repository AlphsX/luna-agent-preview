# Use a lightweight base image
FROM alpine:latest

# Set working directory
WORKDIR /app

# Install necessary tools
RUN apk add --no-cache \
    bash \
    curl \
    git \
    vim \
    tree

# Copy all files from current directory to container
COPY . .

# Set permissions for all files
RUN chmod -R 755 /app

# Create a script to read from all paths
RUN echo '#!/bin/bash' > /usr/local/bin/read-all-paths.sh && \
    echo 'find /app -type f -exec echo "=== {} ===" \; -exec cat {} \; -exec echo "" \;' >> /usr/local/bin/read-all-paths.sh && \
    chmod +x /usr/local/bin/read-all-paths.sh

# Expose port (if needed)
EXPOSE 8080

# Default command to read all paths
CMD ["/usr/local/bin/read-all-paths.sh"]
