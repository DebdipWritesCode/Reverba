import bcrypt
import hashlib

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Encode both to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # Verify password
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def hash_token(token: str) -> str:
    """Hash a token (e.g., refresh token) using SHA256"""
    # JWT tokens can be longer than bcrypt's 72-byte limit
    # Use SHA256 which has no length limit
    token_bytes = token.encode('utf-8')
    hashed = hashlib.sha256(token_bytes).hexdigest()
    return hashed

def verify_token(plain_token: str, hashed_token: str) -> bool:
    """Verify a token against its hash"""
    # Hash the plain token and compare
    token_hash = hash_token(plain_token)
    return token_hash == hashed_token
