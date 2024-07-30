from typing import List, Optional
from datetime import datetime
from psycopg2 import Error

from logger import log_red, log_green

from db.helpers import connect, disconnect
from db.db_types.db_request import EateryCreationRequest, AddressCreationRequest
from db.db_types.db_response import EateryDetailsResponse
from db.helpers.address import insert_address, get_address_by_id

def insert_eatery(eatery: EateryCreationRequest) -> Optional[int]:
    """
    Inserts an eatery into DB
    """
    address_id = insert_address(eatery.address)

    if address_id is None:
        return None

    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO eateries (eatery_name) VALUES (%(name)s) RETURNING id;",
                {"name": eatery.business_name})
            eatery_id = cur.fetchone()

            if eatery_id:
                eatery_id = eatery_id[0]
            else:
                return None

            cur.execute(
                """
                INSERT INTO eatery_details (email, phone_number, manager, abn, date_joined, address, eatery)
                VALUES (%(email)s, %(phone)s, ROW(%(last)s, %(first)s), %(abn)s, %(date_join)s, %(address)s, %(id)s);
            """, {
                    "email": eatery.email,
                    "phone": eatery.phone,
                    "first": eatery.manager_first_name,
                    "last": eatery.manager_last_name,
                    "abn": eatery.abn,
                    "date_join": eatery.date_joined,
                    "address": address_id,
                    "id": eatery_id,
                })

        conn.commit()

        update_eatery_password(eatery_id, eatery.password, eatery.date_joined)

        if eatery.description:
            update_eatery_description(eatery_id, eatery.description)

        log_green("Finished inserting the Eatery in Database")
    except Error as e:
        log_red(f"Error inserting Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return eatery_id

def add_eatery_keywords(eatery_id: int, keywords: List[str]):
    """
    Add a keyword to an eatery
    """
    for keyword in keywords:
        keyword = keyword.lower()
        try:
            conn = connect()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM keywords WHERE title = %(keyword)s;",
                    {"keyword": keyword})
                keyword_id = cur.fetchone()

                if keyword_id is None:
                    cur.execute(
                        "INSERT INTO keywords (title) VALUES (%(title)s) RETURNING id;",
                        {"title": keyword})
                    keyword_id = cur.fetchone()

                if keyword_id:
                    keyword_id = keyword_id[0]

                cur.execute(
                    "INSERT INTO eatery_atoms (keyword, eatery) VALUES (%(keyword)s, %(eatery)s);",
                    {
                        "keyword": keyword_id,
                        "eatery": eatery_id
                    })
            conn.commit()

            log_green(f"Finished inserting keyword \"{keyword}\" for the Eatery in Database")
        except Error as e:
            log_red(f"Error inserting keyword \"{keyword}\" for the Eatery: {e}")
            conn.rollback()
            raise e
        finally:
            disconnect(conn)

def get_all_eateries() -> Optional[List[int]]:
    """
    Fetches all eateries
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM eateries;")
            all_eateries = cur.fetchall()

        log_green("Finished getting all Eateries in Database")
    except Error as e:
        log_red(f"Error getting all Eateries: {e}")
        raise e
    finally:
        disconnect(conn)

    return [eatery[0] for eatery in all_eateries]

def get_eatery_by_id(eatery_id: int) -> Optional[EateryDetailsResponse]:
    """
    Fetches eatery's private details from DB given eatery ID
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT eatery_name FROM eateries WHERE id = %(id)s;",
                        {"id": eatery_id})
            name = cur.fetchone()

            if name is None:
                return None

            cur.execute(
                "SELECT email, phone_number, abn, manager, date_joined, address, description, thumbnail, menu FROM eatery_details WHERE eatery = %(id)s;",
                {"id": eatery_id})
            res = cur.fetchone()

            if res is None:
                return None

            email, phone, abn, manager_name, date_joined, address_id, description, thumbnail, menu = res
            manager_name = manager_name.strip("()")

        log_green("Finished getting information for the specified Eatery in Database")
    except Error as e:
        log_red(f"Error displaying Eatery\'s information: {e}")
        raise e
    finally:
        disconnect(conn)

    address = get_address_by_id(address_id)
    if address is None:
        return None

    return EateryDetailsResponse(
        business_name=name[0],
        email=email,
        phone=phone,
        manager_first_name=manager_name.split(",")[1],
        manager_last_name=manager_name.split(",")[0],
        abn=abn,
        date_joined=date_joined,
        address=address,
        description=description if description else "",
        thumbnail=thumbnail,
        menu=menu
    )

