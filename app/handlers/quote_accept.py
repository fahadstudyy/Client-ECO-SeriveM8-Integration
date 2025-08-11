import os
import logging
import requests
from app.handlers.job import get_job
from app.utility.hubspot import (
    find_hubspot_deal_by_job_uuid,
    update_hubspot_deal_stage,
)

SERVICEM8_API_KEY = os.getenv("SERVICEM8_API_KEY")
QUOTE_ACCEPTED_STAGE_ID = "1599473142"
POST_INSTALL_ADMIN_STAGE_ID = "1637640663"


def update_job_status_to_work_order(uuid):
    url = f"https://api.servicem8.com/api_1.0/job/{uuid}.json"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Api-Key": SERVICEM8_API_KEY,
    }
    payload = {"status": "Work Order"}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logging.info(f"Successfully updated job {uuid} to Work Order.")
        return response.json()
    except Exception as e:
        logging.error(f"Error updating job {uuid} to Work Order: {e}")
        return None


def handle_hubspot_job_quote_accepted(data):
    deal_id = data.get("deal_record_id")
    job_id = data.get("sm8_job_id")
    logging.info(f"Handling quote accepted for job: {job_id}")

    if not job_id or not deal_id:
        logging.error("Missing job_id or deal_id.")
        return

    sm8_job = get_job(job_id)
    sm8_job_status = sm8_job.get("status", "").strip().lower()

    if sm8_job_status == "work order":
        logging.info(f"Job {job_id} is already a Work Order. No action needed.")
        return

    update_job_status_to_work_order(job_id)


def handle_sm8_job_quote_accepted(job_uuid):
    sm8_job = get_job(job_uuid)
    sm8_job_status = sm8_job.get("status", "").strip().lower()

    if sm8_job_status != "work order":
        logging.error(f"Skipping {job_uuid}. Job Status is {sm8_job_status}")
        return

    deal_id = find_hubspot_deal_by_job_uuid(job_uuid)
    if not deal_id:
        logging.warning(f"No HubSpot deal found for job_id: {job_uuid}")
        return

    logging.info(f"Found deal {deal_id}, updating stage to Quote Accepted.")
    update_hubspot_deal_stage(deal_id, QUOTE_ACCEPTED_STAGE_ID)


def handle_sm8_job_completed(job_uuid):
    sm8_job = get_job(job_uuid)
    sm8_job_status = sm8_job.get("status", "").strip().lower()

    if sm8_job_status != "completed":
        logging.error(f"Skipping {job_uuid}. Job Status is {sm8_job_status}")
        return

    deal_id = find_hubspot_deal_by_job_uuid(job_uuid)
    if not deal_id:
        logging.warning(f"No HubSpot deal found for job_id: {job_uuid}")
        return

    logging.info(f"Found deal {deal_id}, updating stage to Post Install Admin.")
    update_hubspot_deal_stage(deal_id, POST_INSTALL_ADMIN_STAGE_ID)
