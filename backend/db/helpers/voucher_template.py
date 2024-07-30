from datetime import timedelta, datetime
from typing import List, Optional
from psycopg2 import Error

from logger import log_red, log_green

from db.helpers import connect, disconnect
from db.db_types.db_request import VoucherTemplateCreationRequest
from db.db_types.db_response import VoucherTemplateDetailsResponse, VoucherTemplateScheduleDetailsResponse

def insert_voucher_template(voucher_template: VoucherTemplateCreationRequest) -> Optional[int]:
    """
    Inserts a voucher into DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO voucher_templates (title, description, conditions, date_created, release_date, release_schedule, release_duration, release_size, eatery)
                VALUES (%(title)s, %(desc)s, %(cond)s, %(date_issue)s, %(date_release)s, %(schedule)s, %(duration)s, %(size)s, %(eatery)s)
                RETURNING id;
            """, {
                    "title": voucher_template.name,
                    "desc": voucher_template.description,
                    "cond": voucher_template.conditions,
                    "date_issue": voucher_template.created,
                    "date_release": voucher_template.release_date,
                    "schedule": voucher_template.release_schedule,
                    "duration": voucher_template.duration,
                    "size": voucher_template.release_size,
                    "eatery": voucher_template.eatery,
                })
            voucher_id = cur.fetchone()

            if voucher_id:
                voucher_id = voucher_id[0]
            else:
                return None
        conn.commit()

        if voucher_template.is_published:
            update_voucher_template_published_status(voucher_id, voucher_template.is_published)

        if voucher_template.is_deleted:
            update_voucher_template_is_deleted(voucher_id, voucher_template.is_deleted)

        log_green("Finished inserting the Voucher Template in Database")
    except Error as e:
        log_red(f"Error inserting Voucher Template: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return voucher_id

def get_voucher_template_by_id(voucher_template_id: int) -> Optional[VoucherTemplateDetailsResponse]:
    """
    Fetches information about a voucher template from DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT title, description, conditions, date_created, eatery, is_deleted, is_published FROM voucher_templates WHERE id = %(id)s;",
                {"id": voucher_template_id})
            res = cur.fetchone()

            if res is None:
                return None

            title, desc, cond, created, eatery, is_deleted, is_pub = res

        log_green("Finished getting public information for the specified Voucher Template in Database")
    except Error as e:
        log_red(f"Error displaying Voucher Template\'s public information: {e}")
        raise e
    finally:
        disconnect(conn)

    qty = get_voucher_template_quantity(voucher_template_id)
    if qty is None:
        return None

    return VoucherTemplateDetailsResponse(
        name=title,
        description=desc,
        conditions=cond,
        created=created,
        eatery=eatery,
        quantity=qty,
        is_deleted=is_deleted,
        is_published=is_pub
    )

def get_voucher_template_quantity(voucher_template_id: int) -> Optional[int]:
    """
    Fetches count of instances for a voucher template in DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM voucher_templates JOIN vouchers ON voucher_templates.id = vouchers.voucher_template
                JOIN voucher_instances ON vouchers.id = voucher_instances.voucher
                WHERE voucher_templates.id = %(id)s;
                """, {
                    "id": voucher_template_id
                })
            qty = cur.fetchone()

        log_green("Finished getting Voucher Templates for the Eatery in Database")
    except Error as e:
        log_red(f"Error getting Voucher Templates for the Eatery: {e}")
        raise e
    finally:
        disconnect(conn)

    if qty:
        return qty[0]

    return None

def get_voucher_templates_by_eatery(eatery_id: int) -> Optional[List[int]]:
    """
    Fetches voucher templates based on eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM voucher_templates WHERE eatery = %(id)s",
                        {"id": eatery_id})
            vouchers_raw = cur.fetchall()

        log_green("Finished getting Voucher Templates for the Eatery in Database")
    except Error as e:
        log_red(f"Error getting Voucher Templates for the Eatery: {e}")
        raise e
    finally:
        disconnect(conn)

    return [voucher[0] for voucher in vouchers_raw]

def get_vouchers_templates_for_eatery_by_published_status(eatery_id: int, published_status: bool) -> Optional[List[int]]:
    """
    Fetches vouchers for an based on published status
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM voucher_templates WHERE eatery = %(id)s AND is_published = %(status)s", {
                "id": eatery_id,
                "status": published_status
            })
            vouchers_raw = cur.fetchall()

        log_green("Finished getting Voucher Template for the Eatery in Database based on published status")
    except Error as e:
        log_red(f"Error getting Voucher Template for the Eatery based on published status: {e}")
        raise e
    finally:
        disconnect(conn)

    return [voucher[0] for voucher in vouchers_raw]

def get_voucher_templates_for_eatery_by_is_deleted(eatery_id: int, is_deleted: bool) -> Optional[List[int]]:
    """
    Fetches vouchers for an based on is_deleted status
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM voucher_templates WHERE eatery = %(id)s AND is_deleted = %(status)s", {
                "id": eatery_id,
                "status": is_deleted
            })
            vouchers_raw = cur.fetchall()

        log_green("Finished getting Voucher Template for the Eatery in Database based on is_deleted status")
    except Error as e:
        log_red(f"Error getting Voucher Template for the Eatery based on is_deleted status: {e}")
        raise e
    finally:
        disconnect(conn)

    return [voucher[0] for voucher in vouchers_raw]

