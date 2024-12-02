import secrets

# Generate a secure random key
jwt_secret = secrets.token_hex(32)
print(f"Generated JWT_SECRET_KEY: {jwt_secret}")