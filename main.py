from API.cms_api_client import CMSAPIClient

if __name__ == "__main__":
    dataset_id = "4pq5-n9py"
    client = CMSAPIClient(dataset_id)
    client.build_cache(ccn = 686123, limit=1)
    print(client.get_facility_name_from_cache())
    print(client.get_facility_location_from_cache())
    print(client.get_census_capacity_from_cache())
    print(client.get_overall_star_rating_from_cache())
    print(client.get_health_inspection_rating_from_cache())
    print(client.get_staffing_rating_from_cache())
    print(client.get_quality_of_resident_care_rating_from_cache())
