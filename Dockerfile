# Use official Python image
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run Streamlit on dynamic port
CMD ["sh", "-c", "streamlit run app.py --server.port=8000 --server.address=0.0.0.0"]
