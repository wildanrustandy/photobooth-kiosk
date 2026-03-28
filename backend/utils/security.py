import secrets
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
from config import settings


def generate_device_id() -> str:
    """Generate a unique device ID."""
    return f"dev_{secrets.token_urlsafe(16)}"


def generate_device_token() -> str:
    """Generate a unique device token."""
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # bcrypt requires bytes, so encode the password
    password_bytes = password.encode("utf-8")
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_device_jwt(device_id: str, booth_id: str = None) -> str:
    """Create JWT token for device session."""
    payload = {
        "device_id": device_id,
        "booth_id": booth_id,
        "exp": datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours),
        "iat": datetime.utcnow(),
        "type": "device_access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_admin_jwt(admin_id: str, username: str, role: str) -> str:
    """Create JWT token for admin user."""
    payload = {
        "admin_id": admin_id,
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=settings.admin_token_expire_hours),
        "iat": datetime.utcnow(),
        "type": "admin_access",
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_jwt_token(token: str) -> dict | None:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_signature": True, "verify_exp": True, "require_exp": True},
        )
        return payload
    except JWTError:
        return None


def verify_admin_token(token: str) -> dict | None:
    """Verify admin JWT token."""
    payload = verify_jwt_token(token)
    if payload and payload.get("type") == "admin_access":
        return payload
    return None


def verify_device_token(token: str) -> dict | None:
    """Verify device JWT token."""
    payload = verify_jwt_token(token)
    if payload and payload.get("type") == "device_access":
        return payload
    return None
