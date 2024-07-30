from typing import Annotated
from fastapi import APIRouter, HTTPException, Response, Security, status, Request
import jwt

from db.helpers.session import get_user_type_by_session, view_session
from router.api_types.api_request import CustomerRegistrationRequest, EateryRegistrationRequest, LoginRequest
from router.api_types.api_response import AuthenticationResponse
from functionality.authorisation import CustomerRegistrationForm, EateryRegistrationForm, customer_login_auth, customer_registration, eatery_login_auth, eatery_registration, logout
from functionality.errors import AuthorisationError, DuplicationError, ValidationError
from functionality.token import HTTPBearer401, create_access_token, create_refresh_token_and_update_session, get_session_id_from_refresh_token, refresh_token_valid

router = APIRouter()

@router.get("/refresh")
async def token_refresh(request: Request, response: Response) -> AuthenticationResponse:
    """
    Refreshes the token
    """
    refresh_token = request.cookies.get("refresh_token")

    try:
        if not refresh_token or not refresh_token_valid(refresh_token):
            raise AuthorisationError("Invalid refresh token")

        sid = get_session_id_from_refresh_token(refresh_token)
        session = view_session(sid)
        uid = None
        user_type = get_user_type_by_session(sid)
        if session and session.customer:
            uid = session.customer
        elif session and session.eatery:
            uid = session.eatery

        if uid is None or user_type is None:
            raise AuthorisationError("Session does not match user type")

        # Create new refresh token
        new_refresh_token = create_refresh_token_and_update_session(
            user_type,
            uid,
            sid
        )
        new_access_token = create_access_token(sid)

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True
        )

        return AuthenticationResponse(
            user_id=uid,
            access_token=new_access_token,
            user_type=user_type
        )
    except (ValueError, AuthorisationError, jwt.exceptions.PyJWTError) as e:
        response.delete_cookie("refresh_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"set-cookie": response.headers["set-cookie"]}
        ) from e

@router.delete("/logout", status_code=status.HTTP_200_OK)
async def logout_user(response: Response, token: Annotated[str, Security(HTTPBearer401())]) -> None:
    """
    Logs a user out of their account
    """
    try:
        logout(token)
        response.delete_cookie("refresh_token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or Password is incorrect for customer") from e

@router.post("/register/customer", status_code=status.HTTP_200_OK, response_model=AuthenticationResponse)
async def register_customer(response: Response, customer: CustomerRegistrationRequest) -> AuthenticationResponse:
    """
    Registers a customer
    """
    customer_form = CustomerRegistrationForm(
        email=customer.email,
        password=customer.password,
        first_name=customer.first_name,
        last_name=customer.last_name,
        address=customer.address,
        phone_number=customer.phone_number
    )

    try:
        res = customer_registration(customer_form)
        response.set_cookie(
            key="refresh_token",
            value=res["refresh_token"],
            httponly=True
        )
        return AuthenticationResponse(user_id=res["user_id"], user_type="customer", access_token=res["access_token"])
    except DuplicationError as d:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(d)) from d
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(v)) from v
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)) from ve

@router.post("/login/customer", status_code=status.HTTP_200_OK, response_model=AuthenticationResponse)
async def customer_login(response: Response, customer_login_props: LoginRequest) -> AuthenticationResponse:
    """
    Logs a customer in
    """
    try:
        res = customer_login_auth(
            customer_login_props.email,
            customer_login_props.password
        )

        response.set_cookie(
            key="refresh_token",
            value=res["refresh_token"],
            httponly=True
        )

        return AuthenticationResponse(user_id=res["user_id"], user_type="customer", access_token=res["access_token"])
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or Password is incorrect for customer") from ve
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or Password is incorrect for customer") from ve

@router.post("/register/eatery", status_code=status.HTTP_200_OK, response_model=AuthenticationResponse)
async def register_eatery(response: Response, eatery: EateryRegistrationRequest) -> AuthenticationResponse:
    """
    Registration for an eatery
    """
    eatery_form = EateryRegistrationForm(
        email=eatery.email,
        password=eatery.password,
        business_name=eatery.business_name,
        manager_first_name=eatery.manager_first_name,
        manager_last_name=eatery.manager_last_name,
        address=eatery.address,
        phone_number=eatery.phone_number,
        abn=eatery.abn
    )

    try:
        res = eatery_registration(eatery_form)

        response.set_cookie(
            key="refresh_token",
            value=res["refresh_token"],
            httponly=True
        )

        return AuthenticationResponse(user_id=res["user_id"], user_type="eatery", access_token=res["access_token"])
    except DuplicationError as d:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(d)) from d
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(v)) from v
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)) from ve

@router.post("/login/eatery", status_code=status.HTTP_200_OK, response_model=AuthenticationResponse)
async def eatery_login(response: Response, eatery_login_props: LoginRequest) -> AuthenticationResponse:
    """
    Logs a eatery in
    """
    try:
        res = eatery_login_auth(
            eatery_login_props.email,
            eatery_login_props.password
        )

        response.set_cookie(
            key="refresh_token",
            value=res["refresh_token"],
            httponly=True
        )

        return AuthenticationResponse(user_id=res["user_id"], user_type="eatery", access_token=res["access_token"])
    except ValidationError as ve:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or Password is incorrect for customer") from ve
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username or Password is incorrect for customer") from ve
