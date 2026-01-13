"""
Authentication system for OneClick Reels AI
Simple admin authentication with JWT tokens
"""
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import jwt

# Secret key for JWT (should be in environment variables in production)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "oneclick-reels-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Admin credentials (in production, store in database with hashed passwords)
# Using SHA256 for simplicity - password is "admin123"
ADMIN_USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest()
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    password_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return password_hash == hashed_password

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user"""
    if username not in ADMIN_USERS:
        return False
    
    hashed_password = ADMIN_USERS[username]
    return verify_password(password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
