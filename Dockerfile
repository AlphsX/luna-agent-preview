# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PostgreSQL client and compilation
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY . .

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Expose Streamlit port
EXPOSE 8501

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Install curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Command to run the Streamlit application
CMD ["streamlit", "run", "src/app/luna_agent_preview.py", "--server.port", "8501", "--server.address", "0.0.0.0"]