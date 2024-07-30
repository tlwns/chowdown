from typing import List, Optional
from datetime import datetime
from psycopg2 import Error

from logger import log_red, log_green

from db.helpers import connect, disconnect
from db.db_types.db_request import CustomerCreationRequest, AddressCreationRequest
from db.db_types.db_response import CustomerDetailsResponse
from db.helpers.address import insert_address, get_address_by_id

def insert_customer(customer: CustomerCreationRequest) -> Optional[int]:
    """
    Inserts a customer into DB
    """
    address_id = insert_address(customer.address)

    if address_id is None:
        return None

    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO customers (customer_name, email, phone_number, date_joined, address)
                VALUES (ROW(%(last)s, %(first)s), %(email)s, %(phone)s, %(date_join)s, %(address)s)
                RETURNING id;
            """, {
                    "last": customer.last_name,
                    "first": customer.first_name,
                    "email": customer.email,
                    "phone": customer.phone,
                    "date_join": customer.date_joined,
                    "address": address_id
                })
            customer_id = cur.fetchone()

            if customer_id:
                customer_id = customer_id[0]
            else:
                return None
        conn.commit()

        update_customer_password(customer_id, customer.password, customer.date_joined)

        log_green("Finished inserting the Customer in Database")
    except Error as e:
        log_red(f"Error inserting Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return customer_id

def add_customer_preferences(customer_id: int, preferences: List[str]):
    """
    Adds a preference to a customers preference list
    """
    for preference in preferences:
        try:
            conn = connect()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM preferences WHERE title = %(preference)s;",
                    {"preference": preference})
                preference_id = cur.fetchone()

                if preference_id is None:
                    cur.execute(
                        "INSERT INTO preferences (title) VALUES (%(title)s) RETURNING id;",
                        {"title": preference})
                    preference_id = cur.fetchone()

                if preference_id:
                    preference_id = preference_id[0]

                cur.execute(
                    "INSERT INTO customer_likes (preference, customer) VALUES (%(preference)s, %(customer)s);",
                    {
                        "preference": preference_id,
                        "customer": customer_id
                    })
            conn.commit()

            log_green(f"Finished inserting preference \"{preference}\" for the Customer in Database")
        except Error as e:
            log_red(f"Error inserting preference \"{preference}\" for the Customer: {e}")
            conn.rollback()
            raise e
        finally:
            disconnect(conn)

def get_all_customers() -> Optional[List[int]]:
    """
    Fetches all customers
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM customers;")
            all_customers = cur.fetchall()

        log_green("Finished getting all Customers in Database")
    except Error as e:
        log_red(f"Error getting all Customers: {e}")
        raise e
    finally:
        disconnect(conn)

    return [customer[0] for customer in all_customers]

def get_customer_by_id(customer_id: int) -> Optional[CustomerDetailsResponse]:
    """
    Gets all the details of the customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT customer_name, email, phone_number, date_joined, is_deleted, address FROM customers WHERE id = %(id)s;",
                {"id": customer_id})
            res = cur.fetchone()

            if res is None:
                return None

            name, email, phone, date_joined, is_deleted, address_id = res
            name = name.strip("()")

        log_green("Finished getting information for the specified Customer in Database")
    except Error as e:
        log_red(f"Error displaying Customer\'s information: {e}")
        raise e
    finally:
        disconnect(conn)

    address = get_address_by_id(address_id)
    if address is None:
        return None

    return CustomerDetailsResponse(
        first_name=name.split(",")[1],
        last_name=name.split(",")[0],
        email=email,
        phone=phone,
        address=address,
        date_joined=date_joined,
        is_deleted=is_deleted
    )

def get_customer_preferences_by_id(customer_id: int) -> Optional[List[str]]:
    """
    Gets all preferences that the customer has
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT p.title FROM preferences p JOIN customer_likes cl ON p.id = cl.preference WHERE cl.customer = %(id)s;",
                {"id": customer_id})
            preferences_raw = cur.fetchall()
        log_green("Finished getting preferences for the Customer in Database")
    except Error as e:
        log_red(f"Error getting preferences for the Customer: {e}")
        raise e
    finally:
        disconnect(conn)

    return [preference[0] for preference in preferences_raw]

