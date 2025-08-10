import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from app.utility.hubspot import find_hubspot_deal_by_job_uuid, update_hubspot_deal


load_dotenv()

SERVICEM8_API_KEY = os.getenv("SERVICEM8_API_KEY")
HUBSPOT_API_TOKEN = os.getenv("HUBSPOT_API_TOKEN")


def get_job_activity(uuid):
    url = f"https://api.servicem8.com/api_1.0/jobactivity/{uuid}.json"
    headers = {"accept": "application/json", "X-Api-Key": SERVICEM8_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching job activity: {e}")
        return None


def handle_consult_visit(data):
    job_activity_uuid = data.get("job_activity_uuid")
    if not job_activity_uuid:
        logging.error("No job_activity_uuid provided in data.")
        return

    job_activity = get_job_activity(job_activity_uuid)
    if not job_activity:
        logging.error(f"Could not fetch JobActivity with uuid: {job_activity_uuid}")
        return

    if str(job_activity.get("activity_was_scheduled")) == "1":
        job_uuid = job_activity.get("job_uuid")
        if not job_uuid:
            logging.error("No job_uuid in JobActivity.")
            return

        start_date_str = job_activity.get("start_date")
        consult_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S").strftime(
            "%Y-%m-%d"
        )
        properties = {"consult_visit_date": consult_date}

        deal_id = find_hubspot_deal_by_job_uuid(job_uuid)
        if deal_id:
            update_hubspot_deal(deal_id, properties)
        else:
            logging.warning(f"No HubSpot deal found with sm8_job_uuid = {job_uuid}")
