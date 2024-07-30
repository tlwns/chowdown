from typing import Annotated
from fastapi import APIRouter, HTTPException, Security, status

from functionality.errors import ValidationError, DuplicationError
from functionality.customer import edit_customer_profile, get_customer_profile, customer_vouchers, make_favourite_eatery, \
    make_unfavourite_eatery, make_hide_eatery, make_unhide_eatery
from functionality.token import HTTPBearer401

from router.api_types.api_request import CustomerUpdatesRequest, CustomerFavouriteEatery, CustomerUnfavouriteEatery, \
    CustomerHideEatery, CustomerUnhideEatery
from router.api_types.api_response import CustomerDetailsResponse, CustomerVoucherListResponse
from router.util import check_customer_id_matches_token

router = APIRouter()

@router.get("/{customer_id}/profile", status_code=status.HTTP_200_OK, response_model=CustomerDetailsResponse)
async def display_full_details_of_customer(customer_id: int, token: Annotated[str, Security(HTTPBearer401())]) -> CustomerDetailsResponse:
    """
    Gets all details (public + private) for the given customer

    Must be authenticated as the same customer as the customer_id
    """
    check_customer_id_matches_token(customer_id, token, "You are not authorized to view this profile")

    return get_customer_profile(customer_id)

@router.put("/{customer_id}/profile", status_code=status.HTTP_200_OK)
async def update_customer_details(customer_id: int, customer_new_info: CustomerUpdatesRequest, token: Annotated[str, Security(HTTPBearer401())]):
    """
    Updates customer’s own profile

    Must be authenticated as the same customer as the customer_id
    """
    check_customer_id_matches_token(customer_id, token, "You are not authorized to view this profile")

    kwargs = {key: getattr(customer_new_info, key, None) for key, value in customer_new_info.model_dump().items() if value is not None}

    try:
        return edit_customer_profile(customer_id, **kwargs)
    except DuplicationError as d:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(d)) from d
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(v)) from v
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)) from ve

@router.get("/{customer_id}/vouchers", status_code=status.HTTP_200_OK, response_model=CustomerVoucherListResponse)
async def get_customer_vouchers(customer_id: int, token: Annotated[str, Security(HTTPBearer401())]) -> CustomerVoucherListResponse:
    """
    Gets all vouchers instances the given customer has

    Must be authenticated as the same customer as the customer_id
    """
    check_customer_id_matches_token(customer_id, token, "You are not authorized to view this page")

    return customer_vouchers(customer_id)

@router.put("/{customer_id}/favourite_eateries", status_code=status.HTTP_200_OK)
async def customer_favourite_eatery(customer_id: int, favourite_eatery: CustomerFavouriteEatery, token: Annotated[str, Security(HTTPBearer401())]):
    """
    For a customer to add a eatery to its favourites list

    Must be authenticated as the same customer as the customer_id
    """
    check_customer_id_matches_token(customer_id, token, "You are not authorized to view this page")

    return make_favourite_eatery(customer_id, favourite_eatery.eatery_id)

@router.delete("/{customer_id}/favourite_eateries", status_code=status.HTTP_200_OK)
async def customer_unfavourite_eatery(customer_id: int, unfavourite_eatery: CustomerUnfavouriteEatery, token: Annotated[str, Security(HTTPBearer401())]):
    """
    For a customer to remove a favourite eatery

    Must be authenticated as the same customer as the customer_id
    """
    check_customer_id_matches_token(customer_id, token, "You are not authorized to view this page")

    return make_unfavourite_eatery(customer_id, unfavourite_eatery.eatery_id)

@router.put("/{customer_id}/hidden_eateries", status_code=status.HTTP_200_OK)
async def customer_hide_eatery(customer_id: int, hide_eatery: CustomerHideEatery, token: Annotated[str, Security(HTTPBearer401())]):
    """
    For a customer to add a eatery to its favourites list

    Must be authenticated as the same customer as the customer_id
    """
    check_customer_id_matches_token(customer_id, token, "You are not authorized to view this page")

    return make_hide_eatery(customer_id, hide_eatery.eatery_id)

@router.delete("/{customer_id}/hidden_eateries", status_code=status.HTTP_200_OK)
async def customer_unhide_eatery(customer_id: int, unhide_eatery: CustomerUnhideEatery, token: Annotated[str, Security(HTTPBearer401())]):
    """
    For a customer to remove a favourite eatery

    Must be authenticated as the same customer as the customer_id
    """
    check_customer_id_matches_token(customer_id, token, "You are not authorized to view this page")

    return make_unhide_eatery(customer_id, unhide_eatery.eatery_id)
