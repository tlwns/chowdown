from datetime import datetime, timedelta, timezone
import random
from typing import List, get_args

from pydantic import AwareDatetime

from db.helpers.customer import get_customer_by_id
from db.helpers.eatery import get_eatery_by_id
from db.helpers.review import get_reviews_by_voucher
from db.helpers.voucher import get_voucher_by_id, get_vouchers_by_customer
from db.helpers.voucher_instance import (
    allocate_redemption_code, allocate_voucher_instance, get_voucher_instance_by_id,
    get_voucher_instance_id_by_redemption_code, get_voucher_instances_by_status,
    update_voucher_instance_status
)
from db.helpers.voucher_template import get_voucher_template_by_id, insert_voucher_template
from db.db_types.db_request import ScheduleType, VoucherTemplateCreationRequest

from functionality.errors import AuthorisationError, ValidationError
from functionality.helpers import get_raw_rating
from functionality.message import VoucherBookingEmailRequest, VoucherClaimEmailRequest, send_voucher_booking_email, send_voucher_claiming_email
from functionality.voucher_scheduler import VoucherScheduler

from router.api_types.api_response import VoucherDetailsResponse, VoucherRedemptionResponse, VoucherCreationResponse, \
    VoucherClaimResponse, VoucherInstanceRedeemResponse

COUPON_FORM_DEFAULT_VALUE = None

class VoucherCreationForm:
    MANDATORY_FIELDS = ["title", "description", "conditions", "duration", "quantity", "eid", "release"]

    def __init__(self, **kwargs) -> None:
        self.eid = kwargs["eid"]
        self.title = kwargs["title"]
        self.description = kwargs["description"]
        self.conditions = kwargs["conditions"]
        self.quantity = kwargs["quantity"]
        self.duration = kwargs["duration"]
        self.release = kwargs["release"]
        self.schedule = kwargs["schedule"] if "schedule" in kwargs else None
        self.date_created = datetime.now(timezone.utc)

    def check_mandatory_fields_full(self):
        """
        A function to check that all mandatory fields are full

        Raises ValidationError when mandatory fields are not full
        """
        for field in self.MANDATORY_FIELDS:
            if getattr(self, field) is None:
                raise ValidationError(f"{field} is mandatory")

    def validate_eid(self):
        """
        Checks that the provided eatery id is valid

        A valid eatery id is a int and is an eatery id
        """
        if not isinstance(self.eid, int):
            raise ValidationError("Invalid eatery id type")

        if get_eatery_by_id(self.eid) is None:
            raise ValidationError("No eatery exists with the given eatery id")

    def validate_quantity(self):
        """
        Checks that the provided quantity is valid

        A valid quantity is a int and is greater than or equal to 0
        """
        if not isinstance(self.quantity, int):
            raise ValidationError("Invalid quantity type")

        if self.quantity <= 0:
            raise ValidationError("Quantity cannot be less than or equal 0")

        if self.quantity > 100:
            raise ValidationError("Quantity cannot be greater than 200")

    def validate_valid_dates(self):
        """
        Checks that the provided dates are valid

        A valid date is a datetime object and valid_from is before valid_till
        """
        if not isinstance(self.release, datetime):
            raise ValidationError("Invalid valid from type")

        if not isinstance(self.duration, timedelta):
            raise ValidationError("Invalid valid till type")

    def validate_voucher_form(self):
        """
        Checks the validity of the form
        """
        self.check_mandatory_fields_full()
        self.validate_eid()
        self.validate_quantity()
        self.validate_valid_dates()

    def database_transfer(self) -> int:
        """
        Transfers the voucher form to the database
        """
        voucher_template = VoucherTemplateCreationRequest(
            name=self.title,
            description=self.description,
            conditions=self.conditions,
            created=self.date_created,
            release_date=self.release,
            release_schedule=self.schedule if self.schedule in get_args(ScheduleType) else None,
            duration=self.duration,
            release_size=self.quantity,
            eatery=self.eid,
        )

        vt_id = insert_voucher_template(voucher_template)

        if vt_id is None:
            raise ValidationError("Error inserting voucher template")

        # Add the voucher to the scheduler
        VoucherScheduler().add_voucher(vt_id)

        # Trigger the voucher scheduler
        VoucherScheduler().trigger_voucher_creation()

        return vt_id

