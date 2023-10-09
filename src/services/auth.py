import pickle
from typing import Optional

import redis as redis_db
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.database.models import User
from config_file import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key_jwt
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis = redis_db.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def __decode_jwt(self, token: str) -> dict:
        return jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

    def __encode_jwt(self, data: dict, iat: datetime, exp: datetime, scope: str) -> str:
        to_encode = data.copy()
        to_encode.update({"iat": iat, "exp": exp, "scope": scope})

        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta or 15 * 60)
        return self.__encode_jwt(data, datetime.utcnow(), expire, "access_token")

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        expire = datetime.utcnow() + (
            timedelta(seconds=expires_delta) if expires_delta else timedelta(days=7)
        )
        return self.__encode_jwt(data, datetime.utcnow(), expire, "refresh_token")

    # define a function to generate a new confirmed email token
    async def create_email_token(self, data: dict, expires_delta: Optional[float] = None) -> str:
        expire = datetime.utcnow() + (
            timedelta(seconds=expires_delta) if expires_delta else timedelta(days=1)
        )
        return self.__encode_jwt(data, datetime.utcnow(), expire, "email_token")

    async def decode_refresh_token(self, refresh_token: str) -> str:
        try:
            payload = self.__decode_jwt(refresh_token)

            if payload.get('scope') == 'refresh_token':
                email = payload.get('sub')
                return email

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = self.__decode_jwt(token)

            if payload.get('scope') == 'access_token':
                email = payload.get("sub")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.redis.get(f"user:{email}")
        if user is None:

            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception

            self.redis.set(f"user:{email}", pickle.dumps(user))
            self.redis.expire(f"user:{email}", 900)

        else:
            user = pickle.loads(user)

        return user

    async def get_email_from_token(self, token: str) -> str:
        try:
            payload = self.__decode_jwt(token)

            if payload.get('scope') == 'email_token':
                email = payload.get('sub')
                return email

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
