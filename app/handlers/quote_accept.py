import logging
from app.utility.hubspot import (
    find_hubspot_deal_by_job_uuid,
    update_hubspot_deal_stage,
)

QUOTE_ACCEPTED_STAGE_ID = "1599473142"

def handle_job_quote_accepted(data):
    """
    Finds a HubSpot deal by job_uuid and updates its stage to 'Quote Accepted'.
    """
    job_id = data.get("job_id")
    logging.info(f"Handling quote accepted for job: {job_id}")

    if not job_id:
        logging.error("Missing job_id")
        return

    deal_id = find_hubspot_deal_by_job_uuid(job_id)
    if not deal_id:
        logging.warning(f"No HubSpot deal found for job_id: {job_id}")
        return
        
    logging.info(f"Found deal {deal_id}, updating stage to Quote Accepted.")
    update_hubspot_deal_stage(deal_id, QUOTE_ACCEPTED_STAGE_ID)