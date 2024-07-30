"""
A module which authorises customer and eatery registration
"""
import re
from datetime import datetime, timezone
from typing import Dict, Union, Optional
from passlib.context import CryptContext

from functionality.errors import DuplicationError, ValidationError
from functionality.helpers import validate_regex_email, validate_regex_phone, validate_regex_password
from functionality.address import valid_address
from functionality.message import send_customer_welcome_email, send_eatery_welcome_email
from functionality.token import create_access_token, create_refresh_token_and_new_session, get_session_id_from_access_token

from db.db_types.db_request import AddressCreationRequest, CustomerCreationRequest, EateryCreationRequest
from db.helpers.customer import get_customer_by_email, get_customer_by_phone_number, get_customer_current_password_by_id, insert_customer
from db.helpers.eatery import get_eatery_by_email, get_eatery_by_phone_number, get_eatery_by_abn, get_eatery_current_password_by_id, insert_eatery
from db.helpers.session import delete_session, view_session

from router.api_types.api_request import AddressCreateRequest

USER_REGISTRATION_DEFAULT_VALUE = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes a password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies against a hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)

class RegistrationForm:
    """
    A common class for registration of either eateries or customers
    """

    MANDATORY_FIELDS = ["email", "password", "address", "phone", "abn"]

    email = USER_REGISTRATION_DEFAULT_VALUE
    password = USER_REGISTRATION_DEFAULT_VALUE
    address: AddressCreateRequest
    validated_address: AddressCreationRequest
    phone = USER_REGISTRATION_DEFAULT_VALUE
    abn = USER_REGISTRATION_DEFAULT_VALUE

    def validate_email(self):
        """
        A function to validate the form email

        Raises ValidationError when invalid email provided

        Email Constraints:
         - Is string
         - Is of form email
        """
        if not bool(self.email):
            raise ValidationError("Email type must be string")
        
        if not isinstance(self.email, str):
            raise ValidationError("Email type must be string")

        validate_regex_email(self.email)

    def validate_address(self):
        """
        A function to validate the form address

        Raises ValidationError when invalid address provided

        Address Constraints:
         - Is valid address
        """
        self.validated_address = valid_address(self.address)

    def check_mandatory_fields_full(self):
        """
        A function to check that all mandatory fields are full

        Raises ValidationError when mandatory fields are not full
        """
        for field in self.MANDATORY_FIELDS:
            if getattr(self, field) is None:
                raise ValidationError(f"{field} is mandatory")

    def validate_phone(self):
        """
        Validates a phone number using a regular expression.

        Raises ValidationError when invalid phone number provided

        Phone number Constraints:
         - Is of form phone number
        """
        if not isinstance(self.phone, str):
            raise ValidationError("Invalid phone number")
            
        validate_regex_phone(self.phone)

    def validate_abn(self):
        """
        Validates an ABN using a regular expression and ABN CheckSum algorithm.

        Raises ValidationError when invalid abn provided

        ABN Constraints:
         - Is of form abn
         - Is of correct AU VAT format (checked using the published ABN CheckSum algorithm)
        """
        if not isinstance(self.abn, str):
            raise ValidationError("ABN type must be string")

        # Define a regex pattern for a simple abn validation
        pattern = re.compile(r"^(\d){11}$")

        # Use the pattern to match the abn
        match = pattern.match(self.abn)  # type: ignore

        # If a match is not found, the abn is invalid
        if not bool(match):
            raise ValidationError("Invalid ABN")

        # Subtract 1 from the first digit
        # pylint: disable=E1136
        abn_digits = str(int(self.abn[0]) - 1) + self.abn[1:]

        # Calculate the total
        weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        total = sum(int(digit) * weight for digit, weight in zip(abn_digits, weights))

        # Check validity
        if total == 0 or total % 89 != 0:
            raise ValidationError("Invalid ABN")

    def validate_password(self):
        """
        Validates a password using a regular expression.

        Args:
        password (str): The password to validate.

        Returns:
        bool: True if the password is valid, False otherwise.
        """
        if not isinstance(self.password, str):
            raise ValidationError("ABN type must be string")
        
        validate_regex_password(self.password)

    def validate_form(self, user_type="Customer"):
        """
        A function to validate the form

        Raises ValidationError when form is invalid
        """
        self.check_mandatory_fields_full()
        self.validate_email()
        self.validate_phone()
        self.validate_password()
        self.validate_address()
        if user_type == "Eatery":
            self.validate_abn()

    def database_transfer(self) -> int:
        """
        Up to subclasses to transfer to DB
        """
        assert False

class CustomerRegistrationForm(RegistrationForm):
    """
    A form which allows customers to register their forms
    """
    MANDATORY_FIELDS = ["first_name", "last_name", "email", "password",  "address"]

    def __init__(self, **kwargs) -> None:
        self.first_name = kwargs["first_name"]
        self.last_name = kwargs["last_name"]
        self.email = kwargs["email"].lower()
        self.password = kwargs["password"]
        self.address = kwargs["address"]
        self.phone = kwargs["phone_number"]

    def database_transfer(self) -> Optional[int]:
        """
        A function to input the form into the database

        Returns: The user id of the user
        """
        hashed_password = hash_password(self.password)
        customer = CustomerCreationRequest(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.phone,
            password=hashed_password,
            address=self.validated_address,
            date_joined=datetime.now(timezone.utc)
        )

        if get_customer_by_email(self.email) is not None:
            raise DuplicationError("Email already in use")

        #check for phone duplication
        if get_customer_by_phone_number(self.phone) is not None:
            raise DuplicationError("Phone already in use")

        return insert_customer(customer)

