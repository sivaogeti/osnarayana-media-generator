# Use stable Python image
FROM python:3.10

# Install OS dependencies for Pillow and others
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirement files first for caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app files
COPY . /app

# Expose port (the port is dynamic and set by the platform, but 8000 is a good fallback)
EXPOSE 8000

# Create a script to start Streamlit with dynamic PORT
RUN echo '#!/bin/bash\n\
export PORT=${PORT:-8000}\n\
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0' > /start.sh && chmod +x /start.sh

# Run the script
CMD ["/start.sh"]
