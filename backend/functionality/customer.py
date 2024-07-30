from typing import Dict, List, Set
from datetime import datetime, timezone

from functionality.errors import ValidationError, DuplicationError
from functionality.authorisation import hash_password, verify_password
from functionality.address import valid_address
from functionality.helpers import get_raw_rating, validate_regex_email, validate_regex_password, validate_regex_phone

from db.helpers.customer import get_customer_by_id, get_customer_current_password_by_id, \
    get_customer_old_passwords_by_id, update_customer_email, update_customer_name, \
    update_customer_password, update_customer_phone, update_customer_address, favourite_eatery, \
    unfavourite_eatery, get_customer_by_email, get_customer_by_phone_number
from db.helpers.voucher import get_voucher_by_id, get_vouchers_by_customer
from db.helpers.voucher_instance import get_voucher_instance_by_id, get_voucher_instances_by_customer
from db.helpers.voucher_template import get_voucher_template_by_id
from db.helpers.review import get_review_by_id, get_review_by_voucher_instance

from router.api_types.api_request import AddressCreateRequest
from router.api_types.api_response import CustomerDetailsResponse, CustomerVoucherResponse, CustomerVoucherListResponse, \
    AddressResponse

def get_customer_profile(customer_id: int) -> CustomerDetailsResponse:
    """
    Gets the profile of the given customer from the database and gives it back as a response
    """
    result = get_customer_by_id(customer_id)

    if result is None:
        raise ValidationError("invalid customer id")

    return CustomerDetailsResponse(
        email=result.email,
        first_name=result.first_name,
        last_name=result.last_name,
        phone_number=result.phone,
        address=AddressResponse(
            unit_number=result.address.unit_number,
            formatted_str=result.address.formatted_str,
        )
    )

def edit_customer_profile(customer_id: int, **kwargs):
    """
    Used for the input for editing a customer profile

    kwargs to check for:
     - first_name
     - last_name
     - email
     - phone_number
     - address
     - password

    /customer/profile [PUT]
    """
    customer_info = get_customer_by_id(customer_id)

    if customer_info is None:
        raise ValidationError("Error retrieving customer's information")

    def validate_name_logic(name: str):
        if not bool(name):
            raise ValidationError("First name and last name must not be empty")

    def update_name_logic(first_name: str, last_name: str):
        if customer_info is not None and (customer_info.first_name != first_name or customer_info.last_name != last_name):
            update_customer_name(customer_id, first_name, last_name)

    def validate_email_logic(email: str):
        if not bool(email):
            raise ValidationError("Email must be a string")

        validate_regex_email(email)

    def update_email_logic(email: str):
        if customer_info is not None and (customer_info.email != email.lower()):
            if get_customer_by_email(email) is not None:
                raise DuplicationError("Email already in use")
            update_customer_email(customer_id, email.lower())

    def validate_phone_logic(phone_number: str):
        if not bool(phone_number):
            raise ValidationError("Phone must not be empty")

        validate_regex_phone(phone_number)

    def update_phone_logic(phone_number: str):
        if customer_info is not None and (customer_info.phone != phone_number):
            if get_customer_by_phone_number(phone_number) is not None:
                raise DuplicationError("Phone already in use")

            update_customer_phone(customer_id, phone_number)

    def validate_address_logic(address: AddressCreateRequest):
        valid_address(address)

    def update_address_logic(address: AddressCreateRequest):
        update_customer_address(customer_id, valid_address(address))

    def validate_password_logic(password: str):
        if not bool(password):
            raise ValidationError("New password must not be empty")

        validate_regex_password(password)

        curr_password = get_customer_current_password_by_id(customer_id)
        if curr_password is None:
            raise ValidationError("Password could not be retrieved")
        if not verify_password(password, curr_password):
            past_passwords = get_customer_old_passwords_by_id(customer_id)
            if past_passwords is None:
                raise ValidationError("Error retrieving past passwords")
            if hash_password(password) in past_passwords:
                raise ValueError("Password is the same as a past password")

    def update_password_logic(password: str):
        update_customer_password(customer_id, hash_password(password), datetime.now(timezone.utc))

    # Validate all kwargs
    key_to_function_map = {
        "first_name": validate_name_logic,
        "last_name": validate_name_logic,
        "email": validate_email_logic,
        "phone_number": validate_phone_logic,
        "address": validate_address_logic,
        "password": validate_password_logic
    }

    for key, function in key_to_function_map.items():
        if key in kwargs:
            function(kwargs[key])

    # Perform all updates

    # Map of keys to their corresponding update logic functions
    key_to_function_map = {
        "email": update_email_logic,
        "phone_number": update_phone_logic,
        "address": update_address_logic,
        "password": update_password_logic
    }

    for key, function in key_to_function_map.items():
        if key in kwargs:
            function(kwargs[key])

    if "first_name" in kwargs or "last_name" in kwargs:
        update_name_logic(kwargs["first_name"], kwargs.get("last_name", ""))

