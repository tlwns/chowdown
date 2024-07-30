from datetime import timedelta
from typing import Literal, Optional
from pydantic import BaseModel, AwareDatetime

from db.db_types.db_request import VoucherStatusType

################################################################################
#################################     Auth     #################################
################################################################################

class SessionDetailsResponse(BaseModel):
    refresh_token: str
    time_last_updated: AwareDatetime
    eatery: Optional[int] = None
    customer: Optional[int] = None

################################################################################
#################################    Address    ################################
################################################################################

class AddressDetailsResponse(BaseModel):
    unit_number: str
    house_number: str
    street_addr: str
    city: str
    state: str
    country: str
    postcode: str
    longitude: float
    latitude: float
    formatted_str: str

################################################################################
#################################    Eatery    #################################
################################################################################

class EateryDetailsResponse(BaseModel):
    business_name: str
    email: str
    phone: str
    manager_first_name: str
    manager_last_name: str
    abn: str
    date_joined: AwareDatetime
    address: AddressDetailsResponse
    description: str
    thumbnail: str
    menu: Optional[str] = None

################################################################################
#################################   Customer   #################################
################################################################################

class CustomerDetailsResponse(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: AddressDetailsResponse
    date_joined: AwareDatetime
    is_deleted: bool

################################################################################
#################################    Voucher    ################################
################################################################################

ScheduleType = Literal["daily", "weekly", "fortnightly", "monthly"]

class VoucherTemplateDetailsResponse(BaseModel):
    name: str
    description: str
    conditions: str
    created: AwareDatetime
    eatery: int
    quantity: int
    is_deleted: bool
    is_published: bool

class VoucherTemplateScheduleDetailsResponse(BaseModel):
    is_deleted: bool
    release_date: AwareDatetime
    release_schedule: Optional[ScheduleType] = None
    release_duration: timedelta
    release_size: int
    last_release: Optional[AwareDatetime] = None

class VoucherDetailsResponse(BaseModel):
    voucher_template: int
    release_date: AwareDatetime
    expiry_date: AwareDatetime
    quantity: int

class VoucherInstanceDetailsResponse(BaseModel):
    status: VoucherStatusType
    redemption_code: Optional[str] = None
    voucher: int
    customer: Optional[int] = None
    reviewed: bool

################################################################################
################################     Reviews    ################################
################################################################################

class ReviewDetailsResponse(BaseModel):
    description: str
    rating: float
    created: AwareDatetime
    voucher_instance: int
    anonymous: bool

################################################################################
#################################    Reports    ################################
################################################################################

class ReportDetailsResponse(BaseModel):
    description: str
    created: AwareDatetime
    voucher_instance: int
