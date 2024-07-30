from typing import List, Optional
from psycopg2 import Error

from logger import log_red, log_green

from db.helpers import connect, disconnect
from db.db_types.db_request import ReviewCreationRequest
from db.db_types.db_response import ReviewDetailsResponse

def create_review(review: ReviewCreationRequest) -> Optional[int]:
    """
    Inserts a Review into DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reviews (description, rating, date_created, voucher_instance, anonymous)
                VALUES (%(desc)s, %(rating)s, %(created)s, %(instance)s, %(anon)s)
                RETURNING id;
            """, {
                    "desc": review.description,
                    "rating": review.rating,
                    "created": review.created,
                    "instance": review.voucher_instance,
                    "anon": review.anonymous
                })
            review_id = cur.fetchone()

            if review_id is None:
                return None

        conn.commit()

        log_green("Finished inserting the Review in Database")
    except Error as e:
        log_red(f"Error inserting Review: {e}")
        conn.rollback()
        raise e
    finally:
        disconnect(conn)

    return review_id[0]

def get_review_by_id(review_id: int) -> Optional[ReviewDetailsResponse]:
    """
    Fetches information about a Review from DB
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT description, rating, date_created, voucher_instance, anonymous FROM reviews WHERE id = %(id)s;",
                {
                    "id": review_id
                })
            res = cur.fetchone()

            if res is None:
                return None

            desc, rating, date_created, instance, anon = res

        log_green("Finished getting information for the specified Review in Database")
    except Error as e:
        log_red(f"Error displaying Review\'s information: {e}")
        raise e
    finally:
        disconnect(conn)

    return ReviewDetailsResponse(
        description=desc,
        rating=rating,
        created=date_created,
        voucher_instance=instance,
        anonymous=anon
    )

def get_review_by_voucher_instance(voucher_instance_id: int) -> Optional[int]:
    """
    Fetches the review belonging to the voucher instance
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM reviews WHERE voucher_instance = %(instance)s;",
            {
                "instance": voucher_instance_id
            })
            review = cur.fetchone()

        log_green("Finished getting all Reviews in Database based on voucher instance")
    except Error as e:
        log_red(f"Error getting all Reviews by voucher instance: {e}")
        raise e
    finally:
        disconnect(conn)

    if review:
        return review[0]

    return None

def get_reviews_by_voucher(voucher_id: int) -> Optional[List[int]]:
    """
    Fetches all reviews belonging to a voucher
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                    SELECT r.id FROM reviews r
                    JOIN voucher_instances vi ON r.voucher_instance = vi.id 
                    WHERE vi.voucher = %(voucher)s;
                """,
                {
                    "voucher": voucher_id
                }
            )
            review_ids = cur.fetchall()

        log_green("Finished getting all Review IDs from Voucher ID in Database")
    except Error as e:
        log_red(f"Error getting all Review IDs from Voucher ID: {e}")
        raise e
    finally:
        disconnect(conn)

    return [review_id[0] for review_id in review_ids]

def get_reviews_by_voucher_template(voucher_template: int) -> Optional[List[int]]:
    """
    Fetches all reviews belonging to a voucher template
    """
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                    SELECT r.id FROM reviews r
                    JOIN voucher_instances vi ON r.voucher_instance = vi.id 
                    JOIN vouchers v ON vi.voucher = v.id 
                    WHERE v.voucher_template = %(template)s;
                """,
                {
                    "template": voucher_template
                }
            )
            review_ids = cur.fetchall()

        log_green("Finished getting all Review IDs from Voucher Template in Database")
    except Error as e:
        log_red(f"Error getting all Review IDs from Voucher Template: {e}")
        raise e
    finally:
        disconnect(conn)

    return [review_id[0] for review_id in review_ids]

def get_reviews_by_eatery(eatery_id: int) -> Optional[List[int]]:
    """
    Fetches all reviews belonging to an eatery
    """
    # TODO: ideally we denormalize at this point and add eatery id as a field on reviews
    try:
        conn = connect()
        with conn.cursor() as cur:
            cur.execute(
                """
                    SELECT r.id FROM reviews r
                    JOIN voucher_instances vi ON r.voucher_instance = vi.id 
                    JOIN vouchers v ON vi.voucher = v.id 
                    JOIN voucher_templates vt ON v.voucher_template = vt.id 
                    WHERE vt.eatery = %(eatery)s;
                """,
                {
                    "eatery": eatery_id
                }
            )
            review_ids = cur.fetchall()

        log_green("Finished getting all Review IDs from Eatery in Database")
    except Error as e:
        log_red(f"Error getting all Review IDs from Eatery: {e}")
        raise e
    finally:
        disconnect(conn)

    return [review_id[0] for review_id in review_ids]
