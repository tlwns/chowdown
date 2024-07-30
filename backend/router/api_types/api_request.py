from enum import Enum
from datetime import timedelta
from typing import List, Literal, Optional
from pydantic import BaseModel, AwareDatetime

################################################################################
#################################     Auth     #################################
################################################################################

class LoginRequest(BaseModel):
    email: str
    password: str

################################################################################
#################################    Address   #################################
################################################################################

class AddressCreateRequest(BaseModel):
    country: str
    state: str
    city: str
    street: str
    county: str
    postcode: str
    house_number: str
    unit_number: str
    longitude: float
    latitude: float
    fmt_address: str

################################################################################
#################################    Eatery    #################################
################################################################################

class EateryRegistrationRequest(BaseModel):
    email: str
    password: str
    business_name: str
    manager_first_name: str
    manager_last_name: str
    abn: str
    address: AddressCreateRequest
    phone_number: str

class EateryUpdatesRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[AddressCreateRequest] = None
    manager_first_name: Optional[str] = None
    manager_last_name: Optional[str] = None
    thumbnail_uri: Optional[str] = None
    menu_uri: Optional[str] = None
    keywords: Optional[List[str]] = None
    password: Optional[str] = None

class EateryThumbnailUpdateRequest(BaseModel):
    thumbnail_uri: str

class EateryMenuUpdateRequest(BaseModel):
    menu_uri: str

################################################################################
#################################   Customer   #################################
################################################################################

class CustomerRegistrationRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    phone_number: str
    address: AddressCreateRequest

class CustomerUpdatesRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[AddressCreateRequest] = None

class CustomerFavouriteEatery(BaseModel):
    eatery_id: int

class CustomerUnfavouriteEatery(BaseModel):
    eatery_id: int

class CustomerHideEatery(BaseModel):
    eatery_id: int

class CustomerUnhideEatery(BaseModel):
    eatery_id: int

################################################################################
#################################    Voucher    ################################
################################################################################

ScheduleOptions = Literal["daily", "weekly", "fortnightly", "monthly"]

class VoucherCreateRequest(BaseModel):
    eatery_id: int
    name: str
    description: str
    conditions: str
    quantity: int
    release: AwareDatetime
    duration: timedelta
    schedule: Optional[ScheduleOptions] = None

class VoucherClaimRequest(BaseModel):
    customer_id: int

################################################################################
#################################    Reviews    ################################
################################################################################

class ReviewCreateRequest(BaseModel):
    voucher_instance_id: int
    description: str
    rating: float
    anonymous: bool

################################################################################
################################    External    ################################
################################################################################

class SingleAutocompletedAddress(BaseModel):
    name: Optional[str] = None
    country: str
    state: str
    city: Optional[str] = None
    county: Optional[str] = None
    lon: float
    lat: float
    street: Optional[str] = None
    postcode: Optional[str] = None
    house_no: Optional[str] = None
    formatted: str

class AddressAutocompletionResponse(BaseModel):
    results: List[SingleAutocompletedAddress]
#   query: dict

class Sorts(Enum):
    DISTANCE = "distance"
    RATING = "rating"
    VOUCHERS = "vouchers"
    FAVOURITES = "favourites"
    NEWEST = "newest"
    NOT_TRIED = "not_tried"
    KEYWORDS = "keywords"
