import json
import pytest
import copy

from testing import client
from testing.test_helpers import register_customer, register_eatery, login_customer, logout_user, refresh_token, view_eatery_private_details
# Load data from JSON file
with open("testing/test_data.json", encoding="utf8") as file:
    test_data = json.load(file)

# Fetching test_data
register_data = test_data["register_data"]
login_data = test_data["login_data"]

INVALID_EMAILS = [
    "email.example.com",
    "e@mail@example.com",
    "john*doe@example.com",
    "jane(doe)@example.com",
    "john.doe@example!com",
    "email@"
    "@example.com",
    "email@example.com!",
    "a'b(c)d,e:f;g<h>i[j\\k]l@example.com",
    "ema'l'@example.com",
    "e mail@example.com",
    ""
]
INVALID_PHONE_NUMBERS = ["abc"] # "0123", "01231231"
INVALID_ABNS = ["12345678965", "65065987968", ]
INVALID_PASSWORDS = [
    "ilovecomputerscience",
    "1234567890",
    "i love computer science",
    "I love computer science",
    "I love computer science @",
    "!@#$%^&*()"
    "",
    "1a",
    "123abcd"
]
INVALID_ADDRESS_FIELDS = [
    {
        "country": "",
    },
    {
        "state": "",
    },
    {
        "city": "",
    },
    {
        "longitude": 181.270550,
    },
    {
        "longitude": -181.270550,
    },
    {
        "latitude": 91.756730,
    },
    {
        "latitude": -91.756730,
    },
]

class TestAuthenticationFlow:
    def test_successful_customer_register_then_logout(self, reset_db):
        # Authenticate Customer
        _, access_token, _ = register_customer(register_data["customer"]["1"]).values()

        # Logout Customer
        header = {"Authorization": "bearer " + access_token}
        assert logout_user(header).status_code == 200

    def test_successful_eatery_register_then_logout(self, reset_db):
        # Authenticate Eatery
        _, access_token, _ = register_eatery(register_data["eatery"]["1"]).values()

        # Logout Eatery
        header = {"Authorization": "bearer " + access_token}
        assert logout_user(header).status_code == 200

    def test_successful_customer_register_then_logout_then_fail_refresh(self, reset_db):
        # Authenticate user
        cookie, access_token, _ = register_customer(register_data["customer"]["1"]).values()

        # Logout user
        header = {"Authorization": "bearer " + access_token}
        assert logout_user(header).status_code == 200

        # Try to refresh the token and expect failure
        client.cookies = {"refresh_token": cookie}
        assert refresh_token(header).status_code == 401

    def test_user_register_then_logout_then_login(self, reset_db):
        # Authenticate user
        register_cookie, register_access_token, _ = register_customer(register_data["customer"]["1"]).values()

        # Logout user
        header = {"Authorization": "bearer " + register_access_token}
        assert logout_user(header).status_code == 200

        # Login user
        login_cookie, login_access_token, _ = login_customer(login_data["customer"]["1"]).values()

        # Logout user
        header = {"Authorization": "bearer " + login_access_token}
        assert logout_user(header).status_code == 200

        # Compare refresh and access tokens
        assert register_cookie != login_cookie
        assert register_access_token != login_access_token

    def test_user_double_logout(self, reset_db):
        # Authenticate user
        _, access_token, _ = register_customer(register_data["customer"]["1"]).values()

        # Logout user
        header = {"Authorization": "bearer " + access_token}
        assert logout_user(header).status_code == 200

        # Try to logout the user again and expect failure
        assert logout_user(header).status_code == 401

class TestAuthorizationScope:
    def test_customer_can_only_view_customer_details(self, reset_db):
        # Authenticate Customer
        _, customer_access_token, _ = register_customer(register_data["customer"]["1"]).values()

        # Authenticate Eatery
        *_, eatery_user_id = register_eatery(register_data["eatery"]["1"]).values()

        # Try to get eatery's full details using customer token and expect failure
        customer_header = {"Authorization": "bearer " + customer_access_token}
        assert view_eatery_private_details(eatery_user_id, customer_header).status_code == 401

    def test_eatery_can_only_view_eatery_details(self, reset_db):
        # Authenticate Customer
        *_, customer_user_id = register_customer(register_data["customer"]["1"]).values()

        # Authenticate Eatery
        _, eatery_access_token, _ = register_eatery(register_data["eatery"]["1"]).values()

        # Try to get customer's full details using eatery token and expect failure
        eatery_header = {"Authorization": "bearer " + eatery_access_token}
        assert view_eatery_private_details(customer_user_id, eatery_header).status_code == 401

