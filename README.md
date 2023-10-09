# FastAPI

Let's create a REST API for storing and managing contacts. The API will be built using the FastAPI infrastructure and use SQLAlchemy for database management.

The contact model is given below:
```commandline
{
    "first_name": "string",
    "last_name": "string",
    "birthday": "2023-09-11",
    "email": "string",
    "phone": "string",
    "address": "string",
    "user_id": int
}
```

The user model is given below:
```commandline
{
    "username": "string",
    "email": "string",
    "password": "string",
    "create_at": "2023-09-11",
    "refresh_token": "string"
}
```

The application has an authentication and authorization mechanism using `JWT tokens`, so that all operations with contacts are performed only by registered users. The user has only operations with his contacts.

When registering, if a user already exists with the same email, the server will return an `HTTP 409 Conflict error`;
The server hashes the password and does not store it in clear text in the database;
If the user is successfully registered, the server must return an `HTTP response status` of `201 Created` and the new user's data;
For all `POST` operations creating a new resource, the server returns a status of `201 Created`;
During the `POST` operation, user authentication, the server accepts a request with user data (email, password) in the body of the request;
If the user does not exist or the password does not match, an `HTTP 401 Unauthorized error` is returned;
The authorization mechanism using `JWT tokens` is implemented by a pair of tokens: an access token `access_token` and a refresh token `refresh_token`;

The API has the ability to perform the following actions:

1. Create a new contact;
2. Get a list of all contacts;
3. Get one contact by ID;
4. Update an existing contact;
5. Delete the contact;
6. Contacts are available for search by name, surname, email, phone or address;
7. The API can retrieve a list of contacts with birthdays for the next 7 days.

A mechanism for verifying the e-mail of a registered user, a limited number of requests and their speed (creation of contacts for the user) has been added.
CORS is also enabled for the REST API, and the update of the user avatar using the Cloudinary service is implemented.

# Sphinx

Sphinx cannot find my python files. Says 'no module named ...'

[Stackoverflow](https://stackoverflow.com/questions/53668052/sphinx-cannot-find-my-python-files-says-no-module-named)
