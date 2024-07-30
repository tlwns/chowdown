import os
import secrets
import string
from typing import Literal, Optional, Tuple
from datetime import datetime, timezone, timedelta
import jwt
from fastapi import HTTPException, Request, status
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel

from functionality.errors import ValidationError, AuthorisationError

from db.helpers.session import create_session, check_if_session_exists, update_refresh_token_in_session, view_session
from db.db_types.db_request import SessionCreationRequest

def extract_bearer_token(request: Request) -> Optional[str]:
    """
    Gets the access token from the Authorization header and returns it
    """
    authorization = request.headers.get("Authorization")
    scheme, credentials = get_authorization_scheme_param(authorization)
    if not (authorization and scheme and credentials and scheme.lower() == "bearer" and credentials != ""):
        return None
    return credentials

def generate_random_string(length: int) -> str:
    """
    Generates a random string given a length
    """
    return "".join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(length))

class HTTPBearer401(SecurityBase):
    # remake because of: https://github.com/tiangolo/fastapi/issues/10177
    def __init__(
        self,
        *,
        scheme_name: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(bearerFormat="Bearer")
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(
        self, request: Request
    ) -> Optional[str]:
        # get the token out of the header
        token = extract_bearer_token(request)
        if token is None:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token was not given in correct format.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        # Check token validity
        if not access_token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token was not given in correct format.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return token

def create_refresh_token_and_new_session(user_type: str, uid: int) -> Tuple[str, int]:
    """
    A function to create a refresh token for a user

    Args:
     - uid: The user id of an account

    Returns: The refresh token
    """
    rid = generate_random_string(10)

    issued_at = datetime.now(timezone.utc)

    sid = create_session(SessionCreationRequest(
        eatery=uid if user_type == "eatery" else None,
        customer=uid if user_type == "customer" else None,
        refresh_token=rid,
        time_last_updated=issued_at,
    ))

    if sid is None:
        raise ValidationError("Error creating session")

    payload = {
        "exp": issued_at + timedelta(days=float(os.environ["REFRESH_TOKEN_EXPIRY_DAYS"])),
        "iat": issued_at,
        "sid": sid,
        "rid": rid
    }

    encoded_token = jwt.encode(
        payload,
        os.environ["REFRESH_TOKEN_SECRET"],
        algorithm="HS256",
    )

    return (encoded_token, sid)

def create_refresh_token_and_update_session(user_type: str, uid: int, sid: int) -> str:
    """
    A function to create a refresh token for a user

    Args:
     - uid: The user id of an account

    Returns: The refresh token
    """
    rid = generate_random_string(10)

    issued_at = datetime.now(timezone.utc)

    update_refresh_token_in_session(sid, rid, issued_at)

    payload = {
        "exp": issued_at + timedelta(days=float(os.environ["REFRESH_TOKEN_EXPIRY_DAYS"])),
        "iat": issued_at,
        "sid": sid,
        "rid": rid
    }

    encoded_token = jwt.encode(
        payload,
        os.environ["REFRESH_TOKEN_SECRET"],
        algorithm="HS256",
    )

    return encoded_token

def create_access_token(sid: int) -> str:
    """
    A function to create an access token for a user

    Args:
     - sid: The session id for the access token

    Returns: The access token
    """
    if not check_if_session_exists(sid):
        raise AuthorisationError("Session does not exist")

    new_payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=0, minutes=float(os.environ["ACCESS_TOKEN_EXPIRY_MINUTES"])),
        "iat": datetime.now(timezone.utc),
        "sid": sid,
        "aid": generate_random_string(10)
    }

    return jwt.encode(
        new_payload,
        os.environ["ACCESS_TOKEN_SECRET"],
        algorithm="HS256"
    )

def access_token_valid(access_token: str) -> bool:
    """
    A function to check if an access token is valid

    Args:
     - access_token: The access token to check

    Returns: True if the access token is valid, False otherwise
    """
    decoded = jwt.decode(access_token, os.environ["ACCESS_TOKEN_SECRET"], algorithms=["HS256"])

    sid = decoded.get("sid")
    return sid and (check_if_session_exists(sid) or False)

def refresh_token_valid(refresh_token: str) -> bool:
    """
    A function to check if a refresh token is valid

    Args:
     - refresh_token: The refresh token to check

    Returns: True if the refresh token is valid, False otherwise
    """
    decoded = jwt.decode(refresh_token, os.environ["REFRESH_TOKEN_SECRET"], algorithms=["HS256"])

    sid = decoded.get("sid")
    return sid and (check_if_session_exists(sid) or False)

def get_session_id_from_access_token(access_token: str) -> int:
    """
    Given an access token, gets us the session id
    """

    # Unpack the session id from the refresh token
    payload = jwt.decode(access_token, os.environ["ACCESS_TOKEN_SECRET"], algorithms=["HS256"])
    sid = payload["sid"]

    return sid

def get_user_id(access_token: str, user_type: Literal["customer", "eatery"]) -> int:
    """
    Gets an access token and returns the user's id
    """
    # Upack the session id from the access token
    sid = get_session_id_from_access_token(access_token)
    if sid is None:
        raise ValidationError("Error creating session")
    session = view_session(sid)

    if session is None:
        raise ValidationError("Error viewing session")

    if user_type == "customer":
        if session.customer is not None:
            return session.customer
        raise AuthorisationError("Invalid session")

    if user_type == "eatery":
        if session.eatery is not None:
            return session.eatery
        raise AuthorisationError("Invalid session")

    raise ValidationError("Undefined user type")

def get_session_id_from_refresh_token(refresh_token: str) -> int:
    """
    Given an access token, gets us the session id
    """

    # Unpack the session id from the refresh token
    payload = jwt.decode(refresh_token, os.environ["REFRESH_TOKEN_SECRET"], algorithms=["HS256"])
    sid = payload["sid"]

    return sid
