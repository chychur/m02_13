from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.shemas.contacts import (
    ContactModel,
    ContactResponse,
    ContactUpdateModel,
    ContactPartialUpdateModel
)
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Pass the contact data to the function
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user id from the jwt token
    :return: The created contact
    """
    contact_exist = await repository_contacts.get_contact_by_email(current_user, body.email, db)
    if contact_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="A contact with this email address already exists")

    return await repository_contacts.create_contact(current_user, body, db)


@router.get("/birthdays", response_model=list[ContactResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contact_birthdays(
                        from_date: Optional[date] = Query(
                            default=None,
                            description="Cannot be greater than {to_date} parameter. Example:",
                            example=date.today()),
                        to_date: Optional[date] = Query(
                            default=None,
                            description="Cannot be less than the {from_date} parameter.",
                            example=date.today() + timedelta(7)),
                        db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Get a list of contacts whose birthday falls within the selected time period. The period cannot exceed 7 days.

    If the **{from_date}** parameter is not specified, then a list of contacts whose birthday falls within the period
    **{to_date} - 7 days** will be returned.

    If the **{to_date}** parameter is not specified, then a list of contacts whose birthday falls within the period
    **{from_date} + 7 days** will be returned.

    If none of the parameters is specified, then a list of contacts whose birthday falls within the next 7 days
    from the current one will be returned.

    If the period is longer than 7 days, it will be truncated to 7 days from the **{from_date}** parameter.
    """
    if from_date and to_date:
        if from_date > to_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The {from_date} parameter cannot be greater than the {to_date} parameter"
            )
        elif from_date + timedelta(days=7) < to_date:
            to_date = from_date + timedelta(days=7)
    else:
        if from_date is None and to_date:
            from_date = to_date + timedelta(7)
        elif to_date is None and from_date:
            to_date = from_date - timedelta(7)
        else:
            from_date = date.today()
            to_date = from_date + timedelta(7)

    return await repository_contacts.get_contacts_birthdays(current_user, from_date, to_date, db)


@router.get("/", response_model=list[ContactResponse], description="Get all contacts",
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = Query(default=10, ge=1, le=100),
                        first_name: Optional[str] = Query(default=None, min_length=3, max_length=100),
                        last_name: Optional[str] = Query(default=None, min_length=3, max_length=100),
                        email: Optional[str] = Query(default=None),
                        db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_contacts function is used to read contacts from the database.
        It takes in a skip, limit, first_name, last_name and email as parameters.
        The skip parameter is used to determine how many records should be skipped before returning results.
        The limit parameter determines how many records should be returned after skipping the specified number of records.
        The first_name and last_name parameters are optional strings that can be passed in to filter by name (first or last).
        If no names are provided then all contacts will be returned regardless of their name(s).

    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of results returned
    :param first_name: Optional[str]: Filter the contacts by first name
    :param last_name: Optional[str]: Filter the results by last name
    :param email: Optional[str]: Filter the contacts by email
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the user_id from the token
    :return: A list of contacts
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contacts(current_user, skip, limit, first_name, last_name, email, db)

    return contact


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=40, seconds=60))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_contact function is used to retrieve a single contact from the database.
    It takes in an integer representing the ID of the contact, and returns a Contact object.

    :param contact_id: int: Specify the id of the contact we want to update
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact_by_id(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactUpdateModel, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes three arguments:
            - body: A ContactUpdateModel object containing the new values for the contact's fields.
            - contact_id: An integer representing the ID of an existing contact to be updated.
            - db (optional): A Session object used to connect to and query a PostgreSQL database, if not provided, one will be created automatically using get_db().

    :param body: ContactUpdateModel: Define the data that will be passed to the function
    :param contact_id: int: Identify the contact to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user that is currently logged in
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse, description="At least one body field must be present!",
              dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def partial_contact_update(body: ContactPartialUpdateModel, contact_id: int, db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    """
    The partial_contact_update function updates a contact in the database.
        The function takes three arguments:
            body: A ContactPartialUpdateModel object containing the fields to be updated and their new values.
            contact_id: An integer representing the ID of the contact to be updated.
            db (optional): A Session object for interacting with an SQLAlchemy database session pool, if not provided, one will be created automatically using Depends(get_db).

    :param body: ContactPartialUpdateModel: Specify the type of data that will be passed in the body
    :param contact_id: int: Specify the contact that is to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the auth_service
    :return: A contact model
    """
    contact = await repository_contacts.partial_update_contact(current_user, contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the contact to be removed
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user that is currently logged in
    :return: The contact that has been removed
    """
    contact = await repository_contacts.remove_contact(current_user, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
