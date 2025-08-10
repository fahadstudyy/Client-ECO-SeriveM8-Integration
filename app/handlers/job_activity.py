import logging
from app.handlers.consult_visit import get_job_activity
from app.utility.hubspot import find_hubspot_deal_by_job_uuid, update_hubspot_deal


def handle_job_activity(data):
    entry = data.get("entry", [{}])[0]
    job_activity_uuid = entry.get("uuid")

    job_activity = get_job_activity(job_activity_uuid)
    if str(job_activity.get("activity_was_scheduled")) == "1":
        job_uuid = job_activity.get("job_uuid")
        if not job_uuid:
            logging.error("No job_uuid in JobActivity.")
            return

        deal_id = find_hubspot_deal_by_job_uuid(job_uuid)
        if deal_id:
            properties = {"sm8_job_scheduled": job_activity_uuid}
            update_hubspot_deal(deal_id, properties)
        else:
            logging.warning(f"No HubSpot deal found with sm8_job_uuid = {job_uuid}")
