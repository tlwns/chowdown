from typing import Literal

from fastapi import HTTPException, status

from functionality.errors import AuthorisationError, ValidationError
from functionality.token import get_user_id

def check_customer_id_matches_token(customer_id: int, token: str, failure_message: str):
    """
    A wrapper for checking if a customer_id matches the provided token
    """
    _check_user_id_matches_token(customer_id, token, "customer", failure_message)

def check_eatery_id_matches_token(eatery_id: int, token: str, failure_message: str):
    """
    A wrapper for checking if a eatery_id matches the provided token
    """
    _check_user_id_matches_token(eatery_id, token, "eatery", failure_message)

def get_customer_id(token: str) -> int:
    """
    A wrapper for getting the customer_id from the token
    """
    return _get_user_id(token, "customer")

def get_eatery_id(token: str) -> int:
    """
    A wrapper for getting the eatery_id from the token
    """
    return _get_user_id(token, "eatery")

def _get_user_id(token: str, user_type: Literal["customer", "eatery"]) -> int:
    """
    A wrapper for getting the user_id from the token

    Handles HTTP Exceptions for if an Authorisation Error gets thrown
    """
    try:
        return get_user_id(token, user_type)
    except AuthorisationError as ae:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ae.message) from ae
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ve.message) from ve

def _check_user_id_matches_token(user_id: int, token: str, user_type: Literal["customer", "eatery"], failure_message: str):
    """
    A wrapper for checking if a user_id matches the provided token.

    Handles HTTP Exceptions for ids are not the same and if an Authorisation Error
    gets thrown
    """
    try:
        if get_user_id(token, user_type) != user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=failure_message)
    except AuthorisationError as ae:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ae.message) from ae
