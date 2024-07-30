from datetime import datetime, timezone
import math
from typing import List, Tuple
from geopy.distance import geodesic

from functionality.errors import ValidationError
from functionality.helpers import get_average_eatery_rating_sort, get_vouchers_unclaimed
from functionality.voucher import get_average_voucher_rating, get_expiry
from functionality.customer import get_customer_past_eateries, get_customer_past_eateries_reviews
from functionality.address import get_customer_location, get_eatery_date_joined, get_eatery_location

from db.helpers.customer import get_customer_preferences_by_id, get_all_favourited_eateries
from db.helpers.voucher import get_voucher_quantity, get_vouchers_by_voucher_template
from db.helpers.voucher_template import get_voucher_templates_for_eatery_by_is_deleted
from db.helpers.eatery import get_eatery_keywords_by_id

from router.api_types.api_request import Sorts

def round_dist(meters: float) -> int:
    """
    Special location rounding for distance
    """
    # if under 1 km away round up to nearest 100 m
    if meters < 1000:
        meters = math.ceil(meters / 100)
        return meters * 100
    # if under 30 kms round up to nearest km
    if meters < 30000:
        meters = math.ceil(meters / 1000)
        return meters * 1000
    # if under 100 kms round up to nearest 10km
    if meters < 100000:
        meters = math.ceil(meters / 10000)
        return meters * 10000
    # if under 1000kms round up to nearest 100kms
    if meters < 1000000:
        meters = math.ceil(meters / 100000)
        return meters * 100000
    # otherwise round up to nearest 1000kms
    meters = math.ceil(meters / 1000000)
    return meters * 1000000

def distance_between_coords(coord_1: Tuple[float, float], coord_2: Tuple[float, float]) -> int:
    """
    gets rounded dist b/w coords
    """
    return round_dist(geodesic(coord_1, coord_2).meters)

def preference_commonality(customer_preferences: List[str], eatery_keywords: List[str]) -> int:
    """
    counts preference commonality

    change later to a commonality score
    """
    return sum(1 for pref in customer_preferences if pref in eatery_keywords)

def get_active_vouchers(eatery_id: int) -> List[int]:
    """
    Gets active vouchers for an eatery
    """
    # TODO: convert to a join query
    active_voucher_templates = get_voucher_templates_for_eatery_by_is_deleted(eatery_id, False)
    if active_voucher_templates is None:
        raise ValueError("Error retrieving active vouchers")
    
    active_vouchers: List[int] = []
    for template_id in active_voucher_templates:
        voucher_ids = get_vouchers_by_voucher_template(template_id)
        if voucher_ids is not None:
            active_vouchers.extend(voucher_ids)

    return active_vouchers

