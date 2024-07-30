from typing import Literal, Optional, Tuple, Union, List
from datetime import datetime, timezone

from functionality.errors import AuthorisationError, ValidationError, DuplicationError
from functionality.recommendations import basic_recommend_sort, recommend_sort, top_3_vouchers
from functionality.address import valid_address
from functionality.authorisation import hash_password, verify_password
from functionality.helpers import calc_average_rating, get_vouchers_unclaimed,validate_regex_phone, \
    validate_regex_password, validate_regex_email

from db.db_types.db_request import ReviewCreationRequest
from db.helpers.eatery import get_all_eateries, get_eatery_by_id, get_eatery_keywords_by_id, \
    update_eatery_email, update_eatery_name, update_eatery_phone, \
    update_eatery_manager_name, update_eatery_description, update_eatery_thumbnail, \
    get_eatery_current_password_by_id, get_eatery_old_passwords_by_id, update_eatery_password, \
    delete_all_eatery_keywords, add_eatery_keywords, update_eatery_menu, update_eatery_address, \
    get_eatery_by_email, get_eatery_by_phone_number
from db.helpers.voucher import get_voucher_by_id, get_vouchers_by_voucher_template
from db.helpers.voucher_instance import get_voucher_instances_by_status, get_voucher_instance_by_id, \
    get_voucher_instances_by_customer, get_voucher_instance_status, update_voucher_instance_review_status
from db.helpers.voucher_template import get_voucher_template_by_id, get_voucher_templates_by_eatery
from db.helpers.review import get_reviews_by_eatery, get_review_by_id, create_review
from db.helpers.customer import get_customer_by_id

from router.api_types.api_response import EateryInformationResponse, EateryVoucherResponse, HomePageResponse, HomePageEateryInformationResponse, \
    PublicEateryDetailsResponse, PrivateEateryDetailsResponse, EateryVoucherListResponse, AddressResponse, \
    ReviewDetailedResponse, EateryReviewListResponse, ReviewCreationResponse
from router.api_types.api_request import AddressCreateRequest, ReviewCreateRequest, Sorts

def list_eateries() -> HomePageResponse:
    """
    Gets a list of the public details for all Eateries
    """
    eatery_ids = get_all_eateries()
    if eatery_ids is None:
        raise ValidationError("Error retrieving eateries")

    eateries_sorted = basic_recommend_sort(eatery_ids)
    eateries = format_eatery_details(eateries_sorted)

    return HomePageResponse(
        eateries=eateries
    )

def recommend_eateries(customer_id: int, sorts: List[Sorts]) -> List[HomePageEateryInformationResponse]:
    """
    reccomends eateries
    """
    eatery_ids = get_all_eateries()
    if eatery_ids is None:
        raise ValidationError("Error retrieving eateries")
    eatery_ids = recommend_sort(customer_id, eatery_ids, sorts)
    eateries = format_eatery_details(eatery_ids)
    return eateries

def format_eatery_details(eatery_ids: List[int]) -> List[HomePageEateryInformationResponse]:
    """
    Formats a list of eateries for the homepage response
    """
    eateries: List[HomePageEateryInformationResponse] = []
    for eatery_id in eatery_ids:
        eatery = get_eatery_by_id(eatery_id)
        if eatery is None:
            raise ValidationError("Error retrieving eatery")
        vouchers = get_voucher_templates_by_eatery(eatery_id)
        if vouchers is None:
            raise ValidationError("Error retrieving vouchers")

        # gets top vouchers
        top_vouchers = top_3_vouchers(eatery_id)

        top_vouchers_tuples = []
        for vouch_id in top_vouchers:
            voucher = get_voucher_by_id(vouch_id)

            if voucher is None:
                raise ValidationError("Error retrieving voucher")

            voucher_template = get_voucher_template_by_id(voucher.voucher_template)

            if voucher_template is None:
                raise ValidationError("Error retrieving voucher template")

            top_vouchers_tuples.append((vouch_id, voucher_template.name))

        homepage_eatery = HomePageEateryInformationResponse(
            eatery_id=eatery_id,
            eatery_name=eatery.business_name,
            thumbnail_uri=eatery.thumbnail,
            num_vouchers=get_vouchers_unclaimed(vouchers),
            top_three_vouchers=top_vouchers_tuples,
            average_rating=calc_average_rating(eatery_id)
        )

        eateries.append(homepage_eatery)

    return eateries

