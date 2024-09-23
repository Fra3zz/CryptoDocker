
# API Documentation for the Timestamp and Encryption Application

This document provides details on all API endpoints for the Timestamp and Encryption Application and explains what each endpoint does.

## Base URL
```
http://localhost:5000/
```

---

### CORS Configuration

CORS (Cross-Origin Resource Sharing) can be enabled or disabled in the application using an environment variable. The environment variable `CORS` can be set in the `.env` file as follows:

- **Enable CORS**: Set `CORS=true` or `CORS=1` to allow cross-origin requests.
- **Disable CORS**: Set `CORS=false` or `CORS=0` (default behavior).

CORS is useful when your frontend and backend are running on different domains or ports, and you want to allow them to communicate.

Example `.env` file:
```
CORS=true
```

---

### 1. `/timestamp`

#### **Description**:
This endpoint generates a timestamp token by signing the provided data with the current timestamp. The response includes the current timestamp and the base64-encoded signature of the timestamped data.

#### **Method**:
`POST`

#### **Request Body (JSON)**:
- **`data`**: The document or message data to be timestamped.

#### **Response (JSON)**:
- **`timestamp`**: The current UTC timestamp.
- **`timestamp_token`**: The base64-encoded signature of the data combined with the timestamp.

#### **Example Request**:

```bash
curl -X POST http://localhost:5000/timestamp \
-H "Content-Type: application/json" \
-d '{"data": "Document data to timestamp"}'
```

#### **Example Response**:
```json
{
  "timestamp": "2024-09-23T12:34:56.789123",
  "timestamp_token": "dGltZXN0YW1wX3NpZ25hdHVyZQ=="
}
```

---

### 2. `/sign`

#### **Description**:
Signs the provided data using the private key and returns the base64-encoded signature.

#### **Method**:
`POST`

#### **Request Body (JSON)**:
- **`data`**: The data to sign.

#### **Response (JSON)**:
- **`signature`**: The base64-encoded signature of the data.

#### **Example Request**:

```bash
curl -X POST http://localhost:5000/sign \
-H "Content-Type: application/json" \
-d '{"data": "Message to sign"}'
```

#### **Example Response**:
```json
{
  "signature": "c2lnbmF0dXJlX2luX2Jhc2U2NA=="
}
```

---

### 3. `/decrypt`

#### **Description**:
Decrypts the base64-encoded encrypted data using the private key and returns the decrypted plaintext.

#### **Method**:
`POST`

#### **Request Body (JSON)**:
- **`data`**: The base64-encoded encrypted data to decrypt.

#### **Response (JSON)**:
- **`decrypted_data`**: The decrypted plaintext data.

#### **Example Request**:

```bash
curl -X POST http://localhost:5000/decrypt \
-H "Content-Type: application/json" \
-d '{"data": "YmFzZTY0X2VuY3J5cHRlZF9kYXRh"}'
```

#### **Example Response**:
```json
{
  "decrypted_data": "Original decrypted message"
}
```

---

### 4. `/encrypt`

#### **Description**:
Encrypts the provided data using the public key and returns the base64-encoded encrypted data.

#### **Method**:
`POST`

#### **Request Body (JSON)**:
- **`data`**: The data to encrypt.

#### **Response (JSON)**:
- **`encrypted_data`**: The base64-encoded encrypted data.

#### **Example Request**:

```bash
curl -X POST http://localhost:5000/encrypt \
-H "Content-Type: application/json" \
-d '{"data": "Message to encrypt"}'
```

#### **Example Response**:
```json
{
  "encrypted_data": "YmFzZTY0X2VuY3J5cHRlZF9kYXRh"
}
```

---

### 5. `/verify`

#### **Description**:
Verifies if the provided signature was created using the private key for the provided data. The endpoint uses the public key for verification.

#### **Method**:
`POST`

#### **Request Body (JSON)**:
- **`data`**: The original data (message or document) to verify.
- **`signature`**: The base64-encoded signature to verify.

#### **Response (JSON)**:
- **`message`**: Either `"Signature is valid"` or `"Signature is invalid"`.

#### **Example Request**:

```bash
curl -X POST http://localhost:5000/verify \
-H "Content-Type: application/json" \
-d '{"data": "Message to verify", "signature": "YmFzZTY0X3NpZ25hdHVyZQ=="}'
```

#### **Example Response (valid)**:
```json
{
  "message": "Signature is valid"
}
```

#### **Example Response (invalid)**:
```json
{
  "message": "Signature is invalid",
  "error": "InvalidSignature: Signature verification failed"
}
```

---

### Error Handling

In case of errors, the API returns an appropriate error message in the response body, along with an HTTP 400 status code.

#### **Example Error Response**:

```json
{
  "error": "No data provided"
}
```

---

## Example Use Cases

- **Timestamping**: Use the `/timestamp` endpoint to generate timestamp tokens for document signing or auditing purposes (still work in progress).
- **Digital Signatures**: Use the `/sign` endpoint to digitally sign documents or messages.
- **Encryption and Decryption**: Use the `/encrypt` and `/decrypt` endpoints to securely transmit sensitive data.
- **Signature Verification**: Use the `/verify` endpoint to verify that a message or document was signed with the corresponding private key.