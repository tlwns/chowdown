from typing import List, Literal, Optional, Tuple
from pydantic import BaseModel, AwareDatetime

from db.db_types.db_request import VoucherStatusType

################################################################################
#################################     Auth     #################################
################################################################################

class AuthenticationResponse(BaseModel):
    """
    Used for the output for registration and login routes
    """
    user_id: int
    access_token: str
    user_type: Literal["customer", "eatery"]

################################################################################
################################     Address    ################################
################################################################################

class AddressResponse(BaseModel):
    unit_number: str
    formatted_str: str

################################################################################
#################################    Eatery    #################################
################################################################################

class HomePageEateryInformationResponse(BaseModel):
    eatery_id: int
    eatery_name: str
    thumbnail_uri: str
    num_vouchers: int
    average_rating: float
    top_three_vouchers: List[Tuple[int, str]]

class HomePageResponse(BaseModel):
    eateries: List[HomePageEateryInformationResponse]

class PublicEateryDetailsResponse(BaseModel):
    name: str
    description: str
    address: AddressResponse
    phone_number: str
    thumbnail_uri: str
    menu_uri: Optional[str]
    keywords: List[str]
    average_rating: float

class PrivateEateryDetailsResponse(BaseModel):
    name: str
    email: str
    description: str
    phone_number: str
    address: AddressResponse
    manager_first_name: str
    manager_last_name: str
    abn: str
    thumbnail_uri: str
    menu_uri: Optional[str]
    keywords: List[str]
    date_joined: AwareDatetime
    average_rating: float

class EateryInformationResponse(BaseModel):
    eatery_id: int 
    eatery_name: str 
    thumbnail_uri: str
    num_vouchers: int
    top_three_vouchers: List[Tuple[int, str]]
    average_rating: float

class EaterySearchResponse(BaseModel):
    eateries: List[EateryInformationResponse]

################################################################################
#################################   Customer   #################################
################################################################################

class CustomerDetailsResponse(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    address: AddressResponse

################################################################################
#################################    Voucher    ################################
################################################################################

class EateryVoucherResponse(BaseModel):
    voucher_id: int
    name: str
    description: str
    conditions: str
    total_quantity: int
    unclaimed_quantity: int
    expiry: AwareDatetime

class CustomerVoucherResponse(BaseModel):
    voucher_instance_id: int
    voucher_id: int
    eatery_id: int
    name: str
    description: str
    conditions: str
    expiry: AwareDatetime
    status: VoucherStatusType
    review_id: Optional[int] = None
    given_rating: Optional[float] = None

class EateryVoucherListResponse(BaseModel):
    vouchers: List[EateryVoucherResponse]

class CustomerVoucherListResponse(BaseModel):
    vouchers: List[CustomerVoucherResponse]

class VoucherCreationResponse(BaseModel):
    voucher_template_id: int

class VoucherDetailsResponse(BaseModel):
    eatery_id: int
    name: str
    description: str
    conditions: str
    total_quantity: int
    unclaimed_quantity: int
    expiry: AwareDatetime

class VoucherClaimResponse(BaseModel):
    voucher_instance_id: int

class VoucherInstanceRedeemResponse(BaseModel):
    redemption_code: str

class VoucherRedemptionResponse(BaseModel):
    eatery_id: int
    name: str
    description: str
    conditions: str
    expiry: AwareDatetime

################################################################################
#################################    Reviews    ################################
################################################################################

class ReviewCreationResponse(BaseModel):
    review_id: int

class ReviewDetailedResponse(BaseModel):
    review_id: int
    description: str
    rating: float
    date_created: AwareDatetime
    voucher_id: int
    voucher_name: str
    voucher_instance_id: int
    author_id: Optional[int] = None
    author_name: Optional[str] = None

class EateryReviewListResponse(BaseModel):
    reviews: List[ReviewDetailedResponse]