class EateryRegistrationForm(RegistrationForm):
    """
    Eatery registration form
    """
    MANDATORY_FIELDS = ["business_name", "manager_first_name", "manager_last_name",
                        "abn", "email", "password",  "address"]

    def __init__(self, **kwargs) -> None:
        self.business_name = kwargs["business_name"]
        self.email = kwargs["email"].lower()
        self.password = kwargs["password"]
        self.phone = kwargs["phone_number"]
        self.address = kwargs["address"]
        self.manager_first_name = kwargs["manager_first_name"]
        self.manager_last_name = kwargs["manager_last_name"]
        self.abn = kwargs["abn"]

    def database_transfer(self) -> Optional[int]:
        """
        A function to input the form into the database
        Returns: The user id of the user
        """
        hashed_password = hash_password(self.password)
        details = EateryCreationRequest(
            business_name=self.business_name,
            email=self.email,
            password=hashed_password,
            phone=self.phone,
            address=self.validated_address,
            manager_first_name=self.manager_first_name,
            manager_last_name=self.manager_last_name,
            abn=self.abn,
            date_joined=datetime.now(timezone.utc)
        )

        # check for email duplication
        if get_eatery_by_email(self.email) is not None:
            raise DuplicationError("Email already in use")

        # check for phone duplication
        if get_eatery_by_phone_number(self.phone) is not None:
            raise DuplicationError("Phone already in use")

        # check for abn duplication
        if get_eatery_by_abn(self.abn) is not None:
            raise DuplicationError("ABN already in use")

        return insert_eatery(details)

def customer_registration(customer_form: CustomerRegistrationForm) -> Optional[Dict[str, Union[str, int]]]:
    """
    A function used to perform customer registration logic

    This function will:
     - Ensure details are valid
     - Input details into the database
     - Get a user id
     - Create and return refresh and access tokens

    Args: The customer registration form

    Return: The refresh and access tokens
    """
    # Validate the form
    customer_form.validate_form()

    # Input into database
    uid = customer_form.database_transfer()

    if uid is None:
        return None

    # Create a refresh token and access token for the user
    refresh_token, sid = create_refresh_token_and_new_session("customer", uid)
    access_token = create_access_token(sid)

    send_customer_welcome_email(customer_form.email, customer_form.first_name)

    return {
        "user_id": uid,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def eatery_registration(eatery_form: EateryRegistrationForm) -> Optional[Dict[str, Union[str, int]]]:
    """
    A function used to perform eatery registration logic

    This function will:
     - Ensure details are valid
     - Input details into the database
     - Get a user id
     - Create and return refresh and access tokens

    Args: The eatery registration form

    Return: The refresh and access tokens
    """
    # Validate the form
    eatery_form.validate_form("Eatery")

    # Input into database
    uid = eatery_form.database_transfer()

    if uid is None:
        return None

    # Create a refresh token and access token for the user
    refresh_token, sid = create_refresh_token_and_new_session("eatery", uid)
    access_token = create_access_token(sid)

    send_eatery_welcome_email(eatery_form.email, eatery_form.manager_first_name)

    return {
        "user_id": uid,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def customer_login_auth(email: str, password: str) -> Dict[str, Union[str, int]]:
    """
    A function to login a user

    email is the email of the user, password is the password of the user
    """
    uid = get_customer_by_email(email.lower())
    if uid is None:
        raise ValueError("Email does not exist for customer")

    curr_password = get_customer_current_password_by_id(uid)
    if not curr_password or not verify_password(password, curr_password):
        raise ValueError("Passwords do not match")

    refresh_token, sid = create_refresh_token_and_new_session("customer", uid)
    access_token = create_access_token(sid)

    return {
        "user_id": uid,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def eatery_login_auth(email: str, password: str) -> Dict[str, Union[str, int]]:
    """
    A function to login a user

    email is the email of the user, password is the password of the user
    """
    uid = get_eatery_by_email(email.lower())
    if uid is None:
        raise ValueError("Email does not exist for eatery")

    curr_password = get_eatery_current_password_by_id(uid)
    if not curr_password or not verify_password(password, curr_password):
        raise ValueError("Passwords do not match")

    refresh_token, sid = create_refresh_token_and_new_session("eatery", uid)
    access_token = create_access_token(sid)

    return {
        "user_id": uid,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def logout(access_token: str):
    """
    A function to logout a user
    """
    # Get the sid from the token

    sid = get_session_id_from_access_token(access_token)

    # Check session exists
    if view_session(sid) is None:
        raise ValidationError("Session does not exist")

    # Remove the session
    delete_session(sid)
