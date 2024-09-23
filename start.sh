#!/bin/bash

# Generate the private key, certificate, and public key
openssl genpkey -algorithm RSA -out private_key.pem
openssl req -new -key private_key.pem -out cert.csr -subj "/CN=My Sign Server"
openssl x509 -req -days 365 -in cert.csr -signkey private_key.pem -out cert.pem
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Start Gunicorn with HTTPS (use cert.pem and private_key.pem for SSL)
gunicorn -w 4 -b 0.0.0.0:443 --certfile=cert.pem --keyfile=private_key.pem app:app
