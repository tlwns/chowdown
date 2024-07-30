import json
from datetime import timedelta

from testing.test_helpers import register_customer, register_eatery, accept_redemption_code, claim_voucher, \
    create_voucher, get_redemption_code_details, redeem_voucher_instance, reject_redemption_code, view_customer_vouchers

from testing.helpers import eatery_create_voucher, customer_claim_voucher, customer_redeem_voucher_instance, \
    compare_expiry_in_response, create_voucher_payload

# Load data from JSON file
with open("testing/test_data.json", encoding="utf8") as file:
    test_data = json.load(file)

# Fetching test_data
register_data = test_data["register_data"]
login_data = test_data["login_data"]
voucher_data = test_data["voucher_data"]

class TestVoucherFlow:
    def test_voucher_creation(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        eatery_create_voucher(eatery_header, voucher_create_payload)

    def test_fail_voucher_creation_0_quantity(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a voucher with 0 quantity
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id, 0).values()
        assert create_voucher(eatery_header, voucher_create_payload).status_code == 400

    def test_fail_voucher_creation_negative_quantity(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a voucher with negative quantity
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id, -100).values()
        assert create_voucher(eatery_header, voucher_create_payload).status_code == 400

    def test_voucher_claim(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer successfully claims the voucher
        customer_claim_voucher(customer_id, voucher_id, customer_header)

    def test_voucher_claim_twice(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create customer1
        _, customer1_access_token, customer1_id = register_customer(register_data["customer"]["1"]).values()
        customer1_header = {"Authorization": "bearer " + customer1_access_token}

        # Create customer2
        _, customer2_access_token, customer2_id = register_customer(register_data["customer"]["2"]).values()
        customer2_header = {"Authorization": "bearer " + customer2_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer1 claims the voucher
        voucher_instance_id_1 = customer_claim_voucher(customer1_id, voucher_id, customer1_header)

        # Customer2 claims the second voucher as there should be 1 more voucher that can be claimed from a total of 2
        voucher_instance_id_2 = customer_claim_voucher(customer2_id, voucher_id, customer2_header)

        assert voucher_instance_id_1 != voucher_instance_id_2

    def test_voucher_claim_then_no_more_so_fail(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create customer1
        _, customer1_access_token, customer1_id = register_customer(register_data["customer"]["1"]).values()
        customer1_header = {"Authorization": "bearer " + customer1_access_token}

        # Create customer2
        _, customer2_access_token, customer2_id = register_customer(register_data["customer"]["2"]).values()
        customer2_header = {"Authorization": "bearer " + customer2_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id, 1).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer1 claims the voucher
        customer_claim_voucher(customer1_id, voucher_id, customer1_header)

        # Customer2 tries to claim the voucher, expect failure (400) as the voucher has been exhausted
        voucher_claim_payload = {"customer_id": customer2_id}
        assert claim_voucher(voucher_id, customer2_header, voucher_claim_payload).status_code == 400

    def test_voucher_claim_by_same_user_twice(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer tries to claim the same voucher again, expect failure (400) as a customer can redeem a voucher once
        voucher_claim_payload = {"customer_id": customer_id}
        assert claim_voucher(voucher_id, customer_header, voucher_claim_payload).status_code == 400

    def test_voucher_redeemed_and_accepted_then_user_tries_to_generate_code(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create a voucher
        release, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery gets redemption code details
        code_details_response = get_redemption_code_details(redemption_code, eatery_header)
        assert code_details_response.status_code == 200
        assert code_details_response.json()["eatery_id"] == eatery_id
        assert code_details_response.json()["name"] == voucher_data["1"]["name"]
        assert code_details_response.json()["description"] == voucher_data["1"]["description"]
        assert code_details_response.json()["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(code_details_response.json()["expiry"], release + timedelta(days=30))

        # Eatery accepts customer's redemption code
        assert accept_redemption_code(redemption_code, eatery_header).status_code == 200

        # Customer attempts to get a new code, expect failure (400) as the voucher has been used once by the customer
        assert redeem_voucher_instance(voucher_instance_id, customer_header).status_code == 400

    def test_voucher_flow_reject_then_accept(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create a voucher
        release, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery gets redemption code details
        code_details_response = get_redemption_code_details(redemption_code, eatery_header)
        assert code_details_response.status_code == 200
        assert code_details_response.json()["eatery_id"] == eatery_id
        assert code_details_response.json()["name"] == voucher_data["1"]["name"]
        assert code_details_response.json()["description"] == voucher_data["1"]["description"]
        assert code_details_response.json()["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(code_details_response.json()["expiry"], release + timedelta(days=30))

        # Eatery rejects customer's redemption code
        assert reject_redemption_code(redemption_code, eatery_header).status_code == 200

        # Eatery accepts customer's redemption code
        assert accept_redemption_code(redemption_code, eatery_header).status_code == 200

class TestRedeemVoucherInstance:
    def test_redeem_voucher_instance(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        customer_redeem_voucher_instance(voucher_instance_id, customer_header)

    def test_user_not_claimed_yet_tries_redeem(self, reset_db):
        # # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, _ = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer tries to claim a non-existent voucher instance, expect failure (403) as they do not have access
        assert redeem_voucher_instance(123456, customer_header).status_code == 403

    def test_user_claims_voucher_then_another_user_tries_to_redeem(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create customer1
        _, customer1_access_token, customer1_id = register_customer(register_data["customer"]["1"]).values()
        customer1_header = {"Authorization": "bearer " + customer1_access_token}

        # Create customer2
        _, customer2_access_token, _ = register_customer(register_data["customer"]["2"]).values()
        customer2_header = {"Authorization": "bearer " + customer2_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer1_id, voucher_id, customer1_header)

        # Customer2 tries to redeem the voucher instance, expect failure (403) as they do not have access
        assert redeem_voucher_instance(voucher_instance_id, customer2_header).status_code == 403

    def test_user_redeems_same_voucher_instance_twice(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create a voucher
        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance first time
        redemption_code_1 = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Customer redeems the voucher instance second time
        redemption_code_2 = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Check we can call redeem multiple times, getting the same code as before
        assert redemption_code_1 == redemption_code_2

class TestVoucherRedemptionWithCode:
    def test_redeem_voucher_code(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create a voucher
        release, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery gets redemption code details
        code_details_response = get_redemption_code_details(redemption_code, eatery_header)
        assert code_details_response.status_code == 200
        assert code_details_response.json()["eatery_id"] == eatery_id
        assert code_details_response.json()["name"] == voucher_data["1"]["name"]
        assert code_details_response.json()["description"] == voucher_data["1"]["description"]
        assert code_details_response.json()["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(code_details_response.json()["expiry"], release + timedelta(days=30))

    def test_redeem_voucher_code_but_uses_customers_token(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Customer tries to  get redemption code details, expect failure (401) because they don't have the correct permissions
        assert get_redemption_code_details(redemption_code, customer_header).status_code == 401

    def test_redeem_voucher_code_but_code_does_not_exist(self, reset_db):
        # Create an eatery
        _, eatery_access_token, _ = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Eatery tries to get the details of a non-existent voucher, expect failure (403)
        assert get_redemption_code_details(123456, eatery_header).status_code == 403

    def test_redeem_voucher_code_calling_twice(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        release, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery gets redemption code details
        code_details_response1 = get_redemption_code_details(redemption_code, eatery_header)
        assert code_details_response1.status_code == 200
        assert code_details_response1.json()["eatery_id"] == eatery_id
        assert code_details_response1.json()["name"] == voucher_data["1"]["name"]
        assert code_details_response1.json()["description"] == voucher_data["1"]["description"]
        assert code_details_response1.json()["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(code_details_response1.json()["expiry"], release + timedelta(days=30))

        # Eatery gets redemption code details again
        code_details_response2 = get_redemption_code_details(redemption_code, eatery_header)
        assert code_details_response2.status_code == 200
        assert code_details_response2.json()["eatery_id"] == eatery_id
        assert code_details_response2.json()["name"] == voucher_data["1"]["name"]
        assert code_details_response2.json()["description"] == voucher_data["1"]["description"]
        assert code_details_response2.json()["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(code_details_response2.json()["expiry"], release + timedelta(days=30))

    def test_redeem_voucher_called_by_eatery_not_owning_voucher(self, reset_db):
        # Create eatery1
        _, eatery1_access_token, eatery1_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery1_header = {"Authorization": "bearer " + eatery1_access_token}

        # Create eatery2
        _, eatery2_access_token, _ = register_eatery(register_data["eatery"]["2"]).values()
        eatery2_header = {"Authorization": "bearer " + eatery2_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        _, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery1_id).values()
        voucher_id = eatery_create_voucher(eatery1_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery2 tries to get the redemption code details, expect failure (403) as this eatery does not own the voucher
        assert get_redemption_code_details(redemption_code, eatery2_header).status_code == 403

class TestVoucherRedemptionAccept:
    def test_voucher_redemption_accept(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        release, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery gets redemption code details
        code_details_response = get_redemption_code_details(redemption_code, eatery_header)
        assert code_details_response.status_code == 200
        assert code_details_response.json()["eatery_id"] == eatery_id
        assert code_details_response.json()["name"] == voucher_data["1"]["name"]
        assert code_details_response.json()["description"] == voucher_data["1"]["description"]
        assert code_details_response.json()["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(code_details_response.json()["expiry"], release + timedelta(days=30))

        # Eatery accepts customer's redemption code
        assert accept_redemption_code(redemption_code, eatery_header).status_code == 200

    def test_voucher_redemption_accept_twice(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        release, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer redeems the voucher instance
        redemption_code = customer_redeem_voucher_instance(voucher_instance_id, customer_header)

        # Eatery gets redemption code details
        code_details_response = get_redemption_code_details(redemption_code, eatery_header)
        assert code_details_response.status_code == 200
        assert code_details_response.json()["eatery_id"] == eatery_id
        assert code_details_response.json()["name"] == voucher_data["1"]["name"]
        assert code_details_response.json()["description"] == voucher_data["1"]["description"]
        assert code_details_response.json()["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(code_details_response.json()["expiry"], release + timedelta(days=30))

        # Eatery accepts customer's redemption code
        assert accept_redemption_code(redemption_code, eatery_header).status_code == 200

        # Customer tries to reuse the redemption code, expect failure (403) as the redemption code can only be used once
        assert accept_redemption_code(redemption_code, eatery_header).status_code == 400

class TestVoucherFlowWithCustomerRoutes:
    def test_customer_claims_voucher_then_sees_it_in_their_vouchers(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        release, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Customer claims the voucher
        voucher_instance_id = customer_claim_voucher(customer_id, voucher_id, customer_header)

        # Customer lists and checks their claimed vouchers
        customer_vouchers = view_customer_vouchers(customer_id, customer_header)
        assert customer_vouchers.status_code == 200
        assert len(customer_vouchers.json()["vouchers"]) == 1

        # Checking the voucher
        voucher = customer_vouchers.json()["vouchers"][0]
        assert voucher["voucher_instance_id"] == voucher_instance_id
        assert voucher["voucher_id"] == voucher_id
        assert voucher["eatery_id"] == eatery_id
        assert voucher["name"] == voucher_data["1"]["name"]
        assert voucher["description"] == voucher_data["1"]["description"]
        assert voucher["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(voucher["expiry"], release + timedelta(days=30))

    def test_customer_claims_2_voucher_then_sees_it_in_their_vouchers(self, reset_db):
        # Create an eatery
        _, eatery_access_token, eatery_id = register_eatery(register_data["eatery"]["1"]).values()
        eatery_header = {"Authorization": "bearer " + eatery_access_token}

        # Create a customer
        _, customer_access_token, customer_id = register_customer(register_data["customer"]["1"]).values()
        customer_header = {"Authorization": "bearer " + customer_access_token}

        # Create voucher1
        release1, voucher_create_payload = create_voucher_payload(voucher_data["1"], eatery_id).values()
        voucher1_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Create voucher2
        release2, voucher_create_payload = create_voucher_payload(voucher_data["2"], eatery_id).values()
        voucher2_id = eatery_create_voucher(eatery_header, voucher_create_payload)

        # Checking vouchers have different IDs
        assert voucher1_id != voucher2_id

        # Customer claims voucher1
        voucher1_instance_id = customer_claim_voucher(customer_id, voucher1_id, customer_header)

        # Customer claims voucher2
        voucher2_instance_id = customer_claim_voucher(customer_id, voucher2_id, customer_header)

        assert voucher1_instance_id != voucher2_instance_id

        # Customer lists and checks their claimed vouchers
        customer_vouchers = view_customer_vouchers(customer_id, customer_header)
        assert customer_vouchers.status_code == 200
        assert len(customer_vouchers.json()["vouchers"]) == 2

        # Checking voucher 1
        voucher1 = customer_vouchers.json()["vouchers"][0]
        assert voucher1["voucher_instance_id"] == voucher1_instance_id
        assert voucher1["voucher_id"] == voucher1_id
        assert voucher1["eatery_id"] == eatery_id
        assert voucher1["name"] == voucher_data["1"]["name"]
        assert voucher1["description"] == voucher_data["1"]["description"]
        assert voucher1["conditions"] == voucher_data["1"]["conditions"]
        compare_expiry_in_response(voucher1["expiry"], release1 + timedelta(days=30))

        # Checking voucher 2
        voucher2 = customer_vouchers.json()["vouchers"][1]
        assert voucher2["voucher_instance_id"] == voucher2_instance_id
        assert voucher2["voucher_id"] == voucher2_id
        assert voucher2["eatery_id"] == eatery_id
        assert voucher2["name"] == voucher_data["2"]["name"]
        assert voucher2["description"] == voucher_data["2"]["description"]
        assert voucher2["conditions"] == voucher_data["2"]["conditions"]
        compare_expiry_in_response(voucher2["expiry"], release2 + timedelta(days=30))
