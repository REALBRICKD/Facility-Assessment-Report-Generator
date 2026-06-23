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