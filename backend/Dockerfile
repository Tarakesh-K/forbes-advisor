# Use the specific Python 3.12.3 slim image for a smaller footprint
FROM python:3.12.3-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
# - libpq-dev: Required for PostgreSQL (psycopg2)
# - gcc: Required to compile Python packages with C extensions
# - netcat-openbsd: Useful for 'wait-for-it' scripts to check DB readiness
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# (Optional) Expose the port Django runs on
EXPOSE 8000