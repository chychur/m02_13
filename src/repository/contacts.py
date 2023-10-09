from datetime import date
from typing import Optional

from sqlalchemy import select, update, func, and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.shemas.contacts import ContactModel, ContactUpdateModel, ContactPartialUpdateModel


async def get_contact_by_id(user: User, contact_id: int, db: Session) -> Contact:
    """
    The get_contact_by_id function returns a contact from the database by its id.

    :param user: User: Get the user id from the database
    :param contact_id: int: Filter the contact by id
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    return db.scalar(
        select(Contact)
        .filter(
            and_(Contact.id == contact_id, Contact.user_id == user.id)
        )
    )


async def get_contact_by_email(user: User, email: str, db: Session) -> Optional[Contact]:
    """
    The get_contact_by_email function returns a contact by email.

    :param user: User: Identify the user that is currently logged in
    :param email: str: Filter the contacts by email
    :param db: Session: Pass the database session to the function
    :return: A contact by email
    :doc-author: Trelent
    """
    return db.scalar(
        select(Contact)
        .filter(
            and_(Contact.email == email, Contact.user_id == user.id)
        )
    )


async def get_contacts(user: User, skip: int, limit: int, first_name: str, last_name: str, email: str,
                       db: Session) -> list[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param user: User: Filter the contacts by user
    :param skip: int: Skip the first n contacts
    :param limit: int: Set the number of contacts to return
    :param first_name: str: Filter the contacts by first name
    :param last_name: str: Filter contacts by last name
    :param email: str: Filter contacts by email
    :param db: Session: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    query = select(Contact).filter(Contact.user_id == user.id)

    if first_name:
        query = query.filter(Contact.first_name == first_name)
    if last_name:
        query = query.filter(Contact.last_name == last_name)
    if email:
        query = query.filter(Contact.email == email)

    contacts = db.execute(
        query.offset(skip).limit(limit)
    ).scalars().all()

    return contacts  # noqa


async def create_contact(user: User, body: ContactModel, db: Session) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    :param user: User: Get the user_id from the request
    :param body: ContactModel: Get the data from the request body
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.dict(), user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


async def update_contact(user: User, contact_id: int, body: ContactUpdateModel, db: Session) -> Optional[Contact]:
    """
    The update_contact function updates a contact in the database.

    :param user: User: Get the user id from the database
    :param contact_id: int: Identify the contact to be updated
    :param body: ContactUpdateModel: Pass the data that will be used to update the contact
    :param db: Session: Access the database
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = db.execute(
        update(Contact)
        .values(**body.dict())
        .filter(
            and_(Contact.id == contact_id, Contact.user_id == user.id)
        )
        .returning(Contact)
    ).scalar()

    if contact:
        db.commit()

    return contact


async def partial_update_contact(user: User, contact_id: int, body: ContactPartialUpdateModel,
                                 db: Session) -> Optional[Contact]:
    """
    The partial_update_contact function updates a contact in the database.

    :param user: User: Ensure that the user is only able to update their own contacts
    :param contact_id: int: Find the contact in the database
    :param body: ContactPartialUpdateModel: Pass the data to be updated
    :param db: Session: Access the database
    :return: The updated contact
    :doc-author: Trelent
    """
    contact_body = {key: val for key, val in body.dict().items() if val is not None}

    contact = db.execute(
        update(Contact)
        .values(**contact_body)
        .filter(
            and_(Contact.id == contact_id, Contact.user_id == user.id)
        )
        .returning(Contact)
    ).scalar()

    db.commit()

    return contact


async def remove_contact(user: User, contact_id: int, db: Session) -> Optional[Contact]:
    """
    The remove_contact function removes a contact from the database.

    :param user: User: Identify the user who is making the request
    :param contact_id: int: Get the contact by id
    :param db: Session: Create a database session
    :return: The contact that was removed
    :doc-author: Trelent
    """
    contact = await get_contact_by_id(user, contact_id, db)

    if contact:
        db.delete(contact)
        db.commit()

    return contact


async def get_contacts_birthdays(user: User, from_date: date, to_date: date, db: Session) -> list[Contact]:
    """
    The get_contacts_birthdays function returns a list of contacts whose birthdays fall within the specified date range.

    :param user: User: Identify the user that is making the request
    :param from_date: date: Specify the start date of the range
    :param to_date: date: Specify the date to which we want to get contacts
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.execute(
        select(Contact).filter(
            and_(
                Contact.user_id == user.id,
                func.to_char(Contact.birth_date, 'MM-DD') >= from_date.strftime("%m-%d"),
                func.to_char(Contact.birth_date, 'MM-DD') <= to_date.strftime("%m-%d")
            )
        )
    ).scalars().all()

    return contacts  # noqa
