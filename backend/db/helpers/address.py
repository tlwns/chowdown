from typing import Optional, List
from psycopg2 import Error

from logger import log_red, log_green

from db.helpers import connect, disconnect
from db.db_types.db_request import AddressCreationRequest
from db.db_types.db_response import AddressDetailsResponse

def insert_address(address: AddressCreationRequest) -> Optional[int]:
    """
    Inserts an address for an eatery or customer into DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO addresses (unit_number, house_number, street_addr, city, state, county, country, postcode, longitude, latitude, formatted_str)
                VALUES (%(unit)s, %(house)s, %(street)s, %(city)s, %(state)s, %(county)s, %(country)s, %(postcode)s, %(long)s, %(lat)s, %(formatted)s)
                RETURNING id;
            """, {
                    "unit": address.unit_number,
                    "house": address.house_number,
                    "street": address.street_addr,
                    "city": address.city,
                    "state": address.state,
                    "county": address.county,
                    "country": address.country,
                    "postcode": address.postcode,
                    "long": address.longitude,
                    "lat": address.latitude,
                    "formatted": address.formatted_str,
                })
            address_id = cur.fetchone()

            if address_id:
                address_id = address_id[0]
            else:
                return None
        conn.commit()

        log_green("Finished inserting the Address in Database")
    except Error as e:
        log_red(f"Error inserting Address: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return address_id

def delete_address(address_id: int):
    """
    Delete address no longer associated with an eatery or customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM addresses WHERE id = %(address_id)s;",
                {"address_id": address_id})
        conn.commit()

        log_green("Finished deleting the Address from Database")
    except Error as e:
        log_red(f"Error deleting Address: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def get_all_addresses() -> Optional[List[int]]:
    """
    Fetches all addresses
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM addresses;")
            all_addresses = cur.fetchall()

        log_green("Finished getting all Addresses in Database")
    except Error as e:
        log_red(f"Error getting all Addresses: {e}")
        raise e
    finally:
        disconnect(conn)

    return [address[0] for address in all_addresses]

def get_address_by_id(address_id: int) -> Optional[AddressDetailsResponse]:
    """
    Fetches address' details from DB given address ID
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT unit_number, house_number, street_addr, city, state, country, postcode, longitude, latitude, formatted_str FROM addresses WHERE id = %(id)s;",
                {"id": address_id})
            res = cur.fetchone()

            if res is None:
                return None

            unit_number, house_number, street_addr, city, state, country, postcode, long, lat, formatted = res

        log_green("Finished getting information for the specified Address in Database")
    except Error as e:
        log_red(f"Error displaying Address\' information: {e}")
        raise e
    finally:
        disconnect(conn)

    return AddressDetailsResponse(
        unit_number=unit_number,
        house_number=house_number,
        street_addr=street_addr,
        city=city,
        state=state,
        country=country,
        postcode=postcode,
        longitude=long,
        latitude=lat,
        formatted_str=formatted,
    )

def get_addresses_by_street(street: str) -> Optional[List[int]]:
    """
    Fetches IDs of all addresses that have matching street
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM addresses WHERE street_addr = %(street)s;",
                {"street": street})
            addresses_raw = cur.fetchall()

        log_green("Finished getting the Address in Database based on street")
    except Error as e:
        log_red(f"Error getting Address by street: {e}")
        raise e
    finally:
        disconnect(conn)

    return [address[0] for address in addresses_raw]

def get_addresses_by_city(city: str) -> Optional[List[int]]:
    """
    Fetches IDs of all addresses that have matching city
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM addresses WHERE city = %(city)s;",
                {"city": city})
            addresses_raw = cur.fetchall()

        log_green("Finished getting the Address in Database based on city")
    except Error as e:
        log_red(f"Error getting Address by city: {e}")
        raise e
    finally:
        disconnect(conn)

    return [address[0] for address in addresses_raw]

def get_addresses_by_state(state: str) -> Optional[List[int]]:
    """
    Fetches IDs of all addresses that have matching state
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM addresses WHERE state = %(state)s;",
                {"state": state})
            addresses_raw = cur.fetchall()

        log_green("Finished getting the Address in Database based on state")
    except Error as e:
        log_red(f"Error getting Address by state: {e}")
        raise e
    finally:
        disconnect(conn)

    return [address[0] for address in addresses_raw]

def get_addresses_by_country(country: str) -> Optional[List[int]]:
    """
    Fetches IDs of all addresses that have matching country
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM addresses WHERE country = %(country)s;",
                {"country": country})
            addresses_raw = cur.fetchall()

        log_green("Finished getting the Address in Database based on country")
    except Error as e:
        log_red(f"Error getting Address by country: {e}")
        raise e
    finally:
        disconnect(conn)

    return [address[0] for address in addresses_raw]

def get_addresses_by_postcode(postcode: str) -> Optional[List[int]]:
    """
    Fetches IDs of all addresses that have matching postcode
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM addresses WHERE postcode = %(postcode)s;",
                {"postcode": postcode})
            addresses_raw = cur.fetchall()

        log_green("Finished getting the Address in Database based on postcode")
    except Error as e:
        log_red(f"Error getting Address by postcode: {e}")
        raise e
    finally:
        disconnect(conn)

    return [address[0] for address in addresses_raw]

def get_addresses_by_latitude_longitude(latitude: float, longitude: float) -> Optional[List[int]]:
    """
    Fetches IDs of all addresses that have matching latitude and longitude
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM addresses WHERE latitude = %(latitude)s AND longitude = %(longitude)s;",
                {
                    "latitude": latitude,
                    "longitude": longitude
                })
            addresses_raw = cur.fetchall()

        log_green("Finished getting the Address in Database based on latitude and longitude")
    except Error as e:
        log_red(f"Error getting Address by latitude and longitude: {e}")
        raise e
    finally:
        disconnect(conn)

    return [address[0] for address in addresses_raw]
