from typing import Optional

from libgravatar import Gravatar
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.database.models import User
from src.shemas.users import UserModel


async def create_user(body: UserModel, db: Session) -> User:
    user = User(**body.dict())

    try:
        g = Gravatar(body.email)
        user.avatar = g.get_image()
    except Exception as e:
        print(e)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    return db.execute(
        select(User)
        .filter(User.email == email)
    ).scalar()


async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    return db.execute(
        select(User)
        .filter(User.id == user_id)
    ).scalar()


async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def update_avatar(user_id: int, url: str, db: Session) -> User:
    user = db.execute(
        update(User)
        .values(avatar=url)
        .filter(User.id == user_id)
        .returning(User)
    ).scalar()
    db.commit()

    return user


async def update_password(user_id: int, password: str, db: Session) -> User:
    user = db.execute(
        update(User)
        .values(password=password)
        .filter(User.id == user_id)
        .returning(User)
    ).scalar()
    db.commit()

    return user


async def update_email(user_id: int, email: str, db: Session) -> User:
    user = db.execute(
        update(User)
        .values(email=email)
        .filter(User.id == user_id)
        .returning(User)
    ).scalar()
    db.commit()

    return user


async def confirmed_email(user: User, db: Session) -> None:
    user.confirmed = True
    db.commit()
