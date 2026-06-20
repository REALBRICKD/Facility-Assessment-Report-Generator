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

We will need manual input for:
EMR
current census
type of patient
medelite history (previous coverage from medelite)
medical coverage
Previous Provider Performance from Medelite

For the bonus, we query from this dataset:
https://data.cms.gov/provider-data/dataset/ijh5-nb2v
"""
from API import cms_api_client

class CMS_Provider_Info_Client(cms_api_client.CMS_API_Client):
    def __init__(self, dataset_id):
        super().__init__(dataset_id)
        
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

    def get_city_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("citytown")
        return None

    def get_state_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("state")
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