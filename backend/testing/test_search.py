import json

from testing.test_helpers import register_eatery, search, update_eatery_details

with open("testing/test_data.json", encoding="utf8") as file:
    test_data = json.load(file)

register_data = test_data["register_data"]

class TestSearch:
    def test_dumb_search(self, reset_db):
        """
        Uses a dumb search
        """
        # Create an eatery
        eatery1_data = register_data["eatery"]["1"]
        _, access_token_1, eid1 = register_eatery(eatery1_data).values()

        # Assign keyword mexican
        res = update_eatery_details(eid1, {"Authorization": "bearer " + access_token_1}, {"keywords": ["mexican"]})
        assert res.status_code == 200

        # Create an eatery
        eatery2_data = register_data["eatery"]["2"]
        _, access_token_2, eid2 = register_eatery(eatery2_data).values()

        # Assign keyword burger
        res = update_eatery_details(eid2, {"Authorization": "bearer " + access_token_2}, {"keywords": ["burger"]})
        assert res.status_code == 200

        # Search for eateries
        res = search("mexican")
        assert res.status_code == 200

        # Check that we get the correct eateries
        eateries = res.json()["eateries"]

        assert len(eateries) == 1

        assert eateries[0]["eatery_id"] == eid1
        assert eateries[0]["eatery_name"] == eatery1_data["business_name"]
