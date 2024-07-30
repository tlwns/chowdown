from typing import List, Optional
from psycopg2 import Error

from logger import log_red, log_green

from db.helpers import connect, disconnect
from db.db_types.db_request import VoucherInstanceCreationRequest, VoucherStatusType
from db.db_types.db_response import VoucherInstanceDetailsResponse

def insert_voucher_instance(voucher_instance: VoucherInstanceCreationRequest) -> Optional[List[int]]:
    """
    Inserts instances of a voucher into DB
    """
    instance_ids: List[int] = []
    try:
        conn = connect()
        with conn.cursor() as cur:
            for _ in range(voucher_instance.qty):
                cur.execute(
                    """
                    INSERT INTO voucher_instances (voucher, customer)
                    VALUES (%(voucher)s, NULL)
                    RETURNING id;
                """, {
                        "voucher": voucher_instance.voucher,
                    })
                instance_id = cur.fetchone()
                if instance_id:
                    instance_ids.append(instance_id[0])
        conn.commit()

        if voucher_instance.status and voucher_instance.status != 'unpublished':
            for instance_id in instance_ids:
                update_voucher_instance_status(instance_id, voucher_instance.status)

        log_green(f"Finished inserting the \"{voucher_instance.qty}\" Voucher Instances in Database")
    except Error as e:
        log_red(f"Error inserting Voucher Instances: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return instance_ids

def get_voucher_instance_by_id(voucher_instance_id: int) -> Optional[VoucherInstanceDetailsResponse]:
    """
    Fetches information about a voucher instance from DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, redemption_code, voucher, customer, reviewed FROM voucher_instances WHERE id = %(id)s;",
                {"id": voucher_instance_id})
            res = cur.fetchone()

            if res is None:
                return None

            status, redemption_code, voucher, customer, reviewed = res

        log_green("Finished getting public information for the specified Voucher in Database")
    except Error as e:
        log_red(f"Error displaying Voucher\'s public information: {e}")
        raise e
    finally:
        disconnect(conn)

    return VoucherInstanceDetailsResponse(
        status=status,
        redemption_code=redemption_code,
        voucher=voucher,
        customer=customer,
        reviewed=reviewed
    )

def get_voucher_instances_by_voucher(voucher_id: int) -> Optional[List[int]]:
    """
    Fetches all voucher instances belonging to a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM voucher_instances WHERE voucher = %(voucher)s;", {
                "voucher": voucher_id
            })
            all_instances = cur.fetchall()

        log_green("Finished getting all Voucher Instances in Database based on voucher")
    except Error as e:
        log_red(f"Error getting all Voucher Instances by voucher: {e}")
        raise e
    finally:
        disconnect(conn)

    return [instance[0] for instance in all_instances]

def get_voucher_instances_by_customer(customer_id: int) -> Optional[List[int]]:
    """
    Fetches all voucher instances belonging to a customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM voucher_instances WHERE customer = %(customer)s;", {
                "customer": customer_id
            })
            all_instances = cur.fetchall()

        log_green("Finished getting all Voucher Instances in Database based on customer")
    except Error as e:
        log_red(f"Error getting all Voucher Instances by customer: {e}")
        raise e
    finally:
        disconnect(conn)

    return [instance[0] for instance in all_instances]

def get_voucher_instances_by_status(voucher_id: int, status: VoucherStatusType) -> Optional[List[int]]:
    """
    Gets all voucher instances with matching status
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM voucher_instances WHERE voucher = %(voucher)s AND status = %(status)s;", {
                "voucher": voucher_id,
                "status": status
            })
            all_instances = cur.fetchall()

        log_green("Finished getting Voucher Instances in Database based on status")
    except Error as e:
        log_red(f"Error getting Voucher Instances by status: {e}")
        raise e
    finally:
        disconnect(conn)

    return [instance[0] for instance in all_instances]

