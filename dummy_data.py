import json
import requests
import random
from datetime import datetime, timezone, timedelta
import data_url
from pydantic import TypeAdapter

# Load data from JSON file
with open('backend/testing/test_data.json', encoding="utf8") as file:
    test_data = json.load(file)

# Fetching required test_data
register_data = test_data["register_data"]
voucher_data = test_data["voucher_data"]
non_anon_review_data = test_data["review_data"]["non_anonymous"]
anon_review_data = test_data["review_data"]["anonymous"]
file_data = test_data["file_data"]
keyword_data = test_data["keyword_data"]
description_data = test_data["description_data"]

URL = f'http://localhost:8080'

def clear_all_database_tables():
    """
    Clears the database
    """
    requests.delete(URL + "/db/clear/all")

def register_customer(payload):
    """
    Registers the Customer
    """
    response = requests.post(URL + "/auth/register/customer", json=payload)
    
    assert response.status_code == 200
    assert "user_id" in response.json(), "missing: user id"
    assert "user_type" in response.json(), "missing: user type"
    
    return {
        "access_token": response.json().get("access_token"),
        "user_id": response.json().get("user_id")
    }

def register_eatery(payload):
    """
    Registers the Eatery
    """
    response = requests.post(URL + "/auth/register/eatery", json=payload)

    assert response.status_code == 200
    assert "user_id" in response.json(), "missing: user id"
    assert "user_type" in response.json(), "missing: user type"

    return {
        "access_token": response.json().get("access_token"),
        "user_id": response.json().get("user_id")
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

def update_eatery_thumbnail(eatery_id, header, thumbnail):
    """
    Updates the eatery's thumbnail
    """
    payload = {"thumbnail_uri": thumbnail}
    return requests.put(URL + "/eatery/" + str(eatery_id) + "/thumbnail", headers=header, json=payload)

def update_eatery_menu(eatery_id, header, menu):
    """
    Updates the eatery's menu
    """
    payload = {"menu_uri": menu}
    return requests.put(URL + "/eatery/" + str(eatery_id) + "/menu", headers=header, json=payload)

def update_eatery_keywords(eatery_id, header, keywords):
    """
    Updates the eatery's keywords 
    """
    payload = {"keywords": keywords}
    return requests.put(URL + "/eatery/" + str(eatery_id) + "/details", headers=header, json=payload)

def update_eatery_description(eatery_id, header, description):
    """
    Updates the eatery's description
    """
    payload = {"description": description}
    return requests.put(URL + "/eatery/" + str(eatery_id) + "/details", headers=header, json=payload)

def create_voucher(header, payload):
    """
    Creates a Voucher
    """
    response = requests.post(URL + "/voucher", headers=header, json=payload)

    assert response.status_code == 200
    assert "voucher_template_id" in response.json(), "missing: voucher template id"

    return response.json().get("voucher_template_id")

def claim_voucher(customer_id, voucher_id, header):
    """
    Claims a Voucher
    """
    payload = {"customer_id": customer_id}
    response = requests.put(URL + "/voucher/claim/" + str(voucher_id), headers=header, json=payload)

    assert response.status_code == 200
    assert "voucher_instance_id" in response.json(), "missing: voucher instance id"

    return response.json().get("voucher_instance_id")

def redeem_voucher_instance(voucher_instance_id, header):
    """
    Redeems a Voucher
    """
    response = requests.put(URL + "/voucher/instance/" + str(voucher_instance_id) + "/redeem", headers=header)

    assert response.status_code == 200
    assert "redemption_code" in response.json(), "missing: redemption code"

    return response.json().get("redemption_code")

def accept_redemption_code(redemption_code, header):
    """
    Accepts Redemption Code provided by Customer
    """
    return requests.put(URL + "/voucher/redemption/" + str(redemption_code) + "/accept", headers=header)

def create_review(eatery_id, header, payload):
    """
    Creates a Review
    """
    return requests.post(URL + "/eatery/" + str(eatery_id) + "/reviews", headers=header, json=payload)

def timedelta_to_iso8601(delta: timedelta):
    """
    Converts timedelta to ISO8601 string
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

    return voucher

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

def leave_review(customer_id, customer_header, eatery_id, eatery_header, voucher_id):
    """
    Creates a review for an Eatery using specified Customer credentials
    """
    # Randomly choosing a review type from a list of available review types
    review_type = random.choice(["anonymous", "non_anonymous"])

    # Randomly choosing a review from a list of available reviews
    review_no = random.randint(1, 10)

    # Customer claims voucher
    voucher_instance_id = claim_voucher(customer_id, voucher_id, customer_header)

    # Customer redeems the voucher instance
    redemption_code = redeem_voucher_instance(voucher_instance_id, customer_header)

    # Eatery accepts customer's redemption code
    accept_redemption_code(redemption_code, eatery_header)

    # Customer leaves a review for Eatery
    if review_type == "anonymous":
        review_payload = create_anonymous_reviews(anon_review_data[str(review_no)], voucher_instance_id)
    else:
        review_payload = create_non_anonymous_reviews(non_anon_review_data[str(review_no)], voucher_instance_id)
    create_review(eatery_id, customer_header, review_payload)

def inject_dummy_data():
    """
    Injects dummy data for demonstration purposes
    """
    # Clean database
    clear_all_database_tables()

    # Create customer1
    customer1_access_token, customer1_id = register_customer(register_data["customer"]["1"]).values()
    customer1_header = {"Authorization": "bearer " + customer1_access_token}

    # Create customer2
    customer2_access_token, customer2_id = register_customer(register_data["customer"]["2"]).values()
    customer2_header = {"Authorization": "bearer " + customer2_access_token}

    vouchers = {
        "with_reviews": {
            1: [1, 2, 3],
            2: [4],
            3: [5],
            5: [7, 8],
            7: [11, 12, 13],
            9: [15],
            10: [16],
            11: [18],
            14: [1, 2],
            15: [4, 5, 6, 8, 9, 10],
            19: [13, 14, 15],
            20: [16]
        },
        "without_reviews": {
            3: [6],
            7: [10],
            8: [9],
            9: [20],
            11: [17, 19],
            12: [18, 19],
            18: [20],
            15: [3],
            16: [7, 11, 12],
            20: [17],
        }
    }

    for eatery in range(1, 21):
        # Create eatery
        eatery_access_token, eatery_id = register_eatery(register_data["eatery"][str(eatery)]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Update eatery's thumbnail and menu
        update_eatery_thumbnail(eatery_id, eatery_header, make_image_uri(f"backend/dummy/{file_data[str(eatery)]}.jpeg"))
        update_eatery_menu(eatery_id, eatery_header, make_pdf_uri(f"backend/dummy/{file_data[str(eatery)]}.pdf"))

        # Update eatery's keywords and description
        update_eatery_keywords(eatery_id, eatery_header, keyword_data[str(eatery)])
        update_eatery_description(eatery_id, eatery_header, description_data[str(eatery)])

        # Creating vouchers that will not have any reviews
        if eatery in vouchers["without_reviews"]:
            for voucher in vouchers["without_reviews"][eatery]:
                voucher_create_payload = create_voucher_payload(voucher_data[str(voucher)], eatery_id)
                create_voucher(eatery_header, voucher_create_payload)
        
        # Creating vouchers that will have reviews
        if eatery in vouchers["with_reviews"]:
            for voucher in vouchers["with_reviews"][eatery]:
                # Eatery creates a voucher 
                voucher_create_payload = create_voucher_payload(voucher_data[str(voucher)], eatery_id)
                voucher_id = create_voucher(eatery_header, voucher_create_payload)
                
                # Randomly choosing a reviewer from a list of available reviewers
                random_reviewer = random.choice(["customer1", "customer2", "both"])

                if random_reviewer == "customer_1":
                    leave_review(customer1_id, customer1_header, eatery_id, eatery_header, voucher_id)
                elif random_reviewer == "customer_2":
                    leave_review(customer2_id, customer2_header, eatery_id, eatery_header, voucher_id)
                else:
                    leave_review(customer1_id, customer1_header, eatery_id, eatery_header, voucher_id)
                    leave_review(customer2_id, customer2_header, eatery_id, eatery_header, voucher_id)

    print("\033[95mFinished inserting dummy data.\033[0m")

if __name__ == "__main__":
    inject_dummy_data()