def create_voucher(voucher_form: VoucherCreationForm) -> VoucherCreationResponse:
    """
    A function to create a voucher instance

    Return: The id of the voucher (note the distinction from voucher instance)
    """
    # Validate the form
    voucher_form.validate_voucher_form()

    # Create the vouchers
    voucher_template_id = voucher_form.database_transfer()

    return VoucherCreationResponse(
        voucher_template_id=voucher_template_id
    )

def voucher_details(voucher_id: int) -> VoucherDetailsResponse:
    """
    Given a voucher_id, returns the details of such a voucher
    """
    voucher = get_voucher_by_id(voucher_id)

    if voucher is None:
        raise ValidationError("Voucher with that id cannot be found")

    unclaimed = get_voucher_instances_by_status(voucher_id, "unclaimed")

    if unclaimed is None:
        raise ValidationError("Error retrieving unclaimed voucher instances")

    voucher_template = get_voucher_template_by_id(voucher.voucher_template)

    if voucher_template is None:
        raise ValidationError("Error retrieving voucher template")

    return VoucherDetailsResponse(
        eatery_id=voucher_template.eatery,
        name=voucher_template.name,
        description=voucher_template.description,
        conditions=voucher_template.conditions,
        total_quantity=voucher.quantity,
        unclaimed_quantity=len(unclaimed),
        expiry=voucher.expiry_date,
    )

def voucher_claim(voucher_id: int, customer_id: int) -> VoucherClaimResponse:
    """
    Given a voucher_id and customer_id, claims an instance of the voucher for the customer.

    Returns the id of the voucher instance
    """
    # Check that the voucher exists
    voucher = get_voucher_by_id(voucher_id)

    if voucher is None:
        raise ValidationError("Voucher with that id cannot be found")
    if voucher is None or voucher.expiry_date < datetime.now(timezone.utc):
        raise ValidationError("Voucher has expired")

    # Check that the customer exists
    customer = get_customer_by_id(customer_id)

    if customer is None:
        raise ValidationError("Customer with that id cannot be found")

    # Check if the customer already owns an instance of this voucher
    user_vouchers = get_vouchers_by_customer(customer_id)

    if user_vouchers is not None and voucher_id in user_vouchers:
        raise ValidationError("Customer already owns that voucher")

    # Check that there exists an instance of the voucher that is not claimed
    voucher_instances = get_voucher_instances_by_status(voucher_id, "unclaimed")

    if voucher_instances is None or len(voucher_instances) == 0:
        raise ValidationError("No unclaimed vouchers exist")

    # Get the first instance of the voucher
    voucher_instance_id = voucher_instances[0]

    # Claim the voucher instance
    update_voucher_instance_status(voucher_instance_id, "claimed")
    allocate_voucher_instance(voucher_instance_id, customer_id)

    voucher_template = get_voucher_template_by_id(voucher.voucher_template)
    
    if voucher_template is not None:
        eatery = get_eatery_by_id(voucher_template.eatery)

        if eatery is not None:
            send_voucher_claiming_email(customer.email, customer.first_name, VoucherClaimEmailRequest(
                eatery_name=eatery.business_name,
                voucher_name=voucher_template.name,
                voucher_description=voucher_template.description,
                voucher_expiry=voucher.expiry_date
            ))

    # Return id of the voucher instance
    return VoucherClaimResponse(
        voucher_instance_id=voucher_instance_id
    )

def get_vouchers_unclaimed(vouchers: List[int]) -> int:
    """
    Gets the number of vouchers remaining that can be claimed
    """
    num_vouchers = 0
    for vid in vouchers:
        unclaimed_vouchers = get_voucher_instances_by_status(vid, "unclaimed")
        if unclaimed_vouchers is None:
            raise ValidationError("Error retrieving vouchers")

        if len(unclaimed_vouchers) > 0:
            num_vouchers += 1

    return num_vouchers