def eatery_details(eatery_id: int, details_type: Literal["private", "public"]) -> Optional[Union[PublicEateryDetailsResponse, PrivateEateryDetailsResponse]]:
    """
    Gets an eatery's own full details (i.e Eatery's private details) or public details based on details_type specified
    """
    eatery = get_eatery_by_id(eatery_id)

    if eatery is None:
        raise ValidationError("Error retrieving eatery")

    eatery_keywords = get_eatery_keywords_by_id(eatery_id)
    assert eatery_keywords is not None

    if details_type == "public":
        return PublicEateryDetailsResponse(
            name=eatery.business_name,
            description=eatery.description,
            phone_number=eatery.phone,
            thumbnail_uri=eatery.thumbnail,
            menu_uri=eatery.menu,
            keywords=eatery_keywords,
            average_rating=calc_average_rating(eatery_id),
            address=AddressResponse(
                unit_number=eatery.address.unit_number,
                formatted_str=eatery.address.formatted_str,
            )
        )

    return PrivateEateryDetailsResponse(
        name=eatery.business_name,
        email=eatery.email,
        description=eatery.description,
        phone_number=eatery.phone,
        manager_first_name=eatery.manager_first_name,
        manager_last_name=eatery.manager_last_name,
        abn=eatery.abn,
        thumbnail_uri=eatery.thumbnail,
        menu_uri=eatery.menu,
        keywords=eatery_keywords,
        date_joined=eatery.date_joined,
        average_rating=calc_average_rating(eatery_id),
        address=AddressResponse(
            unit_number=eatery.address.unit_number,
            formatted_str=eatery.address.formatted_str,
        )
    )

def edit_eatery_profile(eatery_id: int, **kwargs):
    """
    Updates an eatery's details including thumbnail

    kwargs to check for:
     - email
     - phone_number
     - name
     - manager_first_name
     - manager_last_name
     - address
     - description
     - password
     - keywords
     - thumbnail_uri
     - menu_uri
    """
    eatery_info = get_eatery_by_id(eatery_id)

    def validate_email_logic(email: str):
        if not bool(email):
            raise ValidationError("Email must be a string")

        validate_regex_email(email)

    def update_email_logic(email: str):
        if eatery_info is not None and eatery_info.email != email.lower():
            if get_eatery_by_email(email) is not None:
                raise DuplicationError("Email already in use")

            update_eatery_email(eatery_id, email.lower())

    def validate_phone_logic(phone_number: str):
        if not bool(phone_number):
            raise ValidationError("Phone must be a string")

        validate_regex_phone(phone_number)

    def update_phone_logic(phone_number: str):
        if eatery_info is not None and eatery_info.phone != phone_number:
            if get_eatery_by_phone_number(phone_number) is not None:
                raise DuplicationError("Phone already in use")
            update_eatery_phone(eatery_id, phone_number)

    def validate_name_logic(name: str):
        if not bool(name):
            raise ValidationError("Eatery name must be a string")

    def update_name_logic(name: str):
        if eatery_info is not None and eatery_info.business_name != name:
            update_eatery_name(eatery_id, name)

    def validate_manager_first_name_logic(manager_first_name: str):
        if not bool(manager_first_name):
            raise ValidationError("Manager's first name must be not be empty")

    def update_manager_first_name_logic(manager_first_name: str):
        eatery = get_eatery_by_id(eatery_id)

        if eatery is None:
            raise ValidationError("Error retrieving eatery by id")

        if eatery.manager_first_name != manager_first_name:
            update_eatery_manager_name(eatery_id, manager_first_name, eatery.manager_last_name)

    def validate_manager_last_name_logic(manager_last_name: str):
        if not bool(manager_last_name):
            raise ValidationError("Manager's last name must not be empty")

    def update_manager_last_name_logic(manager_last_name: str):
        eatery = get_eatery_by_id(eatery_id)

        if eatery is None:
            raise ValidationError("Error retrieving eatery by id")

        if eatery.manager_last_name != manager_last_name:
            update_eatery_manager_name(eatery_id, eatery.manager_first_name, manager_last_name)

    def validate_address_logic(address: AddressCreateRequest):
        valid_address(address)

    def update_address_logic(address: AddressCreateRequest):
        update_eatery_address(eatery_id, valid_address(address))

    def validate_description_logic(description: str):
        if not isinstance(description, str):
            raise ValidationError("Description must be a string")

    def update_description_logic(description: str):
        if eatery_info is not None and eatery_info.description != description:
            update_eatery_description(eatery_id, description)

    def validate_password_logic(password: str):
        if not isinstance(password, str):
            raise ValidationError("Password must be a string")

        validate_regex_password(password)

        curr_password = get_eatery_current_password_by_id(eatery_id)
        if curr_password is None:
            raise ValidationError("Password could not be retrieved")
        if not verify_password(password, curr_password):
            past_passwords = get_eatery_old_passwords_by_id(eatery_id)
            if past_passwords is None:
                raise ValidationError("Error retrieving past passwords")
            if hash_password(password) in past_passwords:
                raise ValueError("Password is the same as a past password")

    def update_password_logic(password: str):
        update_eatery_password(eatery_id, hash_password(password), datetime.now(timezone.utc))

    def validate_thumbnail_uri_logic(thumbnail_uri: str):
        if not isinstance(thumbnail_uri, str):
            raise ValidationError("Thumbnail must be a string")

    def update_thumbnail_uri_logic(thumbnail_uri: str):
        if eatery_info is not None and eatery_info.thumbnail != thumbnail_uri:
            update_eatery_thumbnail(eatery_id, thumbnail_uri)

    def validate_keywords_logic(keywords: List[str]):
        if not isinstance(keywords, list) or not all(isinstance(keyword, str) for keyword in keywords):
            raise ValueError("Keywords must be a list of strings")

    def update_keywords_logic(keywords: List[str]):
        # Remove duplicate keywords by using a set
        keywords = list(set(keywords))

        delete_all_eatery_keywords(eatery_id)
        add_eatery_keywords(eatery_id, keywords)

    def validate_menu_uri_logic(menu_uri: str):
        if not isinstance(menu_uri, str):
            raise ValidationError("Thumbnail must be a string")

    def update_menu_uri_logic(menu_uri: str):
        if eatery_info is not None and eatery_info.menu != menu_uri:
            update_eatery_menu(eatery_id, menu_uri)

    # Perform all validations
    validation_mapping = {
        "email": validate_email_logic,
        "phone_number": validate_phone_logic,
        "name": validate_name_logic,
        "manager_first_name": validate_manager_first_name_logic,
        "manager_last_name": validate_manager_last_name_logic,
        "address": validate_address_logic,
        "description": validate_description_logic,
        "password": validate_password_logic,
        "keywords": validate_keywords_logic,
        "thumbnail_uri": validate_thumbnail_uri_logic,
        "menu_uri": validate_menu_uri_logic,
    }

    # Iterate through the mapping and apply validation functions as needed
    for key, validation_func in validation_mapping.items():
        if key in kwargs:
            validation_func(kwargs[key])

    # Perform all updations
    update_mapping = {
        "email": update_email_logic,
        "phone_number": update_phone_logic,
        "name": update_name_logic,
        "manager_first_name": update_manager_first_name_logic,
        "manager_last_name": update_manager_last_name_logic,
        "address": update_address_logic,
        "description": update_description_logic,
        "password": update_password_logic,
        "keywords": update_keywords_logic,
        "thumbnail_uri": update_thumbnail_uri_logic,
        "menu_uri": update_menu_uri_logic,
    }

    # Iterate through the mapping and apply updation functions as needed
    for key, update_func in update_mapping.items():
        if key in kwargs:
            update_func(kwargs[key])

