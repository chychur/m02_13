from typing import Optional

from libgravatar import Gravatar
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.database.models import User
from src.shemas.users import UserModel


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Get the data from the request body
    :param db: Session: Access the database
    :return: A user object
    :doc-author: Trelent
    """
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
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists, it returns None.

    :param email: str: Pass in the email of the user that we want to find
    :param db: Session: Pass in the database session to the function
    :return: A single user
    :doc-author: Trelent
    """
    return db.execute(
            select(User)
            .filter(User.email == email)
        ).scalar()


async def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
    """
    The get_user_by_id function returns a user object from the database, given an id.

    :param user_id: int: Pass the user id to the function
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    return db.execute(
            select(User)
            .filter(User.id == user_id)
        ).scalar()


async def update_token(user: User, token: str | None, db: Session) -> None:

    """
    The update_token function updates the refresh token for a user in the database.

    :param user: User: Pass in the user object that is being updated
    :param token: str | None: Update the user's refresh token
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


async def update_avatar(user_id: int, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user in the database.

    :param user_id: int: Identify the user whose avatar is to be updated
    :param url: str: Set the avatar url of a user
    :param db: Session: Connect to the database
    :return: The user object
    :doc-author: Trelent
    """
    user = db.execute(
        update(User)
        .values(avatar=url)
        .filter(User.id == user_id)
        .returning(User)
    ).scalar()
    db.commit()

    return user


async def update_password(user_id: int, password: str, db: Session) -> User:
    """
    The update_password function updates the password of a user in the database.

    :param user_id: int: Identify the user whose password is to be updated
    :param password: str: Update the password of a user
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    :doc-author: Trelent
    """
    user = db.execute(
        update(User)
        .values(password=password)
        .filter(User.id == user_id)
        .returning(User)
    ).scalar()
    db.commit()

    return user


async def update_email(user_id: int, email: str, db: Session) -> User:
    """
    The update_email function updates the email of a user in the database.

    :param user_id: int: Identify which user to update
    :param email: str: Pass the new email address to be updated
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user = db.execute(
        update(User)
        .values(email=email)
        .filter(User.id == user_id)
        .returning(User)
    ).scalar()
    db.commit()

    return user


async def confirmed_email(user: User, db: Session) -> None:
    """
    The confirmed_email function is called when a user confirms their email address.
    It sets the confirmed field of the User object to True, and commits it to the database.

    :param user: User: Pass the user object to the function
    :param db: Session: Access the database
    :return: Nothing
    :doc-author: Trelent
    """
    user.confirmed = True
    db.commit()
