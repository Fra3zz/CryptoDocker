# Generate the private key without encryption
openssl genpkey -algorithm RSA -out private_key.pem

# Generate a certificate signing request (CSR)
openssl req -new -key private_key.pem -out cert.csr -subj "/CN=localhost"

# Generate a self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in cert.csr -signkey private_key.pem -out cert.pem

# Extract the public key from the private key
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Run your Python app
python ./app.py