def get_voucher_instance_status(voucher_instance_id: int) -> Optional[VoucherStatusType]:
    """
    Gets status for a voucher instance
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM voucher_instances WHERE id = %(id)s;", {
                "id": voucher_instance_id
            })
            status = cur.fetchone()

        log_green("Finished getting status for the Voucher Instance in Database")
    except Error as e:
        log_red(f"Error getting status for the Voucher Instance: {e}")
        raise e
    finally:
        disconnect(conn)

    if status:
        return status[0]

    return None

def get_all_redemption_codes() -> Optional[List[str]]:
    """
    Fetches all redemption codes from the DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT redemption_code FROM voucher_instances WHERE redemption_code IS NOT NULL;")
            all_codes = cur.fetchall()

        log_green("Finished getting all Redemption Codes in Database")
    except Error as e:
        log_red(f"Error getting all Redemption Codes: {e}")
        raise e
    finally:
        disconnect(conn)

    return [code[0] for code in all_codes]

def update_voucher_instance_status(voucher_instance_id: int, status: VoucherStatusType):
    """
    Updates status for an voucher instance
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("UPDATE voucher_instances SET status = %(status)s WHERE id = %(id)s;", {
                    "status": status,
                    "id": voucher_instance_id
                })
        conn.commit()

        log_green("Finished updating status for the Voucher Instance in Database")
    except Error as e:
        log_red(f"Error updating status for the Voucher Instance: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_voucher_instance_review_status(voucher_instance_id: int, review_status: bool):
    """
    Updates a voucher instance's review status
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE voucher_instances SET reviewed = %(reviewed)s WHERE id = %(id)s;",
                {
                    "reviewed": review_status,
                    "id": voucher_instance_id
                })
        conn.commit()

        log_green("Finished updating the reviewed field for the Voucher Instance in Database")
    except Error as e:
        log_red(f"Error updating the reviewed field for the Voucher Instance: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def allocate_voucher_instance(voucher_instance_id: int, customer_id: int):
    """
    Allocates the voucher instance to a customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("UPDATE voucher_instances SET customer = %(customer)s WHERE id = %(id)s;", {
                    "customer": customer_id,
                    "id": voucher_instance_id
                })
        conn.commit()

        log_green("Finished allocating the Voucher Instance in Database to the customer")
    except Error as e:
        log_red(f"Error allocating the Voucher Instance to the customer: {e}")
        raise e
    finally:
        disconnect(conn)

def deallocate_voucher_instance(voucher_instance_id: int):
    """
    Deallocates the voucher instance to a customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("UPDATE voucher_instances SET customer = NULL, redemption_code = NULL, status = 'unclaimed' WHERE id = %(id)s;", {
                    "id": voucher_instance_id
                })
        conn.commit()

        log_green("Finished deallocating the Voucher Instance in Database from the customer")
    except Error as e:
        log_red(f"Error deallocating the Voucher Instance from the customer: {e}")
        raise e
    finally:
        disconnect(conn)

def allocate_redemption_code(voucher_instance_id: int, redemption_code: str):
    """
    Allocates the redemption code to a voucher instance
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("UPDATE voucher_instances SET redemption_code = %(code)s WHERE id = %(id)s;", {
                    "code": redemption_code,
                    "id": voucher_instance_id
                })
        conn.commit()

        log_green("Finished allocating the redemption code to a Voucher Instance in Database")
    except Error as e:
        log_red(f"Error allocating the redemption code to a Voucher Instance: {e}")
        raise e
    finally:
        disconnect(conn)

def deallocate_redemption_code(voucher_instance_id: int):
    """
    Deallocates the redemption code to a voucher instance
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("UPDATE voucher_instances SET redemption_code = NULL, status = 'unclaimed' WHERE id = %(id)s;", {
                    "id": voucher_instance_id
                })
        conn.commit()

        log_green("Finished deallocating the redemption code to a Voucher Instance in Database")
    except Error as e:
        log_red(f"Error deallocating the redemption code to a Voucher Instance: {e}")
        raise e
    finally:
        disconnect(conn)

def get_voucher_instance_id_by_redemption_code(redemption_code: str) -> Optional[int]:
    """
    Gets the voucher instance id with the provided redemption code
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM voucher_instances WHERE redemption_code = %(redemption_code)s;", {
                "redemption_code": redemption_code
                })
            instance_id = cur.fetchone()

        log_green("Finished getting Voucher Instance by Redemption Code in Database")
    except Error as e:
        log_red(f"Error getting Voucher Instances by Redemption Code: {e}")
    finally:
        disconnect(conn)

    if instance_id:
        return instance_id[0]

    return None
