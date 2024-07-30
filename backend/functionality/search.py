import asyncio
import os
import re
from typing import List, Set, Tuple
from openai import AsyncOpenAI

from logger import log_green

from functionality.errors import ValidationError
from functionality.helpers import calc_average_rating

from db.helpers.voucher_template import get_voucher_template_by_id, get_voucher_templates_by_eatery
from db.helpers.eatery import get_all_eateries, get_eatery_by_id, get_eatery_keywords_by_id

from router.api_types.api_response import EateryInformationResponse

# ChatGPT client use to assist with search functionality
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "NO_KEY")
)

async def search_eateries(query: str) -> List[EateryInformationResponse]:
    """
    Given a query, we want to return all the eateries that are related to the query
    """
    
    return await smart_search(query) if os.environ.get("SMART_SEARCH", "False") == "True" else dumb_search(query)

def dumb_search(query: str) -> List[EateryInformationResponse]:
    """
    Given a query, returns eateries that match the query
    """

    # Get all the eateries
    prompt_words = query.split() + [query]

    # Get all the eateries
    eatery_ids = get_all_eateries()

    if eatery_ids is None:
        raise ValidationError("No eateries found")

    matched_eateries: Set[int] = set()

    eatery_keywords = {}

    for eid in eatery_ids:
        eatery_keywords[eid] = get_eatery_keywords(eid)

        if eatery_keywords[eid] is None:
            continue

        for keyword in eatery_keywords[eid]:
            for prompt_word in prompt_words:
                if keyword.lower() == prompt_word.lower():
                    matched_eateries.add(eid)
                    break

        # Matches eatery name by intersecting words in query and eatery name
        eatery = get_eatery_by_id(eid)
        if eatery is None:
            continue
        eatery_name = eatery.business_name

        # also match full eatery name with whitespaces removed
        matched_eateries.update(match_eatery_name(eid, prompt_words, eatery_name))
    res = []

    for eid in matched_eateries:
        eatery_info = get_eatery_by_id(eid)

        if eatery_info is None:
            continue

        vouchers = get_voucher_templates_by_eatery(eid)

        if vouchers is None:
            continue

        top_vouchers: List[Tuple[int, str]] = []
        for vouch_id in vouchers[:3]:
            voucher = get_voucher_template_by_id(vouch_id)
            if voucher is None:
                continue
            top_vouchers.append((vouch_id, voucher.name))

        res.append(EateryInformationResponse(
            eatery_id=eid,
            eatery_name=eatery_info.business_name,
            thumbnail_uri=eatery_info.thumbnail,
            num_vouchers=len(vouchers),
            top_three_vouchers=top_vouchers,
            average_rating=calc_average_rating(eid)
        ))

    return res

async def smart_search(query: str) -> List[EateryInformationResponse]:
    """
    Given a query, breaks it down to determine the best eateries to return
    """
    prompt_words = query.split(" ") + [query]

    # Get all the eateries
    eatery_ids = get_all_eateries()

    if eatery_ids is None:
        raise ValidationError("No eateries found")

    scored_eateries = []

    eateries_keywords = get_each_eateries_keywords(eatery_ids)

    # Take all the keywords and turn them into a set
    # Use set to remove duplicates
    all_keywords = {keyword for keywords in eateries_keywords.values() for keyword in keywords}

    score_keywords = await score_all_keywords(prompt_words, list(all_keywords))

    for eid in eatery_ids:
        eatery_score = score_eatery(eateries_keywords[eid], score_keywords)

        # This implies high match to our query
        if eatery_score > 70:
            scored_eateries.append((eid, eatery_score))

    # Sort the eateries by score
    scored_eateries.sort(key=lambda x: x[1], reverse=True)

    res = []

    for eatery in scored_eateries:
        eid = eatery[0]

        eatery_info = get_eatery_by_id(eid)

        if eatery_info is None:
            continue

        vouchers = get_voucher_templates_by_eatery(eid)

        if vouchers is None:
            continue

        top_vouchers: List[Tuple[int, str]] = []
        for vouch_id in vouchers[:3]:
            voucher = get_voucher_template_by_id(vouch_id)
            if voucher is None:
                continue
            top_vouchers.append((vouch_id, voucher.name))

        res.append(EateryInformationResponse(
            eatery_id=eatery[0],
            eatery_name=eatery_info.business_name,
            thumbnail_uri=eatery_info.thumbnail,
            num_vouchers=len(vouchers),
            top_three_vouchers=top_vouchers,
            average_rating=calc_average_rating(eid)
        ))

    return res

def match_eatery_name(eid: int, prompt_words: List[str], eatery_name: str) -> Set[int]:
    """
    Given an eatery ID, a list of prompt words and the eatery name, we want to match the eatery name against the prompt words
    """
    eatery_name_words = eatery_name.split(
    ) + [re.sub(r'\s*', '', eatery_name)]

    matched_eateries: Set[int] = set()

    if any(re.match(prompt_word, eatery_name_word, re.IGNORECASE) for prompt_word in prompt_words for eatery_name_word in eatery_name_words):
        matched_eateries.add(eid)

    return matched_eateries

def get_each_eateries_keywords(eatery_ids: List[int]) -> dict[int, List[str]]:
    """
    Given a list of eatery IDs, we want to get the keywords for each eatery
    """
    res = {}

    for eid in eatery_ids:
        eatery_keywords = get_eatery_keywords(eid)

        if eatery_keywords is None:
            eatery_keywords = []

        res[eid] = eatery_keywords

    return res

def get_eatery_keywords(eid: int) -> List[str]:
    """
    Given an eatery ID, we want to get the keywords for the eatery
    """
    eatery_keywords = get_eatery_keywords_by_id(eid)

    if eatery_keywords is None:
        eatery_keywords = []

    # Add the eatery name and postcode to the keywords
    eatery_info = get_eatery_by_id(eid)

    if eatery_info is not None:
        eatery_keywords.append(eatery_info.business_name)
        eatery_keywords.append(eatery_info.address.postcode)

    return eatery_keywords

async def score_all_keywords(prompt_words: List[str], keywords: List[str]) -> dict[str, dict[str, int]]:
    """
    Given a list of prompt words and a list of keywords, we want to score each keyword against each prompt word

    Returns a dictionary of keyword -> dict(prompt word -> score)
    """
    res = {}

    for prompt_word in prompt_words:
        # Get the score of how this prompt word compares to the keywords
        prompt_keyword_map = await score_prompt_word_against_keywords(prompt_word, keywords)

        res[prompt_word] = prompt_keyword_map

    # Res is currently a dict of prompt word -> dict(keyword -> score)
    # We want to convert to dict of keyword -> dict(prompt word -> score)

    output = {}

    for keyword in keywords:
        output[keyword] = {}

        for prompt_word in prompt_words:
            output[keyword][prompt_word] = res[prompt_word].get(keyword, 0)

    return output

def score_eatery(eatery_keywords: list[str], keyword_score: dict[str, dict[str, int]]) -> int:
    """
    Given an eatery ID and a list of prompt words, we want to score the eatery against the prompt words
    """
    if len(eatery_keywords) == 0:
        return 0

    res = []

    # Get all the scores of each keyword against each prompt
    for keyword in eatery_keywords:
        keyword_prompt_map = keyword_score.get(keyword, {})

        if len(keyword_prompt_map) == 0:
            continue

        # Get the score from the map
        for score in keyword_prompt_map.values():
            res.append(score)

    # There are different scoring strategies we can use
    # For now, we will take the max score
    # Average is also a posibility
    return max(res) if len(res) > 0 else 0

def _score_gpt_result(result: str) -> int:
    """
    Given a GPT result, we want to score it
    """
    # Extract the score from the result
    regex_res = re.findall(r"\d+", result)

    if len(regex_res) == 0:
        return 0

    res = int(regex_res[0])

    # Cap out at 100
    return 100 if res > 100 else res
    
async def score_prompt_word_against_keywords(prompt_word: str, keywords: List[str]) -> dict[str, int]:
    """
    Given a prompt word and a list of keywords, we want to score the prompt word against the keywords

    We will return a dictionary of keyword -> score
    """
    semaphore = asyncio.Semaphore(value=10)

    res = await asyncio.gather(*[_score_keyword_against_prompt_word(keyword, prompt_word, semaphore) for keyword in keywords])

    output = dict(zip(keywords, res))

    return output

def _get_postcode_score(postcode1: int, postcode2: int):
    """
    Given 2 post codes, compare their location

    We detect similarity by the difference between the postcodes
    """

    return 0 if abs(postcode1 - postcode2) > 3 else 100

async def _score_keyword_against_prompt_word(keyword: str, prompt_word: str, semaphore) -> int:
    """
    Given a keyword and a prompt word, we want to score the keyword against the prompt word
    """
    if keyword == prompt_word:
        return 100
    
    # If we're dealing with a number, we need to match up directly otherwise 0
    # This assumes postcode
    if prompt_word.isnumeric():
        return _get_postcode_score(int(keyword), int(prompt_word)) if keyword.isnumeric() else 0

    async with semaphore:
        # Run the prompt against ChatGPT and get a score
        resp = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are to assist in the relatedness of words. You will be given a keyword \
                    and a prompt and you much determine a score between them. For example, if keyword=mexican \
                    and prompt=taco, the score might be 90%. However if keyword=burger and prompt=taco, the \
                    score might be 5%. I only want you to give a number solution. No words what so ever."},
                {
                    "role": "user",
                    "content": f"keyword={keyword} prompt={prompt_word}"
                }
            ],
            model="gpt-3.5-turbo",
        )

        result = resp.choices[0].message.content

        log_green(f"GPT: Scored {keyword} against {prompt_word} with result {result}")

        return 0 if result is None else _score_gpt_result(result)
