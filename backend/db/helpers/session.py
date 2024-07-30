from typing import List, Literal, Optional
from datetime import datetime
from psycopg2 import Error

from logger import log_red, log_green

from db.helpers import connect, disconnect
from db.db_types.db_request import SessionCreationRequest
from db.db_types.db_response import SessionDetailsResponse

def create_session(session: SessionCreationRequest) -> Optional[int]:
    """
    Creates a session in the DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO all_sessions (refresh_token, time_last_updated, eatery, customer) VALUES (%(token)s, %(time_created)s, %(eatery)s, %(customer)s) RETURNING id;
            """, {
                    "token": session.refresh_token,
                    "time_created": session.time_last_updated,
                    "eatery": session.eatery,
                    "customer": session.customer
                })
            session_id = cur.fetchone()
        conn.commit()

        log_green("Finished inserting the Session in Database")
    except Error as e:
        log_red(f"Error inserting Session: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    if session_id:
        return session_id[0]

    return None

def check_if_session_exists(session_id: int) -> Optional[bool]:
    """
    Checks if the session exists in DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM all_sessions WHERE id = %(id)s);", {"id": session_id})
            exists = cur.fetchone()

        log_green("Finished checking if the Session exists in Database")
    except Error as e:
        log_red(f"Error checking if the Session exists: {e}")
        raise e
    finally:
        disconnect(conn)

    if exists:
        return exists[0]

    return None

def view_session(session_id: int) -> Optional[SessionDetailsResponse]:
    """
    Fetches the information for a session in the DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT refresh_token, time_last_updated, eatery, customer FROM all_sessions WHERE id = %(id)s;", {"id": session_id})
            res = cur.fetchone()

            if res is None:
                return None

            refresh_token, time_last_updated, eatery, customer = res

        log_green("Finished getting information about the Session in Database")
    except Error as e:
        log_red(f"Error getting information about the Session: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return SessionDetailsResponse(
        refresh_token=refresh_token,
        time_last_updated=time_last_updated,
        eatery=eatery,
        customer=customer
    )

def view_all_sessions() -> Optional[List[int]]:
    """
    Fetches the information for all sessions in the DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM all_sessions;")
            all_sessions = cur.fetchall()

        log_green("Finished getting information about the Session in Database")
    except Error as e:
        log_red(f"Error getting information about the Session: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return [session[0] for session in all_sessions]

def get_active_sessions_for_eatery(eatery_id: int) -> Optional[List[int]]:
    """
    Gets active sessions in the DB by eatery
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM all_sessions WHERE eatery = %(eatery_id)s;", {"eatery_id": eatery_id})
            sessions_raw = cur.fetchall()

        log_green("Finished getting active Sessions in Database based on Eatery")
    except Error as e:
        log_red(f"Error getting active Sessions based on Eatery: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return [session[0] for session in sessions_raw]

def get_active_sessions_for_customer(customer_id: int) -> Optional[List[int]]:
    """
    Gets active sessions in the DB by customer
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM all_sessions WHERE customer = %(customer_id)s;", {"customer_id": customer_id})
            sessions_raw = cur.fetchall()

        log_green("Finished getting active Sessions in Database based on Customer")
    except Error as e:
        log_red(f"Error getting active Sessions based on Customer: {e}")
        raise e
    finally:
        disconnect(conn)

    return [session[0] for session in sessions_raw]

def get_user_type_by_session(session_id: int) -> Optional[Literal["customer", "eatery"]]:
    """
    Fetches the type of user linked with session id from DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    CASE
                        WHEN eatery IS NOT NULL THEN 'eatery'
                        WHEN customer IS NOT NULL THEN 'customer'
                        ELSE 'Unknown'
                    END AS user_type
                FROM
                    all_sessions
                WHERE
                    id = %(id)s;
            """, {"id": session_id})
            user_type = cur.fetchone()

        log_green("Finished getting type of user linked with Session id in Database")
    except Error as e:
        log_red(f"Error getting type of user linked with Session id: {e}")
        raise e
    finally:
        disconnect(conn)

    if user_type:
        return user_type[0]

    return None

def delete_session(session_id: int):
    """
    Deletes an existing session in the DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM all_sessions WHERE id = %(id)s;", {"id": session_id})
        conn.commit()

        log_green("Finished deleting the Session from Database")
    except Error as e:
        log_red(f"Error deleting Session: {e}")
        raise e
    finally:
        disconnect(conn)

def update_refresh_token_in_session(session_id: int, refresh_token: str, time_last_updated: datetime):
    """
    Updates refresh id in session
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE all_sessions SET refresh_token = %(token)s, time_last_updated = %(updated)s WHERE id = %(id)s;",
                {
                    "id": session_id,
                    "token": refresh_token,
                    "updated": time_last_updated
                })
        conn.commit()

        log_green("Finished updating refresh id for the Session in Database")
    except Error as e:
        log_red(f"Error updating refresh id for the Session: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)
