# Use an official Python runtime as a parent image
FROM python:3.12.6-alpine3.20

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apk update && \
    apk add --no-cache bash openssl build-base libffi-dev && \
    rm -rf /var/cache/apk/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the application code and start script
COPY app.py .
COPY start.sh .

# Convert Windows line endings to Unix line endings (if necessary)
RUN sed -i 's/\r$//' start.sh

# Make start.sh executable
RUN chmod +x start.sh

# Expose the HTTPS port
EXPOSE 443

# Run the start.sh script to generate keys and start Gunicorn with HTTPS
CMD ["./start.sh"]
