"""
Assumption: The application uses the CMS Nursing Home Provider dataset 
because the assignment references CMS star ratings, CCN lookup, and 
Medicare Care Compare nursing-home profile URLs.

We will have to query this datasets:
https://data.cms.gov/provider-data/dataset/4pq5-n9py
location (provider_name)
name of facility (provider_address)
census capacity (number_of_certified_beds)
overall star rating (overall_rating)
Health Inspection (health_inspection_rating)
Staffing (staffing_rating)
Quality of Resident Care (qm_rating)

hospitalization & ED (shortstay_qm_rating/longstay_qm_rating)

We will need manual input for:
EMR
current census
type of patient
medelite history (previous coverage from medelite)
medical coverage
Previous Provider Performance from Medelite
"""
import requests

class CMSAPIClient:
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
        # return self._record_cache
        
    def get_facility_name_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("provider_name")
        return None
    
    def get_facility_location_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("provider_address")
        return None
    
    def get_census_capacity_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("number_of_certified_beds")
        return None
    
    def get_overall_star_rating_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("overall_rating")
        return None
    
    def get_health_inspection_rating_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("health_inspection_rating")
        return None
    
    def get_staffing_rating_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("staffing_rating")
        return None
    
    def get_quality_of_resident_care_rating_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("qm_rating")
        return None