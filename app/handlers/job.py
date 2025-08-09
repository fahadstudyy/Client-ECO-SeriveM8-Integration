import os
import logging
import requests
from datetime import datetime
from app.utility.hubspot import (
    find_hubspot_deal_by_job_uuid,
    update_hubspot_deal,
    update_hubspot_deal_stage,
    QUOTE_SENT_PIPELINE_ID,
)
from dotenv import load_dotenv

load_dotenv()

SERVICEM8_API_KEY = os.getenv("SERVICEM8_API_KEY")

def get_job(uuid):
    """Fetches a single job from ServiceM8 by its UUID."""
    url = f"https://api.servicem8.com/api_1.0/job/{uuid}.json"
    headers = {"accept": "application/json", "X-Api-Key": SERVICEM8_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching job {uuid}: {e}")
        return None

def handle_job_quote_sent(data):
    """
    Fetches job details from ServiceM8 and updates the amount and quote date
    on the corresponding HubSpot deal.
    """
    entry = data.get("entry", [{}])[0]
    job_uuid = entry.get("uuid")
    if not job_uuid:
        logging.error("No uuid in Job entry.")
        return

    logging.info(f"Handling job update for job_id: {job_uuid}")

    job = get_job(job_uuid)
    if not job:
        logging.error(f"Failed to fetch job: {job_uuid}")
        return

    properties_to_update = {}

    total_amount = job.get("total_invoice_amount")
    print(f"Total amount for job {job_uuid}: {total_amount}")

    if total_amount:
        properties_to_update["amount"] = total_amount

    quote_date_str = job.get("quote_date")
    print(f"Quote date for job {job_uuid}: {quote_date_str}")

    if quote_date_str and quote_date_str != "0000-00-00 00:00:00":
        try:
            formatted_date = datetime.strptime(quote_date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            properties_to_update["quote_date"] = formatted_date
        except ValueError:
            logging.warning(f"Invalid quote_date format for job {job_uuid}")

    if properties_to_update:
        deal_id = find_hubspot_deal_by_job_uuid(job_uuid)
        logging.info(f"Updating deal {deal_id}")
        update_hubspot_deal(deal_id, properties_to_update)
        update_hubspot_deal_stage(deal_id, QUOTE_SENT_PIPELINE_ID)
    else:
        logging.warning(f"No data to update for job {job_uuid}")