def recommend_sort(customer_id: int, eateries: List[int], sorts: List[Sorts]) -> List[int]:
    """
    Sorts by distance and preference
    """
    customer_location = get_customer_location(customer_id)
    customer_reviews = get_customer_past_eateries_reviews(customer_id)
    past_eateries = get_customer_past_eateries(customer_id)

    customer_preferences = get_customer_preferences_by_id(customer_id)
    favourited_eateries = get_all_favourited_eateries(customer_id)
    if customer_preferences is None or favourited_eateries is None:
        raise ValidationError("Error retrieving customer preferences and / or favourite eateries")

    eatery_details = []
    for eatery_id in eateries:
        eatery_keywords = get_eatery_keywords_by_id(eatery_id)
        if eatery_keywords is None:
            raise ValidationError("Error retrieving eatery keywords")

        rating = customer_reviews.get(eatery_id)
        if rating is None:
            rating = get_average_eatery_rating_sort(eatery_id)

        eatery_details.append({
            "eid": eatery_id,
            "distance": distance_between_coords(customer_location, get_eatery_location(eatery_id)),
            "vouchers": len(get_active_vouchers(eatery_id)),
            "keywords": preference_commonality(customer_preferences, eatery_keywords),
            "rating": rating,
            "not_tried": eatery_id not in past_eateries,
            "favourite": eatery_id in favourited_eateries,
            "register_date": get_eatery_date_joined(eatery_id)
        })

    # Remove irrelevant things
    # Limit distance always
    eatery_details = [
        eatery for eatery in eatery_details if eatery["distance"] <= 10000]
    if Sorts.RATING in sorts:
        # Minimum rating filter
        eatery_details = [
            eatery for eatery in eatery_details if eatery["rating"] >= 2.5]
    if Sorts.VOUCHERS in sorts:
        # Vouchers available
        eatery_details = [
            eatery for eatery in eatery_details if eatery["vouchers"] > 0]
    if Sorts.NOT_TRIED in sorts:
        # Not previously tried
        eatery_details = [
            eatery for eatery in eatery_details if eatery["not_tried"]]

    # Always apply some basic sorts, more important sorts are bumped later
    eatery_details.sort(key=lambda x: x["vouchers"], reverse=True)
    eatery_details.sort(key=lambda x: x["keywords"])
    eatery_details.sort(key=lambda x: x["rating"], reverse=True)
    eatery_details.sort(key=lambda x: x["distance"])

    # Sorting according to the order in "sorts"
    sorts.reverse()
    for sort in sorts:
        if sort == Sorts.DISTANCE:
            eatery_details.sort(key=lambda x: x["distance"])
        elif sort == Sorts.FAVOURITES:
            eatery_details.sort(key=lambda x: x["favourite"], reverse=True)
        elif sort == Sorts.NEWEST:
            eatery_details.sort(key=lambda x: x["register_date"], reverse=True)
        elif sort == Sorts.RATING:
            eatery_details.sort(key=lambda x: x["rating"], reverse=True)
        elif sort == Sorts.VOUCHERS:
            eatery_details.sort(key=lambda x: x["vouchers"], reverse=True)
        elif sort == Sorts.NOT_TRIED:
            eatery_details.sort(key=lambda x: x["not_tried"], reverse=True)
        elif sort == Sorts.KEYWORDS:
            eatery_details.sort(key=lambda x: x["keywords"], reverse=True)

    return [detail["eid"] for detail in eatery_details]

def basic_recommend_sort(eateries: List[int]) -> List[int]:
    """
    Sorts by registration date rating and number of vouchers
    """
    # Get lnum vouchers average rating and register date
    eatery_details = []
    for eatery_id in eateries:
        vouchers = get_active_vouchers(eatery_id)

        eatery_details.append({
            "eid": eatery_id,
            "vouchers": len(vouchers),
            "rating": get_average_eatery_rating_sort(eatery_id),
            "register_date": get_eatery_date_joined(eatery_id)
        })
    
    eatery_details.sort(key=lambda x: x["register_date"], reverse=True)
    # sort by number of vouchers
    eatery_details.sort(key=lambda x: x["vouchers"], reverse=True)

    # Sort by reviews
    eatery_details = [eatery for eatery in eatery_details if eatery["rating"] >= 2.5]
    eatery_details.sort(key=lambda x: x["rating"], reverse=True)

    return [detail["eid"] for detail in eatery_details]

def top_3_vouchers(eatery_id: int) -> List[int]:
    """
    Sorts by distance and preference
    """
    # Get location and keywords for each eatery
    vouchers = get_active_vouchers(eatery_id)

    voucher_details = []
    for voucher_id in vouchers:
        unclaimed = get_vouchers_unclaimed([voucher_id])
        if unclaimed is None:
            raise ValidationError("Error retrieving unclaimed vouchers")

        total = get_voucher_quantity(voucher_id)
        if total is None:
            raise ValidationError("Error retrieving total voucher count")

        voucher_details.append({
            "vid": voucher_id,
            "rating": get_average_voucher_rating(voucher_id),
            "expiry": get_expiry(voucher_id),
            "rate": unclaimed / total if total is not None else 1
        })

    # sort by rating
    voucher_details.sort(key=lambda x: x["rating"])

    # remove vouchers that have expired
    voucher_details = [
        vouch for vouch in voucher_details if vouch["expiry"] > datetime.now(timezone.utc)]
    voucher_details.sort(key=lambda x: x["expiry"])

    # Sort by speed consumed
    voucher_details.sort(key=lambda x: x["rate"])

    return [detail["vid"] for detail in voucher_details][:3]