def generate_unique_voucher_instance_code(voucher_instance_id: int) -> str:
    """
    Given the voucher_instance_id, generates a unique code for the voucher instance

    The code is a 6 digit string

    Side Effect: Inserts the code into the database
    """

    while True:
        code = "".join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])

        try:
            # We handle uniqueness on the database level
            # Most efficient practice
            allocate_redemption_code(voucher_instance_id, code)
            break
        except Exception:
            continue

    return code

def voucher_redeem_instance(voucher_instance_id: int, customer_id: int) -> VoucherInstanceRedeemResponse:
    """
    Given a voucher_instance_id and customer_id, gets a code for the voucher instance
    """
    # Check that the voucher instnace exists
    voucher_instance = get_voucher_instance_by_id(voucher_instance_id)

    if voucher_instance is None:
        raise AuthorisationError("Customer does not own that voucher")

    # Check that the customer has this voucher

    if voucher_instance.customer is None or voucher_instance.customer != customer_id:
        raise AuthorisationError("Customer does not own that voucher")

    # Check that the voucher instance is in claimed state
    instance_status = voucher_instance.status

    if instance_status == "redeemed":
        raise ValidationError("Voucher instance has already been redeemed")
    if instance_status != "claimed":
        raise ValidationError("Voucher instance is not in claimed state")

    # Check the underlying voucher has not yet expired
    voucher_id = voucher_instance.voucher

    voucher = get_voucher_by_id(voucher_id)

    if voucher is None or voucher.expiry_date < datetime.now(timezone.utc):
        raise ValidationError("Voucher has expired")

    # Check if there is already a code
    if voucher_instance.redemption_code is None:
        voucher_instance.redemption_code = generate_unique_voucher_instance_code(voucher_instance_id)
        
        customer = get_customer_by_id(customer_id)
        voucher_template  = get_voucher_template_by_id(voucher.voucher_template)
        

        if customer is not None and voucher_template is not None:
            eatery = get_eatery_by_id(voucher_template.eatery)

            if eatery is not None:
                send_voucher_booking_email(
                    customer.email,
                    customer.first_name,
                    VoucherBookingEmailRequest(
                        eatery_name=eatery.business_name,
                        voucher_name=voucher_template.name,
                        voucher_description=voucher_template.description,
                        voucher_code=voucher_instance.redemption_code,
                        voucher_expiry=voucher.expiry_date
                    )
                )

    return VoucherInstanceRedeemResponse(
        redemption_code=voucher_instance.redemption_code
    )

def voucher_get_redemption_code(code: str, eatery_id: int) -> VoucherRedemptionResponse:
    """
    Given a redemption code and eatery_id, returns details regarding the voucher
    """
    # Get the voucher instance of this code
    voucher_instance_id = get_voucher_instance_id_by_redemption_code(code)

    if voucher_instance_id is None:
        raise AuthorisationError("Eatery does not have access to that code")

    # Get the voucher instance details
    voucher_instance = get_voucher_instance_by_id(voucher_instance_id)

    if voucher_instance is None:
        raise AuthorisationError("Eatery does not have access to that code")

    # Get the voucher details
    voucher = get_voucher_by_id(voucher_instance.voucher)

    if voucher is None:
        raise AuthorisationError("Eatery does not have access to that code")

    voucher_template = get_voucher_template_by_id(voucher.voucher_template)

    # Check that the eatery has access to the voucher
    if voucher_template is None or voucher_template.eatery != eatery_id:
        raise AuthorisationError("Eatery does not have access to that code")

    # Check if the voucher has expired
    if voucher.expiry_date < datetime.now(timezone.utc):
        raise ValidationError("Voucher has expired")

    # Check if the voucher instance is in claimed state
    instance_status = voucher_instance.status

    if instance_status == "redeemed":
        raise ValidationError("Voucher instance has already been redeemed")
    if instance_status != "claimed":
        raise ValidationError("Voucher instance is not in claimed state")

    return VoucherRedemptionResponse(
        eatery_id=eatery_id,
        name=voucher_template.name,
        description=voucher_template.description,
        conditions=voucher_template.conditions,
        expiry=voucher.expiry_date,
    )

