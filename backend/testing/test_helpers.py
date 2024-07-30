from testing import client

def check_cookies(response, user_type):
    """
    Checks that the response receives both refresh_token and access token in cookies
    """
    # Check that we get refresh_token in cookie
    cookie = response.cookies.get("refresh_token")
    assert cookie is not None, "missing: refresh token (from cookies)"

    # Check that we get the access token, user id and user type
    assert "access_token" in response.json(), "missing: access token"
    assert "user_id" in response.json(), "missing: user id"
    assert "user_type" in response.json(), "missing: user type"

    assert response.json()["user_type"] == user_type

    return {
        "cookie": cookie,
        "access_token": response.json().get("access_token"),
        "user_id": response.json().get("user_id")
    }

def register_customer(payload):
    response = client.post("/auth/register/customer", json=payload)
    assert response.status_code == 200

    return check_cookies(response, "customer")

def register_eatery(payload):
    response = client.post("/auth/register/eatery", json=payload)
    assert response.status_code == 200

    return check_cookies(response, "eatery")

def login_customer(payload):
    response = client.post("/auth/login/customer", json=payload)
    assert response.status_code == 200

    return check_cookies(response, "customer")

def login_eatery(payload):
    response = client.post("/auth/login/eatery", json=payload)
    assert response.status_code == 200

    return check_cookies(response, "eatery")

def logout_user(header):
    return client.delete("/auth/logout", headers=header)

def refresh_token(header):
    return client.get("/auth/refresh", headers=header)

def list_eateries():
    return client.get("/eatery/list").json().get("eateries")

def view_eatery_private_details(eatery_id, header):
    return client.get("/eatery/" + str(eatery_id) + "/details", headers=header)

def update_eatery_details(eatery_id, header, payload):
    return client.put("/eatery/" + str(eatery_id) + "/details", headers=header, json=payload)

def update_eatery_thumbnail(eatery_id, header, payload):
    return client.put("/eatery/" + str(eatery_id) + "/thumbnail", headers=header, json=payload)

def update_eatery_menu(eatery_id, header, payload):
    return client.put("/eatery/" + str(eatery_id) + "/menu", headers=header, json=payload)

def view_eatery_public_details(eatery_id):
    return client.get("/eatery/" + str(eatery_id) + "/details/public")

def view_eatery_vouchers(eatery_id):
    return client.get("/eatery/" + str(eatery_id) + "/vouchers").json().get("vouchers")

def view_eatery_reviews(eatery_id):
    return client.get("/eatery/" + str(eatery_id) + "/reviews").json().get("reviews")

def create_review(eatery_id, header, payload):
    return client.post("/eatery/" + str(eatery_id) + "/reviews", headers=header, json=payload)

def create_voucher(header, payload):
    return client.post("/voucher", headers=header, json=payload)

def view_voucher(voucher_id):
    return client.get("/voucher/" + str(voucher_id))

def claim_voucher(voucher_id, header, payload):
    return client.put("/voucher/claim/" + str(voucher_id), headers=header, json=payload)

def redeem_voucher_instance(voucher_instance_id, header):
    return client.put("/voucher/instance/" + str(voucher_instance_id) + "/redeem", headers=header)

def get_redemption_code_details(redemption_code, header):
    return client.get("/voucher/redemption/" + str(redemption_code), headers=header)

def accept_redemption_code(redemption_code, header):
    return client.put("/voucher/redemption/" + str(redemption_code) + "/accept", headers=header)

def reject_redemption_code(redemption_code, header):
    return client.put("/voucher/redemption/" + str(redemption_code) + "/reject", headers=header)

def view_customer_profile(customer_id, header):
    return client.get("/customer/" + str(customer_id) + "/profile", headers=header)

def update_customer_profile(customer_id, header, payload):
    return client.put("/customer/" + str(customer_id) + "/profile", headers=header, json=payload)

def view_customer_vouchers(customer_id, header):
    return client.get("/customer/" + str(customer_id) + "/vouchers", headers=header)

def search(query):
    return client.get("/eatery/search", params={"search_query": query})
