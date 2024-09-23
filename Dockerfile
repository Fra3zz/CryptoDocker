FROM python:3.12.6-alpine3.20

# Set the working directory
WORKDIR /app/

# Copy the requirements and app files
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY start.sh start.sh

# Install dependencies including Gunicorn, OpenSSL, and bash
RUN pip install -r requirements.txt && \
    apk add --no-cache bash openssl && \
    chmod +x start.sh

# Expose the HTTPS port (443)
EXPOSE 443

# Run the start.sh script to start Gunicorn with HTTPS
CMD [ "bash", "start.sh" ]