def customer_vouchers(customer_id: int) -> CustomerVoucherListResponse:
    """
    Gets all vouchers instances the given customer has
    """
    voucher_instances = get_voucher_instances_by_customer(customer_id)

    if voucher_instances is None:
        raise ValidationError("Error retrieving customers vouchers")

    vouchers: List[CustomerVoucherResponse] = []
    for voucher_inst_id in voucher_instances:
        # Get the voucher details for each instance
        voucher_res = get_voucher_instance_by_id(voucher_inst_id)

        if voucher_res is None:
            raise ValidationError("Error retrieving voucher by instance id")

        v_id = voucher_res.voucher

        voucher = get_voucher_by_id(v_id)

        if voucher is None:
            raise ValidationError("Error retrieving voucher by id")

        voucher_template = get_voucher_template_by_id(voucher.voucher_template)

        if voucher_template is None:
            raise ValidationError("Error retrieving voucher template by id")

        review_id = get_review_by_voucher_instance(voucher_inst_id)

        review_details = None
        if review_id is not None:
            review_details = get_review_by_id(review_id)

        vouchers.append(CustomerVoucherResponse(
            voucher_instance_id=voucher_inst_id,
            voucher_id=v_id,
            eatery_id=voucher_template.eatery,
            name=voucher_template.name,
            description=voucher_template.description,
            conditions=voucher_template.conditions,
            expiry=voucher.expiry_date,
            status=voucher_res.status,
            review_id=review_id,
            given_rating=review_details.rating if review_details else None
        ))

    return CustomerVoucherListResponse(
        vouchers=vouchers
    )

def get_customer_past_eateries(customer_id: int) -> Set[int]:
    """
    Gets the customers past eateries
    """
    past_vouchers = get_vouchers_by_customer(customer_id)
    if past_vouchers is None:
        raise ValidationError("Error retrieving vouchers for the customer")

    past_eateries = set()
    for vid in past_vouchers:
        voucher = get_voucher_by_id(vid)
        if voucher is None:
            raise ValueError("Error retrieving past voucher")

        voucher_template = get_voucher_template_by_id(voucher.voucher_template)
        if voucher_template is None:
            raise ValueError("Error retrieving past voucher template")

        past_eateries.add(voucher_template.eatery)

    return past_eateries

def get_customer_past_eateries_reviews(customer_id: int) -> Dict[int, float]:
    """
    Gets the customers past reviewed eateries
    """
    past_voucher_instances = get_voucher_instances_by_customer(customer_id)
    if past_voucher_instances is None:
        raise ValidationError("Error retrieving vouchers for the customer")

    past_eateries = {}
    past_eateries_average_review = {}
    for vid in past_voucher_instances:
        voucher_review = get_review_by_voucher_instance(vid)
        if voucher_review is None:
            continue

        voucher_instance = get_voucher_instance_by_id(vid)
        if voucher_instance is None:
            raise ValueError("Error retrieving past voucher instance")

        voucher = get_voucher_by_id(voucher_instance.voucher)
        if voucher is None:
            raise ValueError("Error retrieving past voucher")

        voucher_template = get_voucher_template_by_id(voucher.voucher_template)
        if voucher_template is None:
            raise ValueError("Error retrieving past voucher template")

        if voucher_template.eatery not in past_eateries:
            past_eateries[voucher_template.eatery] = []
        past_eateries[voucher_template.eatery].append(voucher_review)

    for eatery_id, reviews in past_eateries.items():
        ratings = get_raw_rating(reviews)
        past_eateries_average_review[eatery_id] = sum(ratings)/len(ratings)

    return past_eateries_average_review

def make_favourite_eatery(customer_id: int, eatery_id: int):
    """
    For a customer to add a eatery to its favourites list
    """
    favourite_eatery(customer_id, eatery_id)

def make_unfavourite_eatery(customer_id: int, eatery_id: int):
    """
    For a customer to remove a favourite eatery
    """
    unfavourite_eatery(customer_id, eatery_id)

def make_hide_eatery(customer_id: int, eatery_id: int):
    """
    For a customer to add a eatery to its favourites list
    """
    favourite_eatery(customer_id, eatery_id)

def make_unhide_eatery(customer_id: int, eatery_id: int):
    """
    For a customer to remove a favourite eatery
    """
    unfavourite_eatery(customer_id, eatery_id)