def voucher_accept_redemption_code(code: str, eatery_id: int):
    """
    Given a redemption code and eatery_id, accepts the voucher instance and places in 'redeemed' state
    """
    # Get the voucher instance of this code
    voucher_instance_id = get_voucher_instance_id_by_redemption_code(code)

    if voucher_instance_id is None:
        raise AuthorisationError("Eatery does not have access to that code")

    # Get the voucher instance details
    voucher_instance = get_voucher_instance_by_id(voucher_instance_id)

    if voucher_instance is None:
        raise AuthorisationError("Eatery does not have access to that code")

    # Get the voucher details
    voucher = get_voucher_by_id(voucher_instance.voucher)

    if voucher is None:
        raise AuthorisationError("Eatery does not have access to that code")

    voucher_template = get_voucher_template_by_id(voucher.voucher_template)

    # Check that the eatery has access to the voucher
    if voucher_template is None or voucher_template.eatery != eatery_id:
        raise AuthorisationError("Eatery does not have access to that code")

    # Check if the voucher has expired
    if voucher.expiry_date < datetime.now(timezone.utc):
        raise ValidationError("Voucher has expired")

    # Check if the voucher instance is in claimed state
    instance_status = voucher_instance.status

    if instance_status == "redeemed":
        raise ValidationError("Voucher instance has already been redeemed")
    if instance_status != "claimed":
        raise ValidationError("Voucher instance is not in claimed state")

    # Update the voucher instance status
    update_voucher_instance_status(voucher_instance_id, "redeemed")

def voucher_reject_redemption_code(code: str, eatery_id: int):
    """
    Given a redemption code and eatery_id, rejects the redemption

    Note: This will not cause a state change in current state
    """
    # Get the voucher instance of this code
    voucher_instance_id = get_voucher_instance_id_by_redemption_code(code)

    if voucher_instance_id is None:
        raise AuthorisationError("Eatery does not have access to that code")

    # Get the voucher instance details
    voucher_instance = get_voucher_instance_by_id(voucher_instance_id)

    if voucher_instance is None:
        raise AuthorisationError("Eatery does not have access to that code")

    # Get the voucher details
    voucher = get_voucher_by_id(voucher_instance.voucher)

    if voucher is None:
        raise AuthorisationError("Eatery does not have access to that code")

    voucher_template = get_voucher_template_by_id(voucher.voucher_template)

    # Check that the eatery has access to the voucher
    if voucher_template is None or voucher_template.eatery != eatery_id:
        raise AuthorisationError("Eatery does not have access to that code")

    # Check if the voucher has expired
    if voucher.expiry_date < datetime.now(timezone.utc):
        raise ValidationError("Voucher has expired")

    # Check if the voucher instance is in claimed state
    instance_status = voucher_instance.status

    if instance_status == "redeemed":
        raise ValidationError("Voucher instance has already been redeemed")
    if instance_status != "claimed":
        raise ValidationError("Voucher instance is not in claimed state")

def get_average_voucher_rating(voucher_id: int) -> float:
    """
    Gets an vouchers average rating
    """
    reviews = get_reviews_by_voucher(voucher_id)
    if reviews is None:
        raise ValueError("Error retrieving reviews")

    if reviews is None or len(reviews) == 0:
        return 0

    ratings = get_raw_rating(reviews)
    return round(sum(ratings) / len(ratings), 1)

def get_expiry(voucher_id: int) -> AwareDatetime:
    """
    Gets an vouchers average rating
    """
    review = get_voucher_by_id(voucher_id)

    if review is None:
        raise ValueError("Error retrieving reviews")

    return review.expiry_date
