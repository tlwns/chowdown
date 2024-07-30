import json

from testing.test_helpers import login_customer, logout_user, register_customer, update_customer_profile, view_customer_profile
from functionality.customer import get_customer_profile
from router.api_types.api_response import AddressResponse, CustomerDetailsResponse

# Load data from JSON file
with open("testing/test_data.json", encoding="utf8") as file:
    test_data = json.load(file)

# Fetching test_data
register_data = test_data["register_data"]
login_data = test_data["login_data"]
voucher_data = test_data["voucher_data"]

class TestCustomerListFlow:
    def test_get_customer_profiles(self, reset_db):

        #test route for getting customer profiles
        cust1 = register_data["customer"]["1"]
        _, access_token1, cid1 = register_customer(cust1).values()
        header = {"Authorization": "bearer " + access_token1}        
        cust_prof = view_customer_profile(cid1, header).json()
        addr = {"unit_number": cust1["address"]["unit_number"], "formatted_str": cust1["address"]["fmt_address"]}
        exp_prof = {
            "email": cust1["email"],
            "first_name": cust1["first_name"],
            "last_name": cust1["last_name"],            
            "phone_number": cust1["phone_number"],
            "address": addr}
        cust2 = register_data["customer"]["2"]

        #test regular functionality for customer profiles
        _, _, cid2 = register_customer(cust2).values()
        cust2_prof = get_customer_profile(cid2)
        addr = AddressResponse(unit_number=cust2["address"]["unit_number"], formatted_str=cust2["address"]["fmt_address"])
        exp2_prof = CustomerDetailsResponse(
            email=cust2["email"],
            first_name=cust2["first_name"],
            last_name=cust2["last_name"],            
            phone_number=cust2["phone_number"],
            address=addr)
        assert cust_prof == exp_prof
        assert cust2_prof == exp2_prof

    def test_update_customer_details(self, reset_db):
        cust1 = register_data["customer"]["1"]
        cust2 = register_data["customer"]["2"]

        _, access_token1, cid1 = register_customer(cust1).values()
        payload = {
            "first_name": cust2["first_name"],
            "last_name": cust2["last_name"],
            "email": cust2["email"],
            "phone_number": cust2["phone_number"],
            "address": cust2["address"],
            "password": "new_password1234ASDF"
        }

        header = {"Authorization": "bearer " + access_token1}
        update_customer_profile(cid1, header, payload)

        cust_prof = get_customer_profile(cid1)
        addr = AddressResponse(unit_number=cust2["address"]["unit_number"], formatted_str=cust2["address"]["fmt_address"])
        exp2_prof = CustomerDetailsResponse(
            email=cust2["email"],
            first_name=cust2["first_name"],
            last_name=cust2["last_name"],            
            phone_number=cust2["phone_number"],
            address=addr)
        assert cust_prof == exp2_prof
        assert logout_user(header).status_code == 200
        #Try logging in with new password
        payload = {
            "email": cust2["email"],
            "password": "new_password1234ASDF"
        }
        login_customer(payload)