class TestEateryRegistration:
    def test_successful_register(self, reset_db):
        # Register eatery
        register_eatery(register_data["eatery"]["1"])

    @pytest.mark.parametrize("email", INVALID_EMAILS)
    def test_invalid_email(self, email, reset_db):
        # Register eatery, expect failure (400) as the email is invalid
        eatery = register_data["eatery"]["1"].copy()
        eatery["email"] = email
        assert client.post("/auth/register/eatery", json=eatery).status_code == 400

    @pytest.mark.parametrize("phone_number", INVALID_PHONE_NUMBERS)
    def test_invalid_phone_number(self, phone_number, reset_db):
        # Register eatery, expect failure (400) as the phone number is invalid
        eatery = register_data["eatery"]["1"].copy()
        eatery["phone_number"] = phone_number
        assert client.post("/auth/register/eatery", json=eatery).status_code == 400

    @pytest.mark.parametrize("abn", INVALID_ABNS)
    def test_invalid_abn(self, abn, reset_db):
        # Register eatery, expect failure (400) as the abn is invalid
        eatery = register_data["eatery"]["1"].copy()
        eatery["abn"] = abn
        assert client.post("/auth/register/eatery", json=eatery).status_code == 400

    @pytest.mark.parametrize("password", INVALID_PASSWORDS)
    def test_invalid_password(self, password, reset_db):
        # Register eatery, expect failure (400) as the password is invalid
        eatery = register_data["eatery"]["1"].copy()
        eatery["password"] = password
        assert client.post("/auth/register/eatery", json=eatery).status_code == 400

    @pytest.mark.parametrize("address_field", INVALID_ADDRESS_FIELDS)
    def test_invalid_address(self, address_field, reset_db):
        # Register eatery, expect failure (400) as the address is invalid
        eatery = copy.deepcopy(register_data["eatery"]["1"])
        for key, value in address_field.items():
            eatery["address"][key] = value

        assert client.post("/auth/register/eatery", json=eatery).status_code == 400

    def test_duplicate_email(self, reset_db):
        # Register eatery
        register_eatery(register_data["eatery"]["1"])

        # Register eatery, expect failure (400) as the email is duplicate
        eatery = register_data["eatery"]["2"].copy()
        eatery["email"] = register_data["eatery"]["1"]["email"]
        assert client.post("/auth/register/eatery", json=eatery).status_code == 400

    def test_duplicate_phone_number(self, reset_db):
        # Register eatery
        register_eatery(register_data["eatery"]["1"])

        # Register eatery, expect failure (400) as the phone number is duplicate
        eatery = register_data["eatery"]["2"].copy()
        eatery["phone_number"] = register_data["eatery"]["1"]["phone_number"]
        assert client.post("/auth/register/eatery", json=eatery).status_code == 400

    def test_duplicate_abn(self, reset_db):
        # Register eatery
        register_eatery(register_data["eatery"]["1"])

        # Register eatery, expect failure (400) as the abn is duplicate
        eatery = register_data["eatery"]["2"].copy()
        eatery["abn"] = register_data["eatery"]["1"]["abn"]
        assert client.post("/auth/register/eatery", json=eatery).status_code == 400

class TestCustomerRegistration:
    def test_successful_register(self, reset_db):
        register_customer(register_data["customer"]["1"])

    @pytest.mark.parametrize("email", INVALID_EMAILS)
    def test_invalid_email(self, email, reset_db):
        # Register customer, expect failure (400) as the email is invalid
        customer = register_data["customer"]["1"].copy()
        customer["email"] = email
        assert client.post("/auth/register/customer", json=customer).status_code == 400

    @pytest.mark.parametrize("phone_number", INVALID_PHONE_NUMBERS)
    def test_invalid_phone_number(self, phone_number, reset_db):
        # Register customer, expect failure (400) as the phone number is invalid
        customer = register_data["customer"]["1"].copy()
        customer["phone_number"] = phone_number
        assert client.post("/auth/register/customer", json=customer).status_code == 400

    @pytest.mark.parametrize("password", INVALID_PASSWORDS)
    def test_invalid_password(self, password, reset_db):
        # Register customer, expect failure (400) as the password is invalid
        customer = register_data["customer"]["1"].copy()
        customer["password"] = password
        assert client.post("/auth/register/customer", json=customer).status_code == 400

    @pytest.mark.parametrize("address_field", INVALID_ADDRESS_FIELDS)
    def test_invalid_address(self, address_field, reset_db):
        # Register customer, expect failure (400) as the address is invalid
        customer = copy.deepcopy(register_data["customer"]["1"])
        for key, value in address_field.items():
            customer["address"][key] = value
        assert client.post("/auth/register/customer", json=customer).status_code == 400

    def test_duplicate_email(self, reset_db):
        # Register customer
        register_customer(register_data["customer"]["1"])

        # Register customer, expect failure (400) as the email is duplicate
        customer = register_data["customer"]["2"].copy()
        customer["email"] = register_data["customer"]["1"]["email"]
        assert client.post("/auth/register/customer", json=customer).status_code == 400

    def test_duplicate_phone_number(self, reset_db):
        # Register customer
        register_customer(register_data["customer"]["1"])

        # Register customer, expect failure (400) as the phone number is duplicate
        customer = register_data["customer"]["2"].copy()
        customer["phone_number"] = register_data["customer"]["1"]["phone_number"]
        assert client.post("/auth/register/customer", json=customer).status_code == 400
