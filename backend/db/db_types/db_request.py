from datetime import timedelta
from typing import Optional, Literal
from pydantic import BaseModel, AwareDatetime

################################################################################
#################################     Auth     #################################
################################################################################

class SessionCreationRequest(BaseModel):
    refresh_token: str
    time_last_updated: AwareDatetime
    eatery: Optional[int] = None
    customer: Optional[int] = None

################################################################################
#################################    Address    ################################
################################################################################

class AddressCreationRequest(BaseModel):
    unit_number: str
    house_number: str
    street_addr: str
    city: str
    state: str
    county: str #added must handle
    country: str
    postcode: str
    longitude: float
    latitude: float
    formatted_str: str

################################################################################
#################################    Eatery    #################################
################################################################################

class EateryCreationRequest(BaseModel):
    business_name: str
    email: str
    password: str
    phone: str
    address: AddressCreationRequest
    manager_first_name: str
    manager_last_name: str
    abn: str
    date_joined: AwareDatetime
    description: Optional[str] = None

################################################################################
#################################   Customer   #################################
################################################################################

class CustomerCreationRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str
    address: AddressCreationRequest
    date_joined: AwareDatetime

################################################################################
#################################    Voucher    ################################
################################################################################

VoucherStatusType = Literal["unpublished", "unclaimed", "claimed", "redeemed", "reserved"]
ScheduleType = Literal["daily", "weekly", "fortnightly", "monthly"]

class VoucherTemplateCreationRequest(BaseModel):
    name: str
    description: str
    conditions: str
    created: AwareDatetime
    release_date: AwareDatetime
    release_schedule: Optional[ScheduleType] = None
    duration: timedelta
    release_size: int
    eatery: int
    is_published: Optional[bool] = None
    is_deleted: Optional[bool] = None

class VoucherCreationRequest(BaseModel):
    voucher_template: int
    release_date: AwareDatetime
    expiry_date: AwareDatetime

class VoucherInstanceCreationRequest(BaseModel):
    status: Optional[VoucherStatusType] = None
    voucher: int
    qty: int

class VoucherInstanceAllocationRequest(BaseModel):
    voucher_id: int
    customer_id: str

################################################################################
################################     Reviews    ################################
################################################################################

class ReviewCreationRequest(BaseModel):
    description: str
    rating: float
    created: AwareDatetime
    voucher_instance: int
    anonymous: bool

################################################################################
#################################    Reports    ################################
################################################################################

class ReportCreationRequest(BaseModel):
    description: str
    created: AwareDatetime
    voucher_instance: int
