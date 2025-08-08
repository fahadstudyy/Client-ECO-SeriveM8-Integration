import os
import logging
import requests
from datetime import datetime
from app.utility.hubspot import update_hubspot_deal
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
    job_id = data.get("job_id")
    deal_id = data.get("deal_record_id")
    logging.info(f"Handling job update for job_id: {job_id}")

    if not deal_id or not job_id:
        logging.error("Missing deal_id or job_id")
        return

    job = get_job(job_id)
    if not job:
        logging.error(f"Failed to fetch job: {job_id}")
        return

    properties_to_update = {}

    total_amount = job.get("total_invoice_amount")
    if total_amount:
        properties_to_update["amount"] = total_amount

    quote_date_str = job.get("quote_date")
    if quote_date_str and quote_date_str != "0000-00-00 00:00:00":
        try:
            formatted_date = datetime.strptime(quote_date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            properties_to_update["quote_date"] = formatted_date
        except ValueError:
             logging.warning(f"Invalid quote_date format for job {job_id}")

    if properties_to_update:
        logging.info(f"Updating deal {deal_id}")
        update_hubspot_deal(deal_id, properties_to_update)
    else:
        logging.warning(f"No data to update for job {job_id}")