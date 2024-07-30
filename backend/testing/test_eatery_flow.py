import json
import os
import random

from testing.test_helpers import list_eateries, register_eatery, view_eatery_vouchers, view_eatery_public_details, \
    view_eatery_private_details, update_eatery_details, login_eatery, register_customer, create_review, \
    redeem_voucher_instance, accept_redemption_code
from testing.helpers import eatery_create_voucher, create_voucher_payload, make_image_uri, make_pdf_uri, \
    eatery_leave_review, create_anonymous_reviews, customer_claim_voucher

from logger import log_purple

# Load data from JSON file
with open("testing/test_data.json", encoding="utf8") as file:
    test_data = json.load(file)

# Fetching test_data
register_data = test_data["register_data"]
login_data = test_data["login_data"]
voucher_data = test_data["voucher_data"]
keyword_data = test_data["keyword_data"]
description_data = test_data["description_data"]
anon_review_data = test_data["review_data"]["anonymous"]

class TestEateryListFlow:
    def test_empty_list_of_eateries(self, reset_db):
        eateries = list_eateries()
        assert len(eateries) == 0

    def test_successful_list_of_multiple_eateries(self, reset_db):
        # Create 4 eateries
        for key in range(1, 5):
            register_eatery(register_data["eatery"][str(key)])

        # Get eatery count and expect 4
        eateries = list_eateries()
        assert len(eateries) == 4

        # Check if they are the same ones as we created by matching their names
        names = [eatery["eatery_name"] for eatery in eateries]
        business_names = [register_data["eatery"][str(key)]["business_name"] for key in range(1, 5)]
        # we know these 4 eateries had unique names
        assert set(names) == set(business_names)

class TestEateryDetailsFlow:
    def test_public_details(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get public details of Eatery
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "name" in details
        assert "address" in details
        assert "unit_number" in details["address"]
        assert "formatted_str" in details["address"]
        assert "phone_number" in details

        # Check if the Eatery's public details are current
        assert details["name"] == register_data["eatery"]["1"]["business_name"]
        assert details["address"]["unit_number"] == register_data["eatery"]["1"]["address"]["unit_number"]
        assert details["address"]["formatted_str"] == register_data["eatery"]["1"]["address"]["fmt_address"]
        assert details["phone_number"] == register_data["eatery"]["1"]["phone_number"]

    def test_private_details(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "name" in details
        assert "address" in details
        assert "unit_number" in details["address"]
        assert "formatted_str" in details["address"]
        assert "phone_number" in details
        assert "manager_first_name" in details
        assert "manager_last_name" in details

        # Check if the Eatery's private details are current
        assert details["name"] == register_data["eatery"]["1"]["business_name"]
        assert details["address"]["unit_number"] == register_data["eatery"]["1"]["address"]["unit_number"]
        assert details["address"]["formatted_str"] == register_data["eatery"]["1"]["address"]["fmt_address"]
        assert details["phone_number"] == register_data["eatery"]["1"]["phone_number"]
        assert details["manager_first_name"] == register_data["eatery"]["1"]["manager_first_name"]
        assert details["manager_last_name"] == register_data["eatery"]["1"]["manager_last_name"]

    def test_update_name(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get public details of Eatery
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "name" in details

        # Check if the Eatery's name is current in public details
        assert details["name"] == register_data["eatery"]["1"]["business_name"]

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "name" in details

        # Check if the Eatery's name is current in private details
        assert details["name"] == register_data["eatery"]["1"]["business_name"]

        # Update Eatery's name
        payload = {"name": register_data["eatery"]["2"]["business_name"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        # Get public details of Eatery again
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "name" in details

        # Check if the Eatery's name has been updated in public details
        assert details["name"] == register_data["eatery"]["2"]["business_name"]

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "name" in details

        # Check if the Eatery's name has been updated in private details
        assert details["name"] == register_data["eatery"]["2"]["business_name"]

    def test_update_unique_email(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Update Eatery's email
        payload = {"email": register_data["eatery"]["2"]["email"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        payload = login_data["eatery"]["1"].copy()
        payload["email"] = login_data["eatery"]["2"]["email"]
        login_eatery(payload)

    def test_update_non_unique_email(self, reset_db):
        # Create eatery1
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create an eatery2
        register_eatery(register_data["eatery"]["2"]).values()

        # Update Eatery's phone_number
        payload = {"phone_number": register_data["eatery"]["2"]["phone_number"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 400

    def test_update_unique_phone_number(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get public details of Eatery
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "phone_number" in details

        # Check if the Eatery's phone_number is current in public details
        assert details["phone_number"] == register_data["eatery"]["1"]["phone_number"]

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "phone_number" in details

        # Check if the Eatery's phone_number is current in private details
        assert details["phone_number"] == register_data["eatery"]["1"]["phone_number"]

        # Update Eatery's phone_number
        payload = {"phone_number": register_data["eatery"]["2"]["phone_number"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        # Get public details of Eatery again
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "phone_number" in details

        # Check if the Eatery's phone_number has been updated in public details
        assert details["phone_number"] == register_data["eatery"]["2"]["phone_number"]

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "phone_number" in details

        # Check if the Eatery's phone_number has been updated in private details
        assert details["phone_number"] == register_data["eatery"]["2"]["phone_number"]

    def test_update_non_unique_phone_number(self, reset_db):
        # Create eatery1
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create an eatery2
        register_eatery(register_data["eatery"]["2"]).values()

        # Update Eatery's phone_number
        payload = {"phone_number": register_data["eatery"]["2"]["phone_number"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 400

    def test_update_address(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get public details of Eatery
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "address" in details
        assert "unit_number" in details["address"]
        assert "formatted_str" in details["address"]

        # Check if the Eatery's address is current in public details
        assert details["address"]["unit_number"] == register_data["eatery"]["1"]["address"]["unit_number"]
        assert details["address"]["formatted_str"] == register_data["eatery"]["1"]["address"]["fmt_address"]

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "address" in details
        assert "unit_number" in details["address"]
        assert "formatted_str" in details["address"]

        # Check if the Eatery's address is current in private details
        assert details["address"]["unit_number"] == register_data["eatery"]["1"]["address"]["unit_number"]
        assert details["address"]["formatted_str"] == register_data["eatery"]["1"]["address"]["fmt_address"]

        # Update Eatery's address
        payload = {"address": register_data["eatery"]["2"]["address"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        # Get public details of Eatery again
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "address" in details
        assert "unit_number" in details["address"]
        assert "formatted_str" in details["address"]

        # Check if the Eatery's address has been updated in public details
        assert details["address"]["unit_number"] == register_data["eatery"]["2"]["address"]["unit_number"]
        assert details["address"]["formatted_str"] == register_data["eatery"]["2"]["address"]["fmt_address"]

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "address" in details
        assert "unit_number" in details["address"]
        assert "formatted_str" in details["address"]

        # Check if the Eatery's address has been updated in private details
        assert details["address"]["unit_number"] == register_data["eatery"]["2"]["address"]["unit_number"]
        assert details["address"]["formatted_str"] == register_data["eatery"]["2"]["address"]["fmt_address"]

    def test_update_manager_first_name(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "manager_first_name" in details

        # Check if the Eatery manager's first name is current
        assert details["manager_first_name"] == register_data["eatery"]["1"]["manager_first_name"]

        # Update Eatery manager's first name
        payload = {"manager_first_name": register_data["eatery"]["2"]["manager_first_name"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "manager_first_name" in details
        
        # Check if the Eatery manager's first name has been updated
        assert details["manager_first_name"] == register_data["eatery"]["2"]["manager_first_name"]

    def test_update_manager_last_name(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "manager_last_name" in details

        # Check if the Eatery manager's last name is current
        assert details["manager_last_name"] == register_data["eatery"]["1"]["manager_last_name"]

        # Update Eatery manager's last name
        payload = {"manager_last_name": register_data["eatery"]["2"]["manager_last_name"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "manager_last_name" in details
        
        # Check if the Eatery manager's last name has been updated
        assert details["manager_last_name"] == register_data["eatery"]["2"]["manager_last_name"]

    def test_update_description(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get public details of Eatery
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "description" in details

        # Check if the Eatery's description is current in public details
        assert details["description"] == ''

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "description" in details

        # Check if the Eatery's description is current in private details
        assert details["description"] == ''

        # Update Eatery's description
        payload = {"description": description_data["1"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        # Get public details of Eatery again
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "description" in details

        # Check if the Eatery's description has been updated in public details
        assert details["description"] == description_data["1"]

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "description" in details

        # Check if the Eatery's description has been updated in private details
        assert details["description"] == description_data["1"]

    def test_update_keywords(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get public details of Eatery
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "keywords" in details

        # Check if the Eatery's keywords is current in public details
        assert details["keywords"] == []

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "keywords" in details

        # Check if the Eatery's keywords is current in private details
        assert details["keywords"] == []

        # Update Eatery's keywords
        payload = {"keywords": keyword_data["1"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        keywords = [keyword.lower() for keyword in keyword_data["1"]]

        # Get public details of Eatery again
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "keywords" in details

        # Check if the Eatery's keywords has been updated in public details
        assert set(details["keywords"]) == set(keywords)

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "keywords" in details

        # Check if the Eatery's keywords has been updated in private details
        assert set(details["keywords"]) == set(keywords)

    def test_update_password(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Update Eatery's password
        payload = {"password": register_data["eatery"]["2"]["password"]}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        payload = login_data["eatery"]["1"].copy()
        payload["password"] = login_data["eatery"]["2"]["password"]
        login_eatery(payload)

    def test_update_thumbnail_uri(self, reset_db): 
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        log_purple(f"cwd {os.getcwd()}")
        log_purple(f"listdir {os.listdir(os.getcwd())}")

        # Get public details of Eatery
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "thumbnail_uri" in details

        # Check if the Eatery's thumbnail_uri is not set in public details
        assert details["thumbnail_uri"] == "/eatery_thumbnail.webp"

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "thumbnail_uri" in details

        # Check if the Eatery's thumbnail_uri is not set in private details
        assert details["thumbnail_uri"] == "/eatery_thumbnail.webp"

        thumbnail_uri_data = make_image_uri('dummy/1-drink.jpeg')

        # Update Eatery's thumbnail_uri
        payload = {"thumbnail_uri": thumbnail_uri_data}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        # Get public details of Eatery again
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "thumbnail_uri" in details

        # Check if the Eatery's thumbnail_uri has been updated in public details
        assert details["thumbnail_uri"] == thumbnail_uri_data

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "thumbnail_uri" in details

        # Check if the Eatery's thumbnail_uri has been updated in private details
        assert details["thumbnail_uri"] == thumbnail_uri_data
    
    def test_update_menu_uri(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get public details of Eatery
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "menu_uri" in details

        # Check if the Eatery's menu_uri is not set in public details
        assert details["menu_uri"] == None

        # Get private details of Eatery
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "menu_uri" in details

        # Check if the Eatery's menu_uri is not set in private details
        assert details["menu_uri"] == None

        menu_uri_data = make_pdf_uri('dummy/1-drink.pdf')

        # Update Eatery's menu_uri
        payload = {"menu_uri": menu_uri_data}
        assert update_eatery_details(eatery_id, eatery_header, payload).status_code == 200

        # Get public details of Eatery again
        details_response = view_eatery_public_details(eatery_id)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "menu_uri" in details

        # Check if the Eatery's menu_uri has been updated in public details
        assert details["menu_uri"] == menu_uri_data

        # Get private details of Eatery again
        details_response = view_eatery_private_details(eatery_id, eatery_header)
        assert details_response.status_code == 200
        details = details_response.json()
        assert "menu_uri" in details

        # Check if the Eatery's menu_uri has been updated in private details
        assert details["menu_uri"] == menu_uri_data

class TestEateryVouchersFlow:
    def test_get_eatery_routes(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Get eatery's vouchers and expect none
        vouchers = view_eatery_vouchers(eatery_id)
        assert len(vouchers) == 0

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        eatery_create_voucher(eatery_header, voucher_create_payload)

        # Get eatery's vouchers and expect one voucher
        vouchers = view_eatery_vouchers(eatery_id)
        assert len(vouchers) == 1

class TestEateryReviewsFlow:
    def test_create_for_non_existent_eatery(self, reset_db):
        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}
        
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery accepts customer's redemption code
        accept_redemption_code(redemption_code, eatery_header)
        
        review_payload = create_anonymous_reviews(anon_review_data[str("1")], voucher_instance_id)
        assert create_review("12345", customer_header, review_payload).status_code == 400

    def test_create_review_for_unrelated_voucher(self, reset_db):
        # Create customer1
        _, customer1_access_token, customer1_id = register_customer(register_data["customer"]["1"]).values()
        customer1_header = {"Authorization": "bearer " + customer1_access_token}
        
        # Create customer2
        _, customer2_access_token, customer2_id = register_customer(register_data["customer"]["2"]).values()
        customer2_header = {"Authorization": "bearer " + customer2_access_token}

        # Create a eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create voucher1
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher1_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Create voucher2
        _, voucher_create_payload = create_voucher_payload(voucher_data["2"], eatery_id).values()
        voucher2_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer1 claims voucher1
        voucher_instance1_id = customer_claim_voucher(customer1_id, voucher1_id, customer1_header)

        # Customer2 claims voucher2
        voucher_instance2_id = customer_claim_voucher(customer2_id, voucher2_id, customer2_header)

        # Customer1 redeems the voucher instance
        redemption_code = redeem_voucher_instance(voucher_instance1_id, customer1_header)

        # Eatery accepts customer's redemption code
        accept_redemption_code(redemption_code, eatery_header)
        
        review_payload = create_anonymous_reviews(anon_review_data[str("1")], voucher_instance2_id)
        assert create_review(eatery_id, customer1_header, review_payload).status_code == 400

    def test_create_review_with_negative_rating(self, reset_db):
        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}
        
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery accepts customer's redemption code
        accept_redemption_code(redemption_code, eatery_header)
        
        review_payload = create_anonymous_reviews(anon_review_data[str("1")].copy(), voucher_instance_id)
        review_payload["rating"] = -1.3
        assert create_review(eatery_id, customer_header, review_payload).status_code == 400

    def test_create_review_with_rating_above_5(self, reset_db):
        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}
        
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery accepts customer's redemption code
        accept_redemption_code(redemption_code, eatery_header)
        
        review_payload = create_anonymous_reviews(anon_review_data[str("1")].copy(), voucher_instance_id)
        review_payload["rating"] = 5.3
        assert create_review(eatery_id, customer_header, review_payload).status_code == 400

    def test_create_review_without_claiming(self, reset_db):
        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}
        
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)
        
        review_payload = create_anonymous_reviews(anon_review_data[str("1")], "1")
        assert create_review(eatery_id, customer_header, review_payload).status_code == 400

    def test_create_review_without_redeeming(self, reset_db):
        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}
        
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        review_payload = create_anonymous_reviews(anon_review_data[str("1")], voucher_instance_id)
        assert create_review(eatery_id, customer_header, review_payload).status_code == 400

    def test_empty_list_of_reviews(self, reset_db):
        # Create 4 eateries
        for key in range(1, 5):
            register_eatery(register_data["eatery"][str(key)])
        
        # Get eatery count and expect 4
        eateries = list_eateries()
        assert len(eateries) == 4

        # Check if all eateries have 0 average rating (since no reviews exist)
        for eatery in eateries:
            assert eatery["average_rating"] == 0

    def test_successful_list_of_multiple_reviews(self, reset_db):
        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create 4 eateries
        for key in range(1, 5):
            _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"][str(key)]).values()
            eatery_header = {"Authorization": "bearer " + eatery_access_token}

            randint = random.randint(2, 5)

            for _ in range(1, randint):
                voucher = random.randint(1, 20)
                _, voucher_create_payload = create_voucher_payload(voucher_data[str(voucher)], eatery_id).values()
                voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)
                eatery_leave_review(customer_id, customer_header, eatery_id, eatery_header, voucher_id)
            
            vouchers = view_eatery_vouchers(eatery_id)
            assert len(vouchers) == randint - 1

        # Get eatery count and expect 4
        eateries = list_eateries()
        assert len(eateries) == 4
