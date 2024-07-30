from typing import Annotated, List, Optional
from fastapi import APIRouter, HTTPException, Query, Security, status

from functionality.search import search_eateries
from functionality.token import HTTPBearer401
from functionality.eatery import get_eatery_information_responses, list_eateries, eatery_details, edit_eatery_profile, eatery_vouchers, eatery_reviews, eatery_review_creation, recommend_eateries
from functionality.errors import ValidationError, DuplicationError, AuthorisationError
from functionality.recommendations import Sorts

from router.api_types.api_request import EateryThumbnailUpdateRequest, EateryUpdatesRequest, EateryMenuUpdateRequest, ReviewCreateRequest
from router.api_types.api_response import EaterySearchResponse, HomePageResponse, PrivateEateryDetailsResponse, PublicEateryDetailsResponse, \
    EateryVoucherListResponse, ReviewCreationResponse, EateryReviewListResponse
from router.util import check_eatery_id_matches_token, get_customer_id

router = APIRouter()

@router.get("/list", status_code=status.HTTP_200_OK, response_model=HomePageResponse)
async def list_of_eateries() -> HomePageResponse:
    """
    Gets a list of the public details for all Eateries
    """
    return list_eateries()

@router.get("/list/personalised", status_code=status.HTTP_200_OK, response_model=HomePageResponse)
async def get_customer_recommended_eateries(
        token: Annotated[str, Security(HTTPBearer401())],
        sort_by: Optional[List[str]] = Query(None, alias="sort_by"),
        max_count: Optional[int] = Query(None, description="Max number of personalised eateries to return")) -> HomePageResponse:
    """
    Gets a list of the public details for all Eateries in a sorted order based off proximity, preferences, and reviews.
    """
    customer_id = get_customer_id(token)
    sort_criteria = []
    if sort_by:
        sort_criteria = [Sorts[s.upper()] for s in sort_by if s.upper() in Sorts.__members__]

    return HomePageResponse(eateries=recommend_eateries(customer_id, sort_criteria)[:max_count])

@router.get("/{eatery_id}/details", status_code=status.HTTP_200_OK, response_model=PrivateEateryDetailsResponse)
async def display_full_details_of_eatery(eatery_id: int, token: Annotated[str, Security(HTTPBearer401())]) -> PrivateEateryDetailsResponse:
    """
    Gets an eatery's own full details (i.e Eatery's private details)

    eatery_id (int): ID of the eatery
    """
    check_eatery_id_matches_token(eatery_id, token, "You are not authorized to view this profile")

    try:
        return eatery_details(eatery_id, "private")
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(v)) from v

@router.put("/{eatery_id}/details", status_code=status.HTTP_200_OK)
async def update_eatery_details(eatery_id: int, eatery_info: EateryUpdatesRequest, token: Annotated[str, Security(HTTPBearer401())]):
    """
    Updates an eatery's details

    NOTE: Must be authenticated as the same eatery as the eatery_id

    eatery_id (int): ID of the eatery
    """
    check_eatery_id_matches_token(eatery_id, token, "You are not authorized to view this profile")

    kwargs = {key: getattr(eatery_info, key, None) for key, value in eatery_info.model_dump().items() if value is not None}

    try:
        return edit_eatery_profile(eatery_id, **kwargs)
    except DuplicationError as d:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(d)) from d
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(v)) from v
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)) from ve

@router.get("/{eatery_id}/details/public", status_code=status.HTTP_200_OK, response_model=PublicEateryDetailsResponse)
async def get_public_details_of_eatery(eatery_id: int) -> PublicEateryDetailsResponse:
    """
    Gets the public details of an eatery, like their about us page

    eatery_id (int): ID of the eatery
    """
    try:
        return eatery_details(eatery_id, "private")
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(v)) from v

@router.put("/{eatery_id}/thumbnail", status_code=status.HTTP_200_OK)
async def update_eatery_thumbnail(eatery_id: int, thumbnail: EateryThumbnailUpdateRequest, token: Annotated[str, Security(HTTPBearer401())]):
    """
    Updates an eatery's thumbnail

    NOTE: Must be authenticated as the same eatery as the eatery_id

    eatery_id (int): ID of the eatery
    """
    check_eatery_id_matches_token(eatery_id, token, "You are not authorized to view this profile")

    return edit_eatery_profile(eatery_id, thumbnail_uri=thumbnail.thumbnail_uri)

@router.put("/{eatery_id}/menu", status_code=status.HTTP_200_OK)
async def update_eatery_menu(eatery_id: int, menu: EateryMenuUpdateRequest, token: Annotated[str, Security(HTTPBearer401())]):
    """
    Updates an eatery's menu

    NOTE: Must be authenticated as the same eatery as the eatery_id

    eatery_id (int): ID of the eatery
    """
    check_eatery_id_matches_token(eatery_id, token, "You are not authorized to view this profile")

    return edit_eatery_profile(eatery_id, menu_uri=menu.menu_uri)

@router.get("/{eatery_id}/vouchers", status_code=status.HTTP_200_OK, response_model=EateryVoucherListResponse)
async def get_eatery_vouchers(eatery_id: int) -> EateryVoucherListResponse:
    """
    Gets a list of details for all Vouchers created by the eatery

    eatery_id (int): ID of the eatery
    """
    return eatery_vouchers(eatery_id)

@router.get("/{eatery_id}/reviews", status_code=status.HTTP_200_OK, response_model=EateryReviewListResponse)
async def get_eatery_reviews(eatery_id: int) -> EateryReviewListResponse:
    """
    Gets a list of details for all reviews created for the eatery

    eatery_id (int): ID of the eatery
    """
    return eatery_reviews(eatery_id)

@router.post("/{eatery_id}/reviews", status_code=status.HTTP_200_OK, response_model=ReviewCreationResponse)
async def create_eatery_review(eatery_id: int, review_info: ReviewCreateRequest, token: Annotated[str, Security(HTTPBearer401())]) -> ReviewCreationResponse:
    """
    Creates a review for a logged in customer who has claimed and redeemed a voucher but is yet to review
    """
    try:
        return eatery_review_creation(eatery_id, get_customer_id(token), review_info)
    except AuthorisationError as a:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(a)) from a
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(v)) from v

@router.get("/search", status_code=status.HTTP_200_OK, response_model=EaterySearchResponse)
async def eateries_search(search_query: str = "") -> EaterySearchResponse:
    """
    Searches for eateries based on the search query
    
    search_query (str): The search query
    """
    # For the case that we get an empty search, use the general list of eateries
    if search_query == "":
        eatery_info_responses = get_eatery_information_responses()

        return EaterySearchResponse(eateries=eatery_info_responses)

    search_results = await search_eateries(search_query)

    return EaterySearchResponse(eateries=search_results)