def get_customer_current_password_by_id(customer_id: int) -> Optional[str]:
    """
    Gets the current password that the customer has
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password FROM passwords WHERE customer = %(id)s AND pass_type = 'current';",
                {"id": customer_id})
            password = cur.fetchone()

        log_green("Finished getting current password for the Customer in Database")
    except Error as e:
        log_red(f"Error getting current password for the Customer: {e}")
        raise e
    finally:
        disconnect(conn)

    if password:
        return password[0]

    return None

def get_customer_old_passwords_by_id(customer_id: int) -> Optional[List[str]]:
    """
    Gets all the old passwords that the customer has had from most recent to least recent
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password FROM passwords WHERE customer = %(id)s AND pass_type = 'old' ORDER BY time_created DESC;",
                {"id": customer_id})
            passwords_raw = cur.fetchall()

        log_green("Finished getting old passwords for the Customer in Database")
    except Error as e:
        log_red(f"Error getting old passwords for the Customer: {e}")
        raise e
    finally:
        disconnect(conn)

    return [password[0] for password in passwords_raw]

def get_customers_by_name(first_name: str, last_name: str) -> Optional[List[int]]:
    """
    Gets the customers that have that name
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM customers WHERE customer_name = ROW(%(last)s, %(first)s)::PERSON_NAME;",
                {
                    "last": last_name,
                    "first": first_name
                })
            relevant_customers = cur.fetchall()

        log_green("Finished getting the Customers in Database based on name")
    except Error as e:
        log_red(f"Error getting Customers by name: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return [customer[0] for customer in relevant_customers]

def get_customers_by_first_name(first_name: str) -> Optional[List[int]]:
    """
    Gets the customers that have that first name
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM customers WHERE customer_name.first_name = %(first)s;",
                {"first": first_name})
            relevant_customers = cur.fetchall()

        log_green("Finished getting the Customers in Database based on first name")
    except Error as e:
        log_red(f"Error getting Customers by first name: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return [customer[0] for customer in relevant_customers]

def get_customers_by_last_name(last_name: str) -> Optional[List[int]]:
    """
    Gets the customers that have that last name
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM customers WHERE customer_name.last_name = %(last)s;",
                {"last": last_name})
            relevant_customers = cur.fetchall()

        log_green("Finished getting the Customers in Database based on last name")
    except Error as e:
        log_red(f"Error getting Customers by last name: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return [customer[0] for customer in relevant_customers]

def get_customer_by_email(email: str) -> Optional[int]:
    """
    Gets the customer that has that email (should be only one)
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM customers WHERE email = %(email)s;",
                        {"email": email})
            relevant_customer = cur.fetchone()

        log_green("Finished getting the Customer in Database based on email")
    except Error as e:
        log_red(f"Error getting Customer by email: {e}")
        raise e
    finally:
        disconnect(conn)

    if relevant_customer:
        return relevant_customer[0]

    return None

def get_customer_by_phone_number(phone_number: str) -> Optional[int]:
    """
    Gets the customer that has that phone number (should be only one)
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM customers WHERE phone_number = %(phone)s;",
                {"phone": phone_number})
            relevant_customer = cur.fetchone()

        log_green("Finished getting the Customer in Database based on phone number")
    except Error as e:
        log_red(f"Error getting Customer by phone number: {e}")
        raise e
    finally:
        disconnect(conn)

    if relevant_customer:
        return relevant_customer[0]

    return None

def get_customers_by_preference(preference: str) -> Optional[List[int]]:
    """
    Gets all preferences that the customer has
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT cl.customer FROM customer_likes cl JOIN preferences p ON cl.preference = p.id WHERE p.title = %(name)s;",
                {"name": preference})
            relevant_eateries = cur.fetchall()

        log_green(f"Finished getting Customers in Database based on preference \"{preference}\"")
    except Error as e:
        log_red(f"Error getting Customers based on preference \"{preference}\": {e}")
        raise e
    finally:
        disconnect(conn)

    return [eatery[0] for eatery in relevant_eateries]

