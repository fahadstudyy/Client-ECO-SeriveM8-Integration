import os
import logging
from datetime import datetime
from app.handlers.consult_visit import get_job_activity
from app.utility.hubspot import (
    find_hubspot_deal_by_job_uuid,
    update_hubspot_deal,
    update_hubspot_deal_stage,
)

SERVICEM8_API_KEY = os.getenv("SERVICEM8_API_KEY")
JOB_SCHEDULE_PIPELINE_ID = "1637640662"


def handle_hubspot_job_scheduled(data):
    job_activity_uuid = data.get("job_activity_uuid")

    if not job_activity_uuid:
        logging.error("Missing job_activity_uuid in incoming request.")
        return

    job_activity = get_job_activity(job_activity_uuid)
    job_uuid = job_activity.get("job_uuid")
    if not job_activity:
        logging.error(f"Could not fetch JobActivity with uuid: {job_activity_uuid}")
        return

    start_date_str = job_activity.get("start_date")
    formatted_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S").strftime(
        "%Y-%m-%d"
    )

    deal_id = find_hubspot_deal_by_job_uuid(job_uuid)
    if deal_id:
        properties = {"pre_install_inspection_date": formatted_date}
        update_hubspot_deal(deal_id, properties)
        update_hubspot_deal_stage(deal_id, JOB_SCHEDULE_PIPELINE_ID)
    else:
        logging.warning(f"No HubSpot deal found with sm8_job_uuid = {job_uuid}")
