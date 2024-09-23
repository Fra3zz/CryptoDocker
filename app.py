from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
import base64
import datetime
import os

app = Flask(__name__)


# Directory where uploaded files will be stored (adjust this as needed)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Path to store the uploaded certificate and key
CERT_FILE_PATH = os.path.join(UPLOAD_FOLDER, 'cert.pem')
KEY_FILE_PATH = os.path.join(UPLOAD_FOLDER, 'private_key.pem')

# Public key storage (could be more sophisticated, but for simplicity, we're replacing a global key)
PUBLIC_KEY_FILE_PATH = os.path.join(UPLOAD_FOLDER, 'public_key.pem')


# Simple HTML form to upload the certificate and key
@app.route('/upload')
def upload_form():
    return '''
    <!doctype html>
    <title>Upload Certificate and Key</title>
    <h1>Upload Your Certificate and Key</h1>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <label for="cert">Upload Certificate (PEM format):</label><br>
        <input type="file" name="cert" required><br><br>
        <label for="key">Upload Private Key (PEM format):</label><br>
        <input type="file" name="key" required><br><br>
        <input type="submit" value="Upload">
    </form>
    '''


# Handle certificate and key file uploads
@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        # Check if files are in the request
        cert_file = request.files.get('cert')
        key_file = request.files.get('key')

        if not cert_file or not key_file:
            return 'Both certificate and key files are required!', 400

        # Save the uploaded certificate and key with new names
        cert_file.save(CERT_FILE_PATH)
        key_file.save(KEY_FILE_PATH)

        # Load the certificate and extract the public key
        with open(CERT_FILE_PATH, 'rb') as cert_file_obj:
            cert_data = cert_file_obj.read()
            cert = load_pem_x509_certificate(cert_data)
            public_key = cert.public_key()

        # Save the extracted public key in PEM format
        with open(PUBLIC_KEY_FILE_PATH, 'wb') as pub_key_file:
            pub_key_file.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

        return '''
        <h1>Files uploaded and public key extracted successfully!</h1>
        <p><a href="/">Upload more</a></p>
        '''

    except Exception as e:
        return str(e), 500


# Load private key for signing, decrypting, and timestamping
with open("uploads/private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(key_file.read(), password=None, backend=default_backend())

# Load public key for encrypting and verifying signatures
with open("uploads/public_key.pem", "rb") as pub_file:
    public_key = serialization.load_pem_public_key(pub_file.read(), backend=default_backend())


# Custom RFC 3161-like timestamping server
@app.route('/timestamp', methods=['POST'])
def rfc3161_timestamp():
    try:
        # Get the document data from the JSON request
        data = request.json.get('data')

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Get the current time
        current_time = datetime.datetime.utcnow().isoformat()

        # Create a timestamp token by signing the document data and current timestamp
        timestamp_token = private_key.sign(
            data.encode() + current_time.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # Return the signed timestamp token along with the current time
        timestamp_token_base64 = base64.b64encode(timestamp_token).decode('utf-8')

        return jsonify({
            'timestamp': current_time,
            'timestamp_token': timestamp_token_base64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Endpoint to sign any data
@app.route('/sign', methods=['POST'])
def sign_data():
    # Get the data to sign from the JSON request
    data = request.json.get('data')

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Sign the data with the private key
    signature = private_key.sign(
        data.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Encode the signature in base64 and return it
    signature_base64 = base64.b64encode(signature).decode('utf-8')

    return jsonify({'signature': signature_base64})


# Endpoint to decrypt base64-encoded encrypted data
@app.route('/decrypt', methods=['POST'])
def decrypt_data():
    # Get the base64 encoded data from the JSON request
    encrypted_data_base64 = request.json.get('data')

    if not encrypted_data_base64:
        return jsonify({'error': 'No encrypted data provided'}), 400

    # Decode the base64 to get the encrypted bytes
    encrypted_data = base64.b64decode(encrypted_data_base64)

    # Decrypt the data using the private key
    decrypted_data = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Return the decrypted data as a UTF-8 string
    return jsonify({'decrypted_data': decrypted_data.decode('utf-8')})


# Endpoint to encrypt data with the public key
@app.route('/encrypt', methods=['POST'])
def encrypt_data():
    # Get the data to encrypt from the JSON request
    data = request.json.get('data')

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Encrypt the data using the public key
    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Encode the encrypted data in base64 and return it
    encrypted_data_base64 = base64.b64encode(encrypted_data).decode('utf-8')

    return jsonify({'encrypted_data': encrypted_data_base64})


# Endpoint to verify the signature
@app.route('/verify', methods=['POST'])
def verify_signature():
    # Get the data and the signature from the JSON request
    data = request.json.get('data')
    signature_base64 = request.json.get('signature')

    if not data or not signature_base64:
        return jsonify({'error': 'Data or signature missing'}), 400

    # Decode the base64 signature
    signature = base64.b64decode(signature_base64)

    try:
        # Verify the signature using the public key
        public_key.verify(
            signature,
            data.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return jsonify({'message': 'Signature is valid'})
    except Exception as e:
        return jsonify({'message': 'Signature is invalid', 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(port=5000)
