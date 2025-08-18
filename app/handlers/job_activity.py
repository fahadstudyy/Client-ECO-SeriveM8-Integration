import logging
from datetime import datetime
from app.handlers.consult_visit import get_job_activity
from app.handlers.job_management import handle_job_management
from app.utility.hubspot import (
    find_hubspot_deal_by_job_uuid,
    get_hubspot_deal_properties,
    update_hubspot_deal,
    update_hubspot_deal_stage,
)

# HubSpot Deal Stage IDs provided by you
CONSULT_VISIT_STAGE_ID = "decisionmakerboughtin"
PRE_INSTALL_STAGE_ID = "1643946489"
READY_TO_SCHEDULE_STAGE_ID = "1637640661"

# The target stage ID for a scheduled job
JOB_SCHEDULED_PIPELINE_ID = "1637640662"

def handle_job_activity(data):
    """
    Acts as a sub-router for JobActivity webhooks.
    Checks the deal stage in HubSpot and performs the correct action.
    """
    entry = data.get("entry", [{}])[0]
    job_activity_uuid = entry.get("uuid")

    handle_job_management(job_activity_uuid)
    if not job_activity_uuid:
        return

    job_activity = get_job_activity(job_activity_uuid)
    if not job_activity or str(job_activity.get("activity_was_scheduled")) != "1":
        return

    job_uuid = job_activity.get("job_uuid")
    deal_id = find_hubspot_deal_by_job_uuid(job_uuid)
    
    if deal_id:
        properties = {"sm8_job_scheduled": job_activity_uuid}
        update_hubspot_deal(deal_id, properties)
    else:
        logging.warning(f"No HubSpot deal found for job_id: {job_uuid}")
        return

    properties = get_hubspot_deal_properties(deal_id, ["dealstage"])
    current_stage = (properties.get("dealstage") or "").lower()

    start_date_str = job_activity.get("start_date")
    if not start_date_str:
        return

    formatted_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

    if current_stage == CONSULT_VISIT_STAGE_ID:
        logging.info(f"Updating consult_visit_date for deal {deal_id}")
        update_hubspot_deal(deal_id, {"consult_visit_date": formatted_date})

    elif current_stage == PRE_INSTALL_STAGE_ID:
        logging.info(f"Updating pre_install_inspection_date for deal {deal_id}")
        update_hubspot_deal(deal_id, {"pre_install_inspection_date": formatted_date})
    else:
        logging.info(f"Ignoring JobActivity for deal {deal_id}: stage '{current_stage}' requires no action.")
