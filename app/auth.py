import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

# Configuration from .env
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-default-key")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", 3600))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:72]   # truncate here
    return pwd_context.hash(pw_bytes)

def verify_password(password: str, hashed: str) -> bool:
    pw_bytes = password.encode("utf-8")[:72]   # truncate here
    return pwd_context.verify(pw_bytes, hashed)


def create_access_token(data: Dict[str, Any]) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(seconds=JWT_EXP_SECONDS)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    token = credentials.credentials
    payload = decode_token(token)
    if "admin_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid payload: 'admin_id' missing")
    return payload