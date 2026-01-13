"""
Security utilities for OneClick Reels AI
"""
import os
import secrets
import hashlib
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks."""
    # Remove path separators and dangerous characters
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    return filename[:255]  # Limit length

def sanitize_text_input(text: str, max_length: int = 5000) -> str:
    """Sanitize text input for API safety."""
    if not text:
        return ""
    
    # Remove HTML tags and dangerous characters
    text = text.replace('<', '').replace('>', '').replace('&', '&amp;')
    text = " ".join(text.split())  # Normalize whitespace
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text

def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)

def rate_limit_key(identifier: str, endpoint: str) -> str:
    """Generate rate limit key for Redis."""
    return f"rate_limit:{identifier}:{endpoint}"