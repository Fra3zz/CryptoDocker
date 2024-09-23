#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define file paths
PRIVATE_KEY="private_key.pem"
CERT_CSR="cert.csr"
CERT_PEM="cert.pem"
PUBLIC_KEY="public_key.pem"

# Generate the private key
openssl genpkey -algorithm RSA -out "$PRIVATE_KEY" -pkeyopt rsa_keygen_bits:2048

# Generate a certificate signing request (CSR)
openssl req -new -key "$PRIVATE_KEY" -out "$CERT_CSR" -subj "/CN=My Sign Server"

# Generate a self-signed certificate valid for 365 days
openssl x509 -req -days 365 -in "$CERT_CSR" -signkey "$PRIVATE_KEY" -out "$CERT_PEM"

# Extract the public key from the private key
openssl rsa -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY"

# Secure the private key and public key files
chmod 600 "$PRIVATE_KEY" "$PUBLIC_KEY" "$CERT_PEM"

# Start Gunicorn with HTTPS
exec gunicorn --certfile="$CERT_PEM" --keyfile="$PRIVATE_KEY" -b 0.0.0.0:443 app:app
