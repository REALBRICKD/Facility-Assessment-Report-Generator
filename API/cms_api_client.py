import requests

class CMS_API_Client:
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        self.base_url = f"https://data.cms.gov/provider-data/api/1/datastore/query/{self.dataset_id}/0"
        self._record_cache = {}
    
    def build_cache(self, ccn, limit):
        """
        We can rely on caching because we are returning all the relevant data at once
        Preconditions: ccn is non-empty
        """
        ccn_text = str(ccn).strip()
        query_body = {
            "conditions": [
                {"property": "cms_certification_number_ccn", "value": ccn_text, "operator": "="}
            ],
            "limit": limit,
            "offset": 0,
            "results": True,
            "count": False,
            "keys": True,
            "schema": False,
        }
        response = requests.post(self.base_url, json=query_body, timeout=30)
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results", [])
        self._record_cache = results[0] if results else {}