def get_customer_is_deleted_status(customer_id: int) -> Optional[bool]:
    """
    Checks if Customer is deleted
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT is_deleted FROM customers WHERE id = %(id)s;",
                        {"id": customer_id})
            is_deleted_status = cur.fetchone()

        log_green("Finished checking if the Customer is deleted in Database")
    except Error as e:
        log_red(f"Error checking if the Customer is deleted: {e}")
        raise e
    finally:
        disconnect(conn)

    if is_deleted_status:
        return is_deleted_status[0]

    return None

def delete_customer_preferences(customer_id: int, preferences: List[str]):
    """
    Deletes preferences from the customer's preference list
    """
    for preference in preferences:
        try:
            conn = connect()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM preferences WHERE title = %(preference)s;",
                    {"preference": preference})
                preference_id = cur.fetchone()

                if preference_id:
                    cur.execute(
                        "DELETE FROM customer_likes WHERE customer = %(customer_id)s AND preference = %(preference_id)s;",
                        {
                            "customer_id": customer_id,
                            "preference_id": preference_id[0]
                        })
            conn.commit()

            log_green(f"Finished deleting preference\"{preference}\" in the Customer from Database")
        except Error as e:
            log_red(f"Error deleting preference \"{preference}\" in Customer: {e}")
            conn.rollback()
            raise e
        finally:
            disconnect(conn)

def delete_all_customer_preferences(customer_id: int):
    """
    Delete all keywords from the customer's preference list
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM customer_likes WHERE customer = %(customer_id)s;",
                {"customer_id": customer_id})
        conn.commit()

        log_green("Finished deleting all keywords from the Customer from Database")
    except Error as e:
        log_red(f"Error deleting all keywords from Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_customer_name(customer_id: int, first_name: str, last_name: str):
    """
    Updates a customers name
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE customers SET customer_name = ROW(%(last)s, %(first)s) WHERE id = %(id)s;",
                {
                    "last": last_name,
                    "first": first_name,
                    "id": customer_id
                })
        conn.commit()

        log_green("Finished updating the name for the Customer in Database")
    except Error as e:
        log_red(f"Error updating the name for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_customer_email(customer_id: int, email: str):
    """
    Updates a customers email
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE customers SET email = %(email)s WHERE id = %(id)s;", {
                    "email": email,
                    "id": customer_id
                })
        conn.commit()

        log_green("Finished updating the email for the Customer in Database")
    except Error as e:
        log_red(f"Error updating the email for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_customer_phone(customer_id: int, phone_number: str):
    """
    Updates a customers phone number
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE customers SET phone_number = %(phone)s WHERE id = %(id)s;",
                {
                    "phone": phone_number,
                    "id": customer_id
                })
        conn.commit()

        log_green("Finished updating the phone number for the Customer in Database")
    except Error as e:
        log_red(f"Error updating the phone number for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_customer_password(customer_id: int, password: str, time_created: datetime):
    """
    Updates a customers password
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM passwords WHERE pass_type = 'current' AND customer = %(id)s;",
                {
                    "password": password,
                    "id": customer_id
                })
            pass_id = cur.fetchone()

            if pass_id is not None:
                cur.execute(
                    "UPDATE passwords SET pass_type = 'old' WHERE id = %(id)s;",
                    {"id": pass_id[0]})

            cur.execute(
                """
                INSERT INTO passwords (password, time_created, eatery, customer)
                VALUES (%(password)s, %(timez)s, NULL, %(customer)s);
            """, {
                    "password": password,
                    "timez": time_created,
                    "customer": customer_id
                })
        conn.commit()

        log_green("Finished updating the password for the Customer in Database")
    except Error as e:
        log_red(f"Error updating the password for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_customer_is_deleted_status(customer_id: int, is_deleted_status: bool):
    """
    Updates deleting the Customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE customers SET is_deleted = %(status)s WHERE id = %(id)s;",
                {
                    "status": is_deleted_status,
                    "id": customer_id
                })
        conn.commit()

        log_green("Finished deleting the Customer in Database")
    except Error as e:
        log_red(f"Error deleting the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_customer_address(customer_id: int, address: AddressCreationRequest):
    """
    Updates an customer's address
    """
    address_id = insert_address(address)

    if address_id is None:
        return

    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE customers SET address = %(address)s WHERE id = %(id)s;",
                {
                    "address": address_id,
                    "id": customer_id
                })
        conn.commit()

        log_green("Finished updating the address for the Customer in Database")
    except Error as e:
        log_red(f"Error updating the address for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def get_all_blocked_eateries(customer_id: int) -> Optional[List[int]]:
    """
    Gets all blocked eateries for a Customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eatery FROM blocked_eateries WHERE customer = %(id)s;",
                {
                    "id": customer_id
                })
            eateries_raw = cur.fetchall()

        log_green("Finished getting blocked eateries for the Customer in Database")
    except Error as e:
        log_red(f"Error getting blocked eateries for the Customer: {e}")
        raise e
    finally:
        disconnect(conn)

    return [eatery[0] for eatery in eateries_raw]

