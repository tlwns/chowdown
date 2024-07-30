import re
from typing import List

from functionality.errors import ValidationError

from db.helpers.review import get_review_by_id, get_reviews_by_eatery
from db.helpers.voucher_instance import get_voucher_instances_by_status

def validate_regex_phone(phone: str) -> bool:
    """
    Validates phone number using regex
    """
    regex = r"^\+?[0-9]{1,3}?[-\s.]?([(]?[0-9]{1,4}[)])?[-\s.]?[0-9]{1,4}[-\s.]?[0-9]{1,4}[-\s.]?[0-9]{1,9}$"

    if re.fullmatch(regex, phone) is None:
        raise ValueError("Invalid phone number")

    return True

def validate_regex_email(email: str):
    """
    Validates phone number using regex
    """
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValidationError("Invalid Email")

def validate_regex_password(password: str) -> bool:
    """
    Keeping it simple for now
    """

    regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@_$!%*?&]{8,}$"

    if re.fullmatch(regex, password) is None:
        raise ValueError("Invalid password")

    return len(password) >= 8

def get_vouchers_unclaimed(vouchers: List[int]) -> int:
    """
    Gets the number of vouchers remaining that can be claimed
    """
    num_vouchers = 0
    for vid in vouchers:        
        unclaimed_vouchers = get_voucher_instances_by_status(vid, "unclaimed")
        if unclaimed_vouchers is None:
            raise ValidationError("Error retrieving vouchers")
        
        if len(unclaimed_vouchers) > 0:
            num_vouchers += 1
    
    return num_vouchers

def get_average_eatery_rating_sort(eatery_id: int) -> float:
    """
    Gets an eateries average rating
    """
    reviews = get_reviews_by_eatery(eatery_id)
    if reviews is None:
        raise ValueError("Error retrieving reviews for eatery")
    ratings = get_raw_rating(reviews)

    # if no ratings default to 3 stars for sorting
    if len(ratings) == 0:
        return 2.7
    return sum(ratings) // len(ratings)

def get_raw_rating(review_ids: List[int]) -> List[float]:
    """
    Gets the number rating
    """
    ratings = []
    for rev_id in review_ids:
        review = get_review_by_id(rev_id)
        if review is None:
            raise ValueError("Error getting review")
        ratings.append(review.rating)
    return ratings

def calc_average_rating(eatery_id: int) -> float:
    """
    Calculates average rating for an eatery
    """
    all_reviews = get_reviews_by_eatery(eatery_id)

    if all_reviews is None:
        raise ValidationError("Error retrieving eatery reviews")

    ratings = map(lambda review_id: get_review_by_id(review_id).rating, all_reviews)
    valid_ratings = list(filter(lambda x: x is not None, ratings))

    # Avoid division by zero
    if len(valid_ratings) == 0:
        return 0.0

    return sum(valid_ratings) / len(valid_ratings)
