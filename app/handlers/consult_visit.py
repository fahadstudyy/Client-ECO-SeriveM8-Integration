import os
import logging
import requests
from datetime import datetime
from app.utility.hubspot import update_hubspot_deal

SERVICEM8_API_KEY = os.getenv("SERVICEM8_API_KEY")

def get_servicem8_activities_for_job(job_uuid):
    """
    Fetches ALL job activities from ServiceM8 and then filters them in Python
    to find the one matching the given job_uuid.
    """
    url = "https://api.servicem8.com/api_1.0/jobactivity.json"  # URL without the filter
    headers = {"X-Api-Key": SERVICEM8_API_KEY, "accept": "application/json"}
    
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        all_activities = resp.json()
        logging.info(f"Successfully fetched {len(all_activities)} total activities from ServiceM8.")

        # Filter the full list in Python to find the matching activity
        matching_activities = [
            activity for activity in all_activities if activity.get("job_uuid") == job_uuid
        ]
        
        return matching_activities

    except Exception as e:
        logging.error(f"Error fetching all ServiceM8 activities: {e}")
        return None

def handle_consult_visit(visit_data):
    """
    Handles consult visit webhook: gets activity start date from ServiceM8 
    and updates the HubSpot deal using the utility function.
    """
    logging.info(f"Handling consult visit: {visit_data}")
    
    deal_id = visit_data.get("deal_record_id")
    job_id = visit_data.get("job_id")

    if not deal_id or not job_id:
        logging.error("Missing 'deal_record_id' or 'job_id' in visit data.")
        return

    # This function now returns a Python-filtered list
    activities = get_servicem8_activities_for_job(job_id)

    # The rest of the logic remains the same
    if activities is None: # Handles API failure
        logging.error("Failed to fetch activities from ServiceM8.")
        return

    if not activities: # Handles case where no match was found
        logging.warning(f"No matching activity found for job_uuid: {job_id}")
        return

    start_date_str = activities[0].get("start_date")
    if not start_date_str:
        logging.error(f"No 'start_date' in activity for job: {job_id}")
        return

    try:
        consult_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        properties = {"consult_visit_date": consult_date}
        
        update_hubspot_deal(deal_id, properties)

    except ValueError as e:
        logging.error(f"Could not parse date '{start_date_str}'. Error: {e}")
        return