def block_eatery(customer_id: int, eatery_id: int):
    """
    Blocks an eatery for the Customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO blocked_eateries (eatery, customer) VALUES (%(eatery)s, %(customer)s);",
                {
                    "customer": customer_id,
                    "eatery": eatery_id
                })
        conn.commit()

        log_green(f"Finished blocking eatery with id: \"{eatery_id}\" for the Customer in Database")
    except Error as e:
        log_red(f"Error blocking eatery with id: \"{eatery_id}\" for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def unblock_eatery(customer_id: int, eatery_id: int):
    """
    Unblocks an eatery for the Customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM blocked_eateries WHERE customer = %(customer)s AND eatery = %(eatery)s;",
                {
                    "customer": customer_id,
                    "eatery": eatery_id
                })
        conn.commit()

        log_green(f"Finished unblocking eatery with id: \"{eatery_id}\" for the Customer in Database")
    except Error as e:
        log_red(f"Error unblocking eatery with id: \"{eatery_id}\" for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def get_all_favourited_eateries(customer_id: int) -> Optional[List[int]]:
    """
    Gets all favourited eateries for a Customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eatery FROM favourite_eateries WHERE customer = %(id)s;",
                {
                    "id": customer_id
                })
            eateries_raw = cur.fetchall()

        log_green("Finished getting favorited eateries for the Customer in Database")
    except Error as e:
        log_red(f"Error getting favorited eateries for the Customer: {e}")
        raise e
    finally:
        disconnect(conn)

    return [eatery[0] for eatery in eateries_raw]

def favourite_eatery(customer_id: int, eatery_id: int):
    """
    Favourites an eatery for the Customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO favourite_eateries (eatery, customer) VALUES (%(eatery)s, %(customer)s);",
                {
                    "customer": customer_id,
                    "eatery": eatery_id
                })
        conn.commit()

        log_green(f"Finished favoriting eatery with id: \"{eatery_id}\" for the Customer in Database")
    except Error as e:
        log_red(f"Error favoriting eatery with id: \"{eatery_id}\" for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def unfavourite_eatery(customer_id: int, eatery_id: int):
    """
    Unfavourites an eatery for the Customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM favourite_eateries WHERE customer = %(customer)s AND eatery = %(eatery)s;",
                {
                    "customer": customer_id,
                    "eatery": eatery_id
                })
        conn.commit()

        log_green(f"Finished unfavoriting eatery with id: \"{eatery_id}\" for the Customer in Database")
    except Error as e:
        log_red(f"Error unfavoriting eatery with id: \"{eatery_id}\" for the Customer: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)
