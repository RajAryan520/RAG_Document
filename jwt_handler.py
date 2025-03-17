import jwt
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta,timezone
from typing import Dict,Optional
from login import Login
from database import SessionLocal
from pydantic import BaseModel
import os

# OAuth2PasswordBearer helps Fastapi to extract token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Login")

# Secret Key 
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class CurrentUser(BaseModel):
    id:int
    username:str

def create_access_token(data:Dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str=Depends(oauth2_scheme)):
    db = SessionLocal()
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
        
        user = db.query(Login).filter(Login.username == username).first()
        
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User not found")
        
        return CurrentUser(id=user.user_id,username=user.username)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token Expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    finally:
        db.close()