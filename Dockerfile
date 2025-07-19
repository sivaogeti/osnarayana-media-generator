FROM python:3.12-slim

# Install OS dependencies for Pillow and others
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirement files first for caching
COPY requirements.txt .

# Install Python dependencies directly (no venv)
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Run Streamlit on port 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
