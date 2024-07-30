from typing import Annotated
import jwt

from fastapi import APIRouter, HTTPException, Security, status

from functionality.errors import AuthorisationError, ValidationError
from functionality.token import HTTPBearer401
from functionality.voucher import VoucherCreationForm, create_voucher, voucher_accept_redemption_code, voucher_claim, \
    voucher_details, voucher_get_redemption_code, voucher_redeem_instance, voucher_reject_redemption_code

from router.api_types.api_request import VoucherCreateRequest, VoucherClaimRequest
from router.api_types.api_response import VoucherClaimResponse, VoucherCreationResponse, VoucherDetailsResponse, \
    VoucherInstanceRedeemResponse, VoucherRedemptionResponse
from router.util import check_customer_id_matches_token, check_eatery_id_matches_token, get_customer_id, get_eatery_id

router = APIRouter()

@router.post("", status_code=status.HTTP_200_OK, response_model=VoucherCreationResponse)
async def register_voucher(voucher: VoucherCreateRequest, token: Annotated[str, Security(HTTPBearer401())]) -> VoucherCreationResponse:
    """
    Creates a new voucher

    Must be authenticated as the same eatery as the eatery_id in request body
    """
    voucher_form = VoucherCreationForm(
        eid=voucher.eatery_id,
        title=voucher.name,
        description=voucher.description,
        conditions=voucher.conditions,
        quantity=voucher.quantity,
        duration=voucher.duration,
        release=voucher.release,
        schedule=voucher.schedule,
    )

    check_eatery_id_matches_token(voucher.eatery_id, token, "You are not authorized to view this profile")

    try:
        return create_voucher(voucher_form)
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=v.message) from v
    except jwt.DecodeError as d:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from d
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ve)) from ve

@router.get("/{voucher_id}", status_code=status.HTTP_200_OK, response_model=VoucherDetailsResponse)
async def get_voucher(voucher_id: int) -> VoucherDetailsResponse:
    """
    Given a voucher_id, returns the details of such a voucher
    """
    try:
        return voucher_details(voucher_id)
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=v.message) from v

@router.put("/claim/{voucher_id}", status_code=status.HTTP_200_OK, response_model=VoucherClaimResponse)
async def claim_voucher(voucher_id: int, voucher_claim_request: VoucherClaimRequest, token: Annotated[str, Security(HTTPBearer401())]) -> VoucherClaimResponse:
    """
    Given a voucher_id and customer_id, claims an instance of the voucher for the customer
    """
    check_customer_id_matches_token(voucher_claim_request.customer_id, token, "You are not authorized to view this profile")

    try:
        return voucher_claim(voucher_id, voucher_claim_request.customer_id)
    except jwt.DecodeError as d:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from d
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=v.message) from v

@router.put("/instance/{instance_id}/redeem", status_code=status.HTTP_200_OK, response_model=VoucherInstanceRedeemResponse)
async def redeem_voucher_instance(instance_id: int, token: Annotated[str, Security(HTTPBearer401())]) -> VoucherInstanceRedeemResponse:
    """
    Given a voucher_instance_id, marks the voucher as redeemed
    """
    try:
        return voucher_redeem_instance(instance_id, get_customer_id(token))
    except AuthorisationError as ae:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ae.message) from ae
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=v.message) from v

@router.get("/redemption/{code}", status_code=status.HTTP_200_OK, response_model=VoucherRedemptionResponse)
async def redemption_voucher_code(code: str, token: Annotated[str, Security(HTTPBearer401())]) -> VoucherRedemptionResponse:
    """
    Given a redemption code, returns the details of the voucher instance
    """
    try:
        return voucher_get_redemption_code(code, get_eatery_id(token))
    except AuthorisationError as ae:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ae.message) from ae
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=v.message) from v

@router.put("/redemption/{code}/accept", status_code=status.HTTP_200_OK)
async def accept_voucher_redemption(code: str, token: Annotated[str, Security(HTTPBearer401())]):
    """
    Given a redemption code, marks the voucher as redeemed
    """
    try:
        return voucher_accept_redemption_code(code, get_eatery_id(token))
    except AuthorisationError as ae:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ae.message) from ae
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=v.message) from v

@router.put("/redemption/{code}/reject", status_code=status.HTTP_200_OK)
async def reject_voucher_redemption(code: str, token: Annotated[str, Security(HTTPBearer401())]):
    """
    Given a redemption code, marks the voucher as rejected
    """
    try:
        return voucher_reject_redemption_code(code, get_eatery_id(token))
    except AuthorisationError as ae:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ae.message) from ae
    except ValidationError as v:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=v.message) from v