def get_voucher_template_published_status(voucher_id: int) -> Optional[bool]:
    """
    Gets published status for a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT is_published FROM voucher_templates WHERE id = %(id)s;",
                        {"id": voucher_id})
            is_pub = cur.fetchone()

        log_green("Finished getting published status for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error getting published status for the Voucher Template: {e}")
        raise e
    finally:
        disconnect(conn)

    if is_pub:
        return is_pub[0]

    return None

def get_voucher_template_is_deleted(voucher_id: int) -> Optional[bool]:
    """
    Gets is_deleted status for a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT is_deleted FROM voucher_templates WHERE id = %(id)s;",
                        {"id": voucher_id})
            is_deleted = cur.fetchone()

        log_green("Finished getting is_deleted status for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error getting is_deleted status for the Voucher Template: {e}")
        raise e
    finally:
        disconnect(conn)

    if is_deleted:
        return is_deleted[0]

    return None

def update_voucher_template_published_status(voucher_id: int, published: bool):
    """
    Updates published status for an voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE voucher_templates SET is_published = %(status)s WHERE id = %(id)s;", {
                    "status": published,
                    "id": voucher_id
                })
        conn.commit()

        log_green("Finished updating published status for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error updating published status for the Voucher Template: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_voucher_template_is_deleted(voucher_id: int, is_deleted: bool):
    """
    Updates is_deleted status for an voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE voucher_templates SET is_deleted = %(status)s WHERE id = %(id)s;", {
                    "status": is_deleted,
                    "id": voucher_id
                })
        conn.commit()

        log_green("Finished updating is_deleted status for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error updating is_deleted status for the Voucher Template: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_voucher_template_name(voucher_id: int, name: str):
    """
    Updates name for a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE voucher_templates SET title = %(title)s WHERE id = %(id)s;", {
                    "title": name,
                    "id": voucher_id
                })
        conn.commit()

        log_green("Finished updating name for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error updating name for the Voucher Template: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_voucher_template_description(voucher_id: int, description: str):
    """
    Updates description for a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE voucher_templates SET description = %(description)s WHERE id = %(id)s;", {
                    "description": description,
                    "id": voucher_id
                })
        conn.commit()

        log_green("Finished updating description for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error updating description for the Voucher Template: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_voucher_template_condition(voucher_id: int, condition: str):
    """
    Updates condition for a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE voucher_templates SET conditions = %(condition)s WHERE id = %(id)s;", {
                    "condition": condition,
                    "id": voucher_id
                })
        conn.commit()

        log_green("Finished updating condition for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error updating condition for the Voucher Template: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def update_voucher_template_duration(voucher_id: int, duration: timedelta):
    """
    Updates duration for a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE voucher_templates SET release_duration = %(duration)s WHERE id = %(id)s;", {
                    "duration": duration,
                    "id": voucher_id
                })
        conn.commit()

        log_green("Finished updating expiry for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error updating expiry for the Voucher Template: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

def get_all_voucher_templates() -> Optional[List[int]]:
    """
    Fetches all the voucher templates
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM voucher_templates;")
            vouchers_raw = cur.fetchall()

        log_green("Finished getting all Voucher Templates in Database")
    except Error as e:
        log_red(f"Error getting all Voucher Templates: {e}")
        raise e
    finally:
        disconnect(conn)

    return [voucher[0] for voucher in vouchers_raw]

def get_voucher_template_schedule_by_id(voucher_template_id: int) -> Optional[VoucherTemplateScheduleDetailsResponse]:
    """
    Fetch all the voucher template scheduling details
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT is_deleted, release_date, release_schedule, release_duration, release_size, last_release FROM voucher_templates WHERE id = %(id)s;",
                        {"id": voucher_template_id})
            res = cur.fetchone()

            if res is None:
                return None

            is_deleted, release_date, release_schedule, release_duration, release_size, last_release = res

        log_green("Finished getting Voucher Template Schedule in Database")
    except Error as e:
        log_red(f"Error getting Voucher Template Schedule: {e}")
        raise e
    finally:
        disconnect(conn)

    return VoucherTemplateScheduleDetailsResponse(
        is_deleted=is_deleted,
        release_date=release_date,
        release_schedule=release_schedule,
        release_duration=release_duration,
        release_size=release_size,
        last_release=last_release
    )

def update_voucher_template_last_release(voucher_template_id: int, last_release: datetime):
    """
    Updates last release for a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE voucher_templates SET last_release = %(release)s WHERE id = %(id)s;", {
                    "release": last_release,
                    "id": voucher_template_id
                })
        conn.commit()

        log_green("Finished updating last release for the Voucher Template in Database")
    except Error as e:
        log_red(f"Error updating last release for the Voucher Template: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)
