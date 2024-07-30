from typing import List, Optional
from psycopg2 import Error

from logger import log_red, log_green

from db.helpers import connect, disconnect
from db.db_types.db_request import VoucherCreationRequest
from db.db_types.db_response import VoucherDetailsResponse

def insert_voucher(voucher: VoucherCreationRequest) -> Optional[int]:
    """
    Inserts a voucher into DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO vouchers (voucher_template, release_date, expiry_date)
                VALUES (%(voucher_template)s, %(release_date)s, %(expiry_date)s)
                RETURNING id;
            """, {
                    "voucher_template": voucher.voucher_template,
                    "release_date": voucher.release_date,
                    "expiry_date": voucher.expiry_date
                })
            voucher_id = cur.fetchone()

            if voucher_id:
                voucher_id = voucher_id[0]
            else:
                return None
        conn.commit()

        log_green("Finished inserting the Voucher in Database")
    except Error as e:
        log_red(f"Error inserting Voucher: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return voucher_id

def get_voucher_by_id(voucher_id: int) -> Optional[VoucherDetailsResponse]:
    """
    Fetches information about a voucher from DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT voucher_template, release_date, expiry_date FROM vouchers WHERE id = %(id)s;",
                {"id": voucher_id})
            res = cur.fetchone()

            if res is None:
                return None

            voucher_template, release_date, expiry_date = res

        log_green("Finished getting information for the specified Voucher in Database")
    except Error as e:
        log_red(f"Error displaying Voucher\'s information: {e}")
        raise e
    finally:
        disconnect(conn)

    qty = get_voucher_quantity(voucher_id)
    if qty is None:
        return None

    return VoucherDetailsResponse(
        voucher_template=voucher_template,
        release_date=release_date,
        expiry_date=expiry_date,
        quantity=qty,
    )

def get_voucher_quantity(voucher_id: int) -> Optional[int]:
    """
    Fetches count of instances for a voucher in DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            # Get all voucher batches
            # Get count of each voucher batch

            cur.execute(
                """
                SELECT COUNT(*) FROM voucher_instances WHERE voucher = %(id)s;
                """, {
                    "id": voucher_id
                })
            qty = cur.fetchone()

        log_green("Finished getting Voucher for the Eatery in Database")
    except Error as e:
        log_red(f"Error getting Voucher for the Eatery: {e}")
        raise e
    finally:
        disconnect(conn)

    if qty:
        return qty[0]

    return None

def get_vouchers_by_voucher_template(voucher_template: int) -> Optional[List[int]]:
    """
    Fetches all vouchers belonging to a voucher template
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM vouchers WHERE voucher_template = %(template)s;",
                        {
                            "template": voucher_template
                        })
            vouchers_raw = cur.fetchall()

        log_green("Finished getting all Vouchers in Database based on voucher template")
    except Error as e:
        log_red(f"Error getting all Vouchers by voucher template: {e}")
        raise e
    finally:
        disconnect(conn)

    return [voucher[0] for voucher in vouchers_raw]

def get_vouchers_by_customer(customer_id: int) -> Optional[List[int]]:
    """
    Fetches vouchers based on customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT voucher FROM voucher_instances WHERE customer = %(id)s",
                        {"id": customer_id})
            vouchers_raw = cur.fetchall()

        log_green("Finished getting voucher instances for the Customer in Database")
    except Error as e:
        log_red(f"Error getting voucher instances for the Customer: {e}")
        raise e
    finally:
        disconnect(conn)

    return [voucher[0] for voucher in vouchers_raw]