def eatery_vouchers(eatery_id: int) -> EateryVoucherListResponse:
    """
    Gets a list of details for all Vouchers created by the eatery
    """
    all_vouchers = get_voucher_templates_by_eatery(eatery_id)

    if all_vouchers is None:
        raise ValidationError("Error retrieving eatery's vouchers")

    vouchers: List[EateryVoucherResponse] = []

    for voucher_template_id in all_vouchers:
        voucher_template = get_voucher_template_by_id(voucher_template_id)

        if voucher_template is None:
            raise ValidationError("Error retrieving voucher template")

        voucher_ids = get_vouchers_by_voucher_template(voucher_template_id)

        if voucher_ids is None:
            continue

        for voucher_id in voucher_ids:
            voucher = get_voucher_by_id(voucher_id)

            if voucher is None:
                raise ValidationError("Error retrieving voucher by id")

            unclaimed = get_voucher_instances_by_status(voucher_id, "unclaimed")

            if unclaimed is None:
                raise ValidationError("Error retrieving unclaimed voucher instances")

            vouchers.append(EateryVoucherResponse(
                voucher_id=voucher_id,
                name=voucher_template.name,
                description=voucher_template.description,
                conditions=voucher_template.conditions,
                total_quantity=voucher.quantity,
                unclaimed_quantity=len(unclaimed),
                expiry=voucher.expiry_date
            ))

    return EateryVoucherListResponse(
        vouchers=vouchers
    )

