from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.shemas.users import UserModel, UserResponse, TokenModel, EmailModel
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email_confirmed, send_email_reset_password
from config_file import Template


router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes in a UserModel object, which is validated by pydantic.
        If the email already exists, it will return an HTTP 409 error code (conflict).
        Otherwise, it will create a new user and send them an email to confirm their account.

    :param body: UserModel: Get the data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A dictionary with the new user and a detail message
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)

    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    background_tasks.add_task(send_email_confirmed, new_user.email, new_user.username, request.base_url)

    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Pass the database session to the function
    :return: A token
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})

    await repository_users.update_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns a new access_token and refresh_token.
        If the user's current refresh token does not match what was passed into this function, then it will return an error.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the header
    :param db: Session: Get the database session
    :return: A dictionary with the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})

    await repository_users.update_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}', include_in_schema=False)
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it gets that user from the database and checks if they are already confirmed or not.
        If they are already confirmed, then we return a message saying so; otherwise, we update their record in
            our database with their new status of &quot;confirmed&quot;.

    :param token: str: Get the token from the url
    :param db: Session: Access the database
    :return: A message that the email has been confirmed
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    elif user.confirmed:
        return {"message": "Your email is already confirmed"}

    await repository_users.confirmed_email(user, db)

    return {"message": "Email confirmed"}


@router.post("/reset_password", dependencies=[Depends(RateLimiter(times=10, minutes=5))])
async def reset_password(body: EmailModel, background_tasks: BackgroundTasks, request: Request,
                         db: Session = Depends(get_db)):
    """
    The reset_password function is used to send an email to the user with a link that will allow them
    to reset their password. The function takes in the body of the request, which contains only an email address,
    and uses this information to find and retrieve a user from our database. If no such user exists, then we raise
    an HTTPException indicating that there was no such account found for this email address. Otherwise, we add a task
    to our background tasks queue (which is handled by Celery) and call it send_email_reset_password with arguments:
    the users' email address; username; and base

    :param body: EmailModel: Get the email address from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the server
    :param db: Session: Get the database session
    :return: A dictionary with a message and timeout_link
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")

    background_tasks.add_task(send_email_reset_password, user.email, user.username, request.base_url)

    return {"message": "Password reset email sent", "timeout_link": {"seconds": 600}}


@router.get('/reset_password/{token}', response_class=HTMLResponse, include_in_schema=False)
async def reset_password_template(token: str, request: Request, db: Session = Depends(get_db)):
    """
    The reset_password_template function is used to render the new_password.html template, which allows a user to reset their password.

    :param token: str: Get the token from the url
    :param request: Request: Access the request object
    :param db: Session: Pass the database session to the function
    :return: The new_password
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")

    return Template.html_response.TemplateResponse("new_password.html", {"request": request})


@router.post('/reset_password/{token}', include_in_schema=False)
async def new_password(token: str, password: str = Form(...), db: Session = Depends(get_db)):
    """
    The new_password function is used to change the password of a user.
        It takes in a token and new password, and returns an ok status if successful.

    :param token: str: Get the email from the token
    :param password: str: Get the password from the request body,
    :param db: Session: Get the database session
    :return: A dictionary with a status key and an ok value
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")

    password = auth_service.get_password_hash(password)
    await repository_users.update_password(user.id, password, db)

    return {"status": 'ok'}
