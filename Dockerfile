# Use slim Python image
FROM python:3.11-slim

# Install only the required system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        build-essential \
        default-libmysqlclient-dev \
        libcairo2-dev \
        libpango1.0-dev \
        libgdk-pixbuf2.0-dev \
        libffi-dev \
        libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all app code
COPY . .

# Command to start your Django app
CMD ["gunicorn", "MoviesPro.wsgi:application", "--bind", "0.0.0.0:8000"]