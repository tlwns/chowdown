from typing import List, Tuple
from pydantic import AwareDatetime

from functionality.errors import ValidationError

from db.helpers.eatery import get_eatery_by_id
from db.helpers.customer import get_customer_by_id
from db.db_types.db_request import AddressCreationRequest

from router.api_types.api_request import AddressCreateRequest

def valid_address(address: AddressCreateRequest) -> AddressCreationRequest:
    """
    A function to check if an access token is valid

    Args:
     - address request from front end to check

    Returns: A db request if its valid otherwise nothing
    """
    # Country - check not empty
    if address.country == "":
        raise ValidationError("Country not specified")

    # State - check not empty:
    if address.state == "":
        raise ValidationError("State not specified")

    # City - check not empty:
    if address.city == "":
        raise ValidationError("City not specified")

    # Street - none
    # County - none
    # Postcode - none
    # Housenumber - none could be 50-52 or 5A too many
    # Unit Number - none could be blank

    # longitude - valid range
    if address.longitude > 180 or address.longitude < -180:
        raise ValidationError("Longitude must be between -180 and 180")

    # latitude - valid range
    if address.latitude > 90 or address.latitude < -90:
        raise ValidationError("Latitude must be between -90 and 90")

    # Format address - none
    return AddressCreationRequest(
        unit_number=address.unit_number,
        house_number=address.house_number,
        street_addr=address.street,
        city=address.city,
        state=address.state,
        country=address.country,
        county=address.county,
        postcode=address.postcode,
        longitude=address.longitude,
        latitude=address.latitude,
        formatted_str=address.fmt_address,
    )

def get_location_keywords(address: AddressCreateRequest) -> List[str]:
    """
    Transforms address into a list of keywords
    """
    location_keywords: List[str] = []

    if address.street != "":
        location_keywords.append(address.street)

    if address.postcode != "":
        location_keywords.append(address.postcode)

    if address.city != "":
        location_keywords.append(address.city)

    if address.county != "":
        location_keywords.append(address.county)

    return location_keywords

def get_customer_location(customer_id) -> Tuple[float,float]:
    """
    gets long and lat coords for customer
    """
    customer = get_customer_by_id(customer_id)

    if customer is None:
        raise ValueError("Error fetching customer")


    return (customer.address.latitude, customer.address.longitude)

def get_eatery_location(eatery_id) -> Tuple[float,float]:
    """
    gets long and lat coords for eatery
    """
    eatery = get_eatery_by_id(eatery_id)

    if eatery is None:
        raise ValueError("Error fetching customer")


    return (eatery.address.latitude, eatery.address.longitude)

def get_eatery_date_joined(eatery_id) -> AwareDatetime:
    """
    gets registry date for eatery
    """
    eatery = get_eatery_by_id(eatery_id)

    if eatery is None:
        raise ValueError("Error fetching customer")


    return eatery.date_joined
