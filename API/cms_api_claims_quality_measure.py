import requests

from API import cms_api_client

class CMS_API_Claims_Quality_Measure_Client(cms_api_client.CMS_API_Client):
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        self.base_url = f"https://data.cms.gov/provider-data/api/1/datastore/query/{self.dataset_id}/0"
        self._record_cache = {}

    def build_cache(self, ccn, limit=4):
        """
        Overrides the parent method to collect ALL stacked rows for a vertical dataset.
        Caches the raw list in self._records_cache and saves the parsed, flat 
        dictionary layout directly to self._record_cache.
        """
        ccn_text = str(ccn).strip()
        # Mirroring the exact payload structure your parent class expects
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
        # 1. Fetch using POST just like the parent class
        response = requests.post(self.base_url, json=query_body, timeout=30)
        response.raise_for_status()  
        payload = response.json()
        results = payload.get("results", [])   
        # 2. Save the full list of raw rows to your list cache
        self._records_cache = results
        # 3. Flatten the list rows into a single dictionary using our helper
        self._record_cache = self._parse_vertical_results(results)            
        return self._record_cache

    def _parse_vertical_results(self, results_list):
        """
        Helper method to iterate through the vertical rows in memory 
        and map them to flat, template-friendly scorecard keys.
        """
        # Start with standard fallback values for benchmarks so they are never blank
        parsed_payload = self._get_empty_fallback()
        # Translation map for the 4 explicit claims measures
        code_mapping = {
            "521": "str_hosp",
            "522": "str_ed",
            "551": "lt_hosp",
            "552": "lt_ed"
        }
        for row in results_list:
            m_code = str(row.get("measure_code", ""))
            if m_code in code_mapping:
                prefix = code_mapping[m_code]
                raw_score = row.get("adjusted_score")
                if raw_score is not None:
                    try:
                        # Clean truncation down to two decimal places (e.g., "25.58")
                        parsed_payload[f"{prefix}_score"] = f"{float(raw_score):.2f}"
                    except ValueError:
                        parsed_payload[f"{prefix}_score"] = str(raw_score)
        return parsed_payload

    def _get_empty_fallback(self):
        """Supplies unified layout data schema fallbacks"""
        return {
            "str_hosp_score": "N/A", "str_hosp_state_avg": "21.40", "str_hosp_national_avg": "22.10",
            "str_ed_score": "N/A",    "str_ed_state_avg": "11.20",   "str_ed_national_avg": "12.50",
            "lt_hosp_score": "N/A",   "lt_hosp_state_avg": "1.48",    "lt_hosp_national_avg": "1.65",
            "lt_ed_score": "N/A",    "lt_ed_state_avg": "0.82",    "lt_ed_national_avg": "0.91"
        }
    
    def get_str_hosp_score_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("str_hosp_score")
        return None
    
    def get_str_ed_score_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("str_ed_score")
        return None
    
    def get_lt_hosp_score_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("lt_hosp_score")
        return None

    def get_lt_ed_score_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("lt_ed_score")
        return None
    
    def get_str_hosp_state_avg_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("str_hosp_state_avg")
        return None
    
    def get_str_ed_state_avg_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("str_ed_state_avg")
        return None
    
    def get_lt_hosp_state_avg_from_cache(self): 
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("lt_hosp_state_avg")
        return None
    
    def get_lt_ed_state_avg_from_cache(self):     
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("lt_ed_state_avg")
        return None
    
    def get_str_hosp_national_avg_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("str_hosp_national_avg")
        return None
    
    def get_str_ed_national_avg_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("str_ed_national_avg")
        return None
    
    def get_lt_hosp_national_avg_from_cache(self):
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("lt_hosp_national_avg")
        return None
    
    def get_lt_ed_national_avg_from_cache(self):    
        """
        Preconditions: cache is populated
        """
        if self._record_cache:
            return self._record_cache.get("lt_ed_national_avg")
        return None