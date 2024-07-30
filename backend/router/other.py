import os
import requests
from fastapi import APIRouter, HTTPException, status
from router.api_types.api_request import AddressAutocompletionResponse

router = APIRouter()

GEOAPIFY_API_KEY = os.environ.get("GEOAPIFY_API_KEY")
USE_API_FOR_ADDRESS = os.environ.get("USE_API_FOR_ADDRESS_AUTOCOMPLETE")

@router.get("/autocomplete_address", status_code=status.HTTP_200_OK, response_model=AddressAutocompletionResponse)
async def autocomplete_address(query: str) -> AddressAutocompletionResponse:
    """
    Gives a list of autocomplete results for a given query string,
    using geoapify's address autocompletion API.

    query (str): The search query string to autocomplete
    """
    if len(query) == 0:
        return AddressAutocompletionResponse(results=[])

    if USE_API_FOR_ADDRESS is None or USE_API_FOR_ADDRESS == "False":
        return AddressAutocompletionResponse.model_validate(SAMPLE_DATA)


    try:
        res = requests.get(
            "https://api.geoapify.com/v1/geocode/autocomplete",
            params={
                "text": query,
                "lang": "en",
                "limit": 5,
                "type": "amenity",
                "format": "json",
                "apiKey": GEOAPIFY_API_KEY,
            },
            timeout=5
        ).json()
    except Exception as e:
        # assume that we got rate limitted or something else happened
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not generate a response"
        ) from e

    return AddressAutocompletionResponse.model_validate(res)

# pylint: disable=line-too-long
SAMPLE_DATA = {
    "results": [
        {
            "country_code": "au",
            "housenumber": "9",
            "street": "Ulm Street",
            "country": "Australia",
            "county": "Randwick",
            "datasource": {
                "sourcename": "openaddresses",
                "attribution": "© OpenAddresses contributors",
                "license": "BSD-3-Clause License"
            },
            "postcode": "2035",
            "state": "New South Wales",
            "district": "Maroubra",
            "city": "Maroubra",
            "state_code": "NSW",
            "lon": 151.228489,
            "lat": -33.944966,
            "result_type": "building",
            "formatted": "9 Ulm Street, Maroubra NSW 2035, Australia",
            "address_line1": "9 Ulm Street",
            "address_line2": "Maroubra NSW 2035, Australia",
            "timezone": {
                "name": "Australia/Sydney",
                "offset_STD": "+10:00",
                "offset_STD_seconds": 36000,
                "offset_DST": "+11:00",
                "offset_DST_seconds": 39600,
                "abbreviation_STD": "AEST",
                "abbreviation_DST": "AEDT"
            },
            "plus_code": "4RRH364H+29",
            "plus_code_short": "4H+29 Maroubra, Randwick, Australia",
            "rank": {
                "confidence": 1,
                "match_type": "full_match"
            },
            "place_id": "51ddcf29c84fe76240597dea58a5f4f840c0c00203e2034b6f70656e6164647265737365733a616464726573733a61752f636f756e747279776964652d6164647265737365732d636f756e7472792e6373763a35323234316461303565393234653237"
        },
        {
            "country_code": "au",
            "housenumber": "9",
            "street": "Ulm Street",
            "country": "Australia",
            "county": "Lane Cove",
            "datasource": {
                "sourcename": "openaddresses",
                "attribution": "© OpenAddresses contributors",
                "license": "BSD-3-Clause License"
            },
            "postcode": "2066",
            "state": "New South Wales",
            "district": "Lane Cove North",
            "city": "Lane Cove North",
            "state_code": "NSW",
            "lon": 151.156969,
            "lat": -33.802652,
            "result_type": "building",
            "formatted": "9 Ulm Street, Lane Cove North NSW 2066, Australia",
            "address_line1": "9 Ulm Street",
            "address_line2": "Lane Cove North NSW 2066, Australia",
            "timezone": {
                "name": "Australia/Sydney",
                "offset_STD": "+10:00",
                "offset_STD_seconds": 36000,
                "offset_DST": "+11:00",
                "offset_DST_seconds": 39600,
                "abbreviation_STD": "AEST",
                "abbreviation_DST": "AEDT"
            },
            "plus_code": "4RRH55W4+WQ",
            "plus_code_short": "W4+WQ Lane Cove North, Lane Cove, Australia",
            "rank": {
                "confidence": 1,
                "match_type": "full_match"
            },
            "place_id": "518c2fdae305e5624059d508fd4cbde640c0c00203e2034b6f70656e6164647265737365733a616464726573733a61752f636f756e747279776964652d6164647265737365732d636f756e7472792e6373763a36323630303234343935663633353464"
        },
        {
            "datasource": {
                "sourcename": "openstreetmap",
                "attribution": "© OpenStreetMap contributors",
                "license": "Open Database License",
                "url": "https://www.openstreetmap.org/copyright"
            },
            "name": "University of New South Wales",
            "country": "Australia",
            "country_code": "au",
            "state": "New South Wales",
            "city": "Sydney",
            "municipality": "Randwick City Council",
            "postcode": "2031",
            "district": "Eastern Suburbs",
            "suburb": "Randwick",
            "street": "Arthur Street",
            "lon": 151.23126487290787,
            "lat": -33.91759945,
            "state_code": "NSW",
            "result_type": "amenity",
            "formatted": "University of New South Wales, Arthur Street, Randwick NSW 2031, Australia",
            "address_line1": "University of New South Wales",
            "address_line2": "Arthur Street, Randwick NSW 2031, Australia",
            "category": "education.university",
            "timezone": {
                "name": "Australia/Sydney",
                "offset_STD": "+10:00",
                "offset_STD_seconds": 36000,
                "offset_DST": "+11:00",
                "offset_DST_seconds": 39600,
                "abbreviation_STD": "AEST",
                "abbreviation_DST": "AEDT"
            },
            "plus_code": "4RRH36JJ+XG",
            "plus_code_short": "36JJ+XG Sydney, New South Wales, Australia",
            "rank": {
                "importance": 0.6149041172901903,
                "confidence": 1,
                "confidence_city_level": 1,
                "match_type": "inner_part"
            },
            "place_id": "514b3b978566e7624059ee4916e673f540c0f00102f901b8dc570a00000000c0020192031d556e6976657273697479206f66204e657720536f7574682057616c6573"
        },
        {
            "datasource": {
                "sourcename": "openstreetmap",
                "attribution": "© OpenStreetMap contributors",
                "license": "Open Database License",
                "url": "https://www.openstreetmap.org/copyright"
            },
            "name": "University of New South Wales Randwick Campus",
            "country": "Australia",
            "country_code": "au",
            "state": "New South Wales",
            "city": "Sydney",
            "municipality": "Randwick City Council",
            "postcode": "2031",
            "district": "Eastern Suburbs",
            "suburb": "Randwick",
            "street": "John Street",
            "lon": 151.23465683738365,
            "lat": -33.9062434,
            "state_code": "NSW",
            "result_type": "amenity",
            "formatted": "University of New South Wales Randwick Campus, John Street, Randwick NSW 2031, Australia",
            "address_line1": "University of New South Wales Randwick Campus",
            "address_line2": "John Street, Randwick NSW 2031, Australia",
            "category": "education.university",
            "timezone": {
                "name": "Australia/Sydney",
                "offset_STD": "+10:00",
                "offset_STD_seconds": 36000,
                "offset_DST": "+11:00",
                "offset_DST_seconds": 39600,
                "abbreviation_STD": "AEST",
                "abbreviation_DST": "AEDT"
            },
            "plus_code": "4RRH36VM+GV",
            "plus_code_short": "36VM+GV Sydney, New South Wales, Australia",
            "rank": {
                "importance": 0.6149041172901903,
                "confidence": 1,
                "confidence_city_level": 1,
                "match_type": "inner_part"
            },
            "place_id": "510f4b0e4f82e7624059a19ba2c8fff340c0f00102f9012a026a2400000000c0020192032d556e6976657273697479206f66204e657720536f7574682057616c65732052616e647769636b2043616d707573"
        },
        {
            "datasource": {
                "sourcename": "openstreetmap",
                "attribution": "© OpenStreetMap contributors",
                "license": "Open Database License",
                "url": "https://www.openstreetmap.org/copyright"
            },
            "name": "University of New South Wales",
            "country": "Australia",
            "country_code": "au",
            "state": "New South Wales",
            "city": "Sydney",
            "municipality": "Randwick City Council",
            "postcode": "2033",
            "district": "Eastern Suburbs",
            "suburb": "Kensington",
            "street": "Anzac Parade",
            "lon": 151.2251677447594,
            "lat": -33.91701725,
            "state_code": "NSW",
            "result_type": "amenity",
            "formatted": "University of New South Wales, Anzac Parade, Kensington NSW 2033, Australia",
            "address_line1": "University of New South Wales",
            "address_line2": "Anzac Parade, Kensington NSW 2033, Australia",
            "category": "education.university",
            "timezone": {
                "name": "Australia/Sydney",
                "offset_STD": "+10:00",
                "offset_STD_seconds": 36000,
                "offset_DST": "+11:00",
                "offset_DST_seconds": 39600,
                "abbreviation_STD": "AEST",
                "abbreviation_DST": "AEDT"
            },
            "plus_code": "4RRH36MG+53",
            "plus_code_short": "36MG+53 Sydney, New South Wales, Australia",
            "rank": {
                "importance": 0.6149041172901903,
                "confidence": 1,
                "confidence_city_level": 1,
                "match_type": "inner_part"
            },
            "place_id": "51627bfc9234e7624059164f3dd260f540c0f00102f901dedeb70200000000c0020192031d556e6976657273697479206f66204e657720536f7574682057616c6573"
        },
    ],
    "query": {
        "text": 'Mosco',
        "parsed": {
        "city": 'mosco',
        "expected_type": 'unknown'
        }
    }
}