def get_eatery_keywords_by_id(eatery_id: int) -> Optional[List[str]]:
    """
    Gets all keywords for an eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT k.title FROM keywords k JOIN eatery_atoms ea ON k.id = ea.keyword WHERE ea.eatery = %(id)s;",
                {"id": eatery_id})
            keywords_raw = cur.fetchall()

        log_green("Finished getting keywords for the Eatery in Database")
    except Error as e:
        log_red(f"Error getting keywords for the Eatery: {e}")
        raise e
    finally:
        disconnect(conn)

    return [keyword[0] for keyword in keywords_raw]

def get_eatery_current_password_by_id(eatery_id: int) -> Optional[str]:
    """
    Gets the current password that the eatery has
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password FROM passwords WHERE eatery = %(id)s AND pass_type = 'current';",
                {"id": eatery_id})
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

def get_eatery_old_passwords_by_id(eatery_id: int) -> Optional[List[str]]:
    """
    Gets all the old passwords that the eatery has had from most recent to least recent
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password FROM passwords WHERE eatery = %(id)s AND pass_type = 'old' ORDER BY time_created DESC;",
                {"id": eatery_id})
            passwords_raw = cur.fetchall()

        log_green("Finished getting old passwords for the Customer in Database")
    except Error as e:
        log_red(f"Error getting old passwords for the Customer: {e}")
        raise e
    finally:
        disconnect(conn)

    return [password[0] for password in passwords_raw]

def get_eateries_by_name(eatery_name: str) -> Optional[List[int]]:
    """
    Fetches IDs all eateries that have name in their Name
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM eateries WHERE eatery_name = %(name)s;",
                {"name": eatery_name})
            relevant_eateries = cur.fetchall()

        log_green("Finished getting the Eateries in Database based on name")
    except Error as e:
        log_red(f"Error getting Eateries by name: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return [eatery[0] for eatery in relevant_eateries]

def get_eatery_by_email(email: str) -> Optional[int]:
    """
    Fetches ID of the eatery tied to an email (should be only one)
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eatery FROM eatery_details WHERE email = %(email)s;",
                {"email": email})
            relevant_eatery = cur.fetchone()

        log_green("Finished getting the Eatery in Database based on email")
    except Error as e:
        log_red(f"Error getting Eatery by email: {e}")
        raise e
    finally:
        disconnect(conn)

    if relevant_eatery:
        return relevant_eatery[0]

    return None

def get_eatery_by_phone_number(phone_number: str) -> Optional[int]:
    """
    Fetches ID of the eatery tied to a phone number (should be only one)
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eatery FROM eatery_details WHERE phone_number = %(phone)s;",
                {"phone": phone_number})
            relevant_eatery = cur.fetchone()

        log_green("Finished getting the Eatery in Database based on phone number")
    except Error as e:
        log_red(f"Error getting Eatery by phone number: {e}")
        raise e
    finally:
        disconnect(conn)

    if relevant_eatery:
        return relevant_eatery[0]

    return None

def get_eatery_by_abn(abn: int) -> Optional[int]:
    """
    Fetches eatery's private details from DB given eatery ID
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eatery FROM eatery_details WHERE abn = %(abn)s;",
                {'abn': abn})
            relevant_eatery = cur.fetchone()

        log_green("Finished getting information for the specified Eatery in Database")
    except Error as e:
        log_red(f"Error displaying Eatery's information: {e}")
        raise e
    finally:
        disconnect(conn)

    if relevant_eatery:
        return relevant_eatery[0]

    return None

def get_eateries_by_keyword(keyword: str) -> Optional[List[int]]:
    """
    Gets a list of eatery ID's that have that keyword
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ea.eatery FROM eatery_atoms ea JOIN keywords k ON ea.keyword = k.id WHERE k.title = %(name)s;",
                {"name": keyword})
            relevant_eateries = cur.fetchall()

        log_green(f"Finished getting Eateries in Database based on keyword \"{keyword}\"")
    except Error as e:
        log_red(f"Error getting Eateries based on keyword \"{keyword}\": {e}")
        raise e
    finally:
        disconnect(conn)

    return [eatery[0] for eatery in relevant_eateries]