def get_voucher_details(voucher_instance_id: int):
    """
    Fetches voucher details
    """
    voucher_instance = get_voucher_instance_by_id(voucher_instance_id)
    if voucher_instance is None:
        raise ValidationError("Error retrieving voucher instance by id")

    voucher = get_voucher_by_id(voucher_instance.voucher)
    if voucher is None:
        raise ValidationError("Error retrieving voucher by id")

    voucher_template = get_voucher_template_by_id(voucher.voucher_template)
    if voucher_template is None:
        raise ValidationError("Error retrieving voucher template by id")

    return {
        "voucher_instance": voucher_instance,
        "voucher_template": voucher_template
    }

def eatery_reviews(eatery_id: int) -> EateryReviewListResponse:
    """
    Gets a list of details for all Vouchers created by the eatery
    """
    all_reviews = get_reviews_by_eatery(eatery_id)

    if all_reviews is None:
        raise ValidationError("Error retrieving eatery reviews")

    reviews: List[ReviewDetailedResponse] = []
    for review_id in all_reviews:
        # Get the details for each review

        review = get_review_by_id(review_id)
        if review is None:
            raise ValidationError("Error retrieving voucher by id")

        voucher_instance, voucher_template = get_voucher_details(review.voucher_instance).values()

        author = None
        if voucher_instance.customer and not review.anonymous:
            author = get_customer_by_id(voucher_instance.customer)
            if author is None:
                raise ValidationError("Error retrieving voucher by id")

        reviews.append(ReviewDetailedResponse(
            review_id=review_id,
            description=review.description,
            rating=review.rating,
            date_created=review.created,
            voucher_id=voucher_instance.voucher,
            voucher_name=voucher_template.name,
            voucher_instance_id=review.voucher_instance,
            author_id=voucher_instance.customer if author else None,
            author_name=f"{author.first_name} {author.last_name}" if author else None
        ))

    return EateryReviewListResponse(
        reviews=reviews
    )

def eatery_review_creation(eatery_id: int, customer_id: int, review: ReviewCreateRequest) -> ReviewCreationResponse:
    """
    Creates a review for a logged in customer who has claimed and redeemed a voucher but is yet to review
    """
    eatery = get_eatery_by_id(eatery_id)
    if eatery is None:
        raise ValidationError("Error retrieving eatery")

    voucher_instance, voucher_template = get_voucher_details(review.voucher_instance_id).values()

    if voucher_template.eatery != eatery_id:
        raise AuthorisationError("Voucher does not belong to the eatery")

    all_voucher_inst = get_voucher_instances_by_customer(customer_id)

    if not 0 <= review.rating <= 5:
        raise ValidationError("Rating must be between 0 to 5")

    if all_voucher_inst and review.voucher_instance_id in all_voucher_inst:
        status = get_voucher_instance_status(review.voucher_instance_id)
        if status == "redeemed":
            if not voucher_instance.reviewed:
                review_id = create_review(ReviewCreationRequest(
                    description=review.description,
                    rating=review.rating,
                    created=datetime.now(timezone.utc),
                    voucher_instance=review.voucher_instance_id,
                    anonymous=review.anonymous
                ))
            else:
                raise ValidationError("A voucher can only be reviewed once")
        else:
            raise ValidationError("Voucher should be redeemed before reviewing")
    else:
        raise ValidationError("Voucher should be claimed in order to review")

    if review_id is None:
        raise ValidationError("Could not create a review")

    update_voucher_instance_review_status(review.voucher_instance_id, True)

    return ReviewCreationResponse(
        review_id=review_id
    )

def get_eatery_information_responses() -> List[EateryInformationResponse]:
    """
    Gets a list of eatery information responses
    """
    responses = []

    eatery_ids = get_all_eateries()

    if eatery_ids is None:
        raise ValidationError("No eateries found")

    for eatery_id in eatery_ids:
        eatery = get_eatery_by_id(eatery_id)

        if eatery is None:
            continue

        vouchers = get_voucher_templates_by_eatery(eatery_id)

        if vouchers is None:
            continue

        top_vouchers: List[Tuple[int, str]] = []
        for vouch_id in vouchers[:3]:
            voucher = get_voucher_template_by_id(vouch_id)
            if voucher is None:
                continue
            top_vouchers.append((vouch_id, voucher.name))

        responses.append(EateryInformationResponse(
            eatery_id=eatery_id,
            eatery_name=eatery.business_name,
            thumbnail_uri=eatery.thumbnail,
            num_vouchers=get_vouchers_unclaimed(vouchers),
            top_three_vouchers=top_vouchers if len(top_vouchers) > 0 else [(1, "dummy 1"), (2, "dummy 2"), (3, "dummy 3")],
            average_rating=calc_average_rating(eatery_id)
        ))

    return responses
