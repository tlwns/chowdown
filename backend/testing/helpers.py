import json
import random
from datetime import datetime, timedelta, timezone
import data_url
from pydantic import TypeAdapter

from testing.test_helpers import create_voucher, claim_voucher, redeem_voucher_instance, create_review, \
    accept_redemption_code

# Load data from JSON file
with open('testing/test_data.json', encoding="utf8") as file:
    test_data = json.load(file)

# Fetching required test_data
non_anon_review_data = test_data["review_data"]["non_anonymous"]
anon_review_data = test_data["review_data"]["anonymous"]

def eatery_create_voucher(eatery_header, voucher_create_payload):
    """
    Creates a voucher for an eatery based on given details
    """
    eatery_response = create_voucher(eatery_header, voucher_create_payload)

    assert eatery_response.status_code == 200
    assert "voucher_template_id" in eatery_response.json()
    return eatery_response.json().get("voucher_template_id")

def customer_claim_voucher(customer_id, voucher_id, customer_header):
    """
    Claims a voucher for a customer
    """
    voucher_claim_payload = {"customer_id": customer_id}
    customer_response = claim_voucher(voucher_id, customer_header, voucher_claim_payload)
    assert customer_response.status_code == 200
    assert "voucher_instance_id" in customer_response.json()
    return customer_response.json().get("voucher_instance_id")

def customer_redeem_voucher_instance(voucher_instance_id, customer_header):
    """
    Redeems a voucher for a customer
    """
    redeem_response = redeem_voucher_instance(voucher_instance_id, customer_header)
    assert redeem_response.status_code == 200
    assert "redemption_code" in redeem_response.json()
    return redeem_response.json().get("redemption_code")

def compare_expiry_in_response(json_expiry, expected_expiry: datetime):
    """
    Compares expiry details of the voucher with actual expiry
    """
    assert json_expiry == str(expected_expiry).replace("+00:00", "Z").replace(" ", "T")

def timedelta_to_iso8601(delta: timedelta) -> str:
    """
    Takes in a timedelta and outputs a iso8601 string
    """
    timedelta_adapter = TypeAdapter(timedelta)

    return timedelta_adapter.dump_python(delta, mode="json")

def create_voucher_payload(voucher, eatery_id, quantity=2, duration=None, schedule=None):
    """
    Creates voucher payload with dynamic fields
    """
    release = datetime.now(timezone.utc)

    voucher["eatery_id"] = eatery_id
    voucher["quantity"] = quantity
    voucher["release"] = release.isoformat()
    voucher["duration"] = duration if duration else timedelta_to_iso8601(timedelta(days=30))
    voucher["schedule"] = schedule if schedule else None

    return {
        "release": release,
        "voucher": voucher
    }

def make_image_uri(image_path):
    """
    Create image URI of MIMEType image/jpeg
    """
    with open(image_path, 'rb') as image:
        data = image.read()

    return data_url.construct_data_url(mime_type='image/jpeg', base64_encode=True, data=data)

def make_pdf_uri(image_path):
    """
    Create pdf URI of MIMEType application/pdf
    """
    with open(image_path, 'rb') as image:
        data = image.read()

    return data_url.construct_data_url(mime_type='application/pdf', base64_encode=True, data=data)

def create_anonymous_reviews(review, voucher_instance_id):
    """
    Creates anonymous review payload with dynamic fields
    """
    review["anonymous"] = True
    review["voucher_instance_id"] = voucher_instance_id

    return review

def create_non_anonymous_reviews(review, voucher_instance_id):
    """
    Creates non anonymous review payload with dynamic fields
    """
    review["anonymous"] = False
    review["voucher_instance_id"] = voucher_instance_id

    return review

def eatery_leave_review(customer_id, customer_header, eatery_id, eatery_header, voucher_id):
    """
    Creates a review for an Eatery using specified Customer credentials
    """
    # Randomly choosing a review type from a list of available review types
    review_type = random.choice(["anonymous", "non_anonymous"])

    # Randomly choosing a review from a list of available reviews
    review_no = random.randint(1, 10)

    # Customer claims voucher
    voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

    # Customer redeems the voucher instance
    redemption_code = redeem_voucher_instance(voucher_instance_id, customer_header)

    # Eatery accepts customer's redemption code
    accept_redemption_code(redemption_code, eatery_header)

    # Customer leaves a review for Eatery
    if review_type == "anonymous":
        review_payload = create_anonymous_reviews(anon_review_data[str(review_no)], voucher_instance_id)
    else:
        review_payload = create_non_anonymous_reviews(non_anon_review_data[str(review_no)], voucher_instance_id)
    
    return create_review(eatery_id, customer_header, review_payload)