def get_eatery_is_deleted_status(eatery_id: int) -> Optional[bool]:
    """
    Checks if Eatery is deleted
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT is_deleted FROM eateries WHERE id = %(id)s;",
                        {"id": eatery_id})
            is_deleted_status = cur.fetchone()

        log_green("Finished checking if the Eatery is deleted in Database")
    except Error as e:
        log_red(f"Error checking if the Eatery is deleted: {e}")
        raise e
    finally:
        disconnect(conn)

    if is_deleted_status:
        return is_deleted_status[0]

    return None

def delete_eatery_keywords(eatery_id: int, keywords: List[str]):
    """
    Delete keywords from an eatery
    """
    for keyword in keywords:
        try:
            conn = connect()
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM keywords WHERE title = %(keyword)s;",
                            {"keyword": keyword})
                keyword_id = cur.fetchone()

                if keyword_id:
                    cur.execute(
                        "DELETE FROM eatery_atoms WHERE eatery = %(eatery_id)s AND keyword = %(keyword_id)s;",
                        {
                            "eatery_id": eatery_id,
                            "keyword_id": keyword_id[0]
                        })
            conn.commit()

            log_green(f"Finished deleting keyword \"{keyword}\" from the Eatery from Database")
        except Error as e:
            log_red(f"Error deleting keyword \"{keyword}\" from Eatery: {e}")
            conn.rollback()
            raise e
        finally:
            disconnect(conn)

def delete_all_eatery_keywords(eatery_id: int):
    """
    Delete all keywords from an eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM eatery_atoms WHERE eatery = %(eatery_id)s;",
                {"eatery_id": eatery_id})
        conn.commit()

        log_green("Finished deleting all keywords from the Eatery from Database")
    except Error as e:
        log_red(f"Error deleting all keywords from Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_name(eatery_id: int, eatery_name: str):
    """
    Updates an eatery's name
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eateries SET eatery_name = %(name)s WHERE id = %(id)s;",
                {
                    "name": eatery_name,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished updating the name for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the name for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_email(eatery_id: int, email: str):
    """
    Updates a eatery's email
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eatery_details SET email = %(email)s WHERE eatery = %(id)s;",
                {
                    "email": email,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished updating the email for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the email for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_phone(eatery_id: int, phone_number: str):
    """
    Updates an eatery's phone
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eatery_details SET phone_number = %(phone)s WHERE eatery = %(id)s;",
                {
                    "phone": phone_number,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished updating the phone number for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the phone number for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_manager_name(eatery_id: int, first_name: str, last_name: str):
    """
    Updates an eatery's manager name
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eatery_details SET manager = ROW(%(last)s, %(first)s) WHERE eatery = %(id)s;",
                {
                    "last": last_name,
                    "first": first_name,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished updating the manager name for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the manager name for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_password(eatery_id: int, password: str, time_created: datetime):
    """
    Updates an eatery's password
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM passwords WHERE pass_type = 'current' AND eatery = %(id)s;",
                {
                    "password": password,
                    "id": eatery_id
                })
            pass_id = cur.fetchone()

            if pass_id is not None:
                cur.execute(
                    "UPDATE passwords SET pass_type = 'old' WHERE id = %(id)s;",
                    {"id": pass_id[0]})

            cur.execute(
                """
                INSERT INTO passwords (password, time_created, eatery, customer)
                VALUES (%(password)s, %(timez)s, %(eatery)s, NULL);
            """, {
                    "password": password,
                    "timez": time_created,
                    "eatery": eatery_id
                })
        conn.commit()

        log_green("Finished updating the password for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the password for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_is_deleted_status(eatery_id: int, is_deleted_status: bool):
    """
    Updates deleting the Eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eateries SET is_deleted = %(status)s WHERE id = %(id)s;", {
                    "status": is_deleted_status,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished deleting the Eatery in Database")
    except Error as e:
        log_red(f"Error deleting the Eatery: {e}")
    finally:
        disconnect(conn)

def update_eatery_description(eatery_id: int, description: str):
    """
    Updates an eatery's description
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eatery_details SET description = %(description)s WHERE eatery = %(id)s;",
                {
                    "description": description,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished updating the description for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the description for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_thumbnail(eatery_id: int, thumbnail: str):
    """
    Updates an eatery's thumbnail
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eatery_details SET thumbnail = %(thumbnail)s WHERE eatery = %(id)s;",
                {
                    "thumbnail": thumbnail,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished updating the thumbnail for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the thumbnail for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_menu(eatery_id: int, menu: str):
    """
    Updates an eatery's menu
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eatery_details SET menu = %(menu)s WHERE eatery = %(id)s;",
                {
                    "menu": menu,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished updating the menu for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the menu for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_eatery_address(eatery_id: int, address: AddressCreationRequest):
    """
    Updates an eatery's address
    """
    address_id = insert_address(address)

    if address_id is None:
        return

    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE eatery_details SET address = %(address)s WHERE eatery = %(id)s;",
                {
                    "address": address_id,
                    "id": eatery_id
                })
        conn.commit()

        log_green("Finished updating the address for the Eatery in Database")
    except Error as e:
        log_red(f"Error updating the address for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def get_all_blocked_customers(eatery_id: int) -> Optional[List[int]]:
    """
    Gets all blocked customers for an Eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eatery FROM blocked_customers WHERE eatery = %(id)s;",
                {
                    "id": eatery_id
                })
            customers_raw = cur.fetchall()

        log_green("Finished getting blocked customers for the Eatery in Database")
    except Error as e:
        log_red(f"Error getting blocked customers for the Eatery: {e}")
        raise e
    finally:
        disconnect(conn)

    return [customer[0] for customer in customers_raw]

def block_customer(eatery_id: int, customer_id: int):
    """
    Blocks a customer for the Eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO blocked_customers (eatery, customer) VALUES (%(eatery)s, %(customer)s);",
                {
                    "eatery": eatery_id,
                    "customer": customer_id
                })
        conn.commit()

        log_green(f"Finished blocking customer with id: \"{customer_id}\" for the Eatery in Database")
    except Error as e:
        log_red(f"Error blocking customer with id: \"{customer_id}\" for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def unblock_customer(eatery_id: int, customer_id: int):
    """
    Unblocks a customer for the Eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM blocked_customers WHERE eatery = %(eatery)s AND customer = %(customer)s;",
                {
                    "eatery": eatery_id,
                    "customer": customer_id
                })
        conn.commit()

        log_green(f"Finished unblocking customer with id: \"{customer_id}\" for the Eatery in Database")
    except Error as e:
        log_red(f"Error unblocking customer with id: \"{customer_id}\" for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def get_all_favourited_customers(eatery_id: int) -> Optional[List[int]]:
    """
    Gets all favourited customers for an Eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT customer FROM favourite_customers WHERE eatery = %(id)s;",
                {
                    "id": eatery_id
                })
            customers_raw = cur.fetchall()

        log_green("Finished getting favorited customers for the Eatery in Database")
    except Error as e:
        log_red(f"Error getting favorited customers for the Eatery: {e}")
        raise e
    finally:
        disconnect(conn)

    return [customer[0] for customer in customers_raw]

def favourite_customer(eatery_id: int, customer_id: int):
    """
    Favourites a customer for the Eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO favourite_customers (eatery, customer) VALUES (%(eatery)s, %(customer)s);",
                {
                    "eatery": eatery_id,
                    "customer": customer_id
                })
        conn.commit()

        log_green(f"Finished favoriting customer with id: \"{customer_id}\" for the Eatery in Database")
    except Error as e:
        log_red(f"Error favoriting customer with id: \"{customer_id}\" for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def unfavourite_customer(customer_id: int, eatery_id: int):
    """
    Unfavourites a customer for the Eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM favourite_customers WHERE eatery = %(eatery)s AND customer = %(customer)s;",
                {
                    "eatery": eatery_id,
                    "customer": customer_id
                })
        conn.commit()

        log_green(f"Finished unfavoriting customer with id: \"{customer_id}\" for the Eatery in Database")
    except Error as e:
        log_red(f"Error unfavoriting customer with id: \"{customer_id}\" for the Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)
