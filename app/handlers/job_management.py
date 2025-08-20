import logging
from datetime import datetime
from app.handlers.consult_visit import get_job_activity
from app.utility.hubspot import (
    find_hubspot_deal_by_job_uuid,
    get_associated_deal_ids,
    get_hubspot_deal_properties,
    update_hubspot_deal,
    update_hubspot_deal_stage,
)

READY_TO_SCHEDULE_STAGE_ID = "1637640661"
JOB_SCHEDULED_PIPELINE_ID = "1637640662"


def handle_job_management(job_activity_uuid):
    if not job_activity_uuid:
        return

    job_activity = get_job_activity(job_activity_uuid)
    if not job_activity or str(job_activity.get("activity_was_scheduled")) != "1":
        return

    job_uuid = job_activity.get("job_uuid")
    deal_id = find_hubspot_deal_by_job_uuid(job_uuid)

    if not deal_id:
        logging.warning(f"No HubSpot deal found for job_id: {job_uuid}")
        return

    associated_deal_ids = get_associated_deal_ids(deal_id)
    if associated_deal_ids:
        first_associated_deal_id = associated_deal_ids[0]
        properties = {"sm8_job_scheduled": job_activity_uuid}
        update_hubspot_deal(first_associated_deal_id, properties)
        print(f"First associated deal ID: {first_associated_deal_id}")
    else:
        print("No associated deals found.")
        return

    properties = get_hubspot_deal_properties(first_associated_deal_id, ["dealstage"])
    current_stage = (properties.get("dealstage") or "").lower()

    start_date_str = job_activity.get("start_date")
    if not start_date_str:
        return

    formatted_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S").strftime(
        "%Y-%m-%d"
    )

    if current_stage == READY_TO_SCHEDULE_STAGE_ID:
        logging.info(f"Updating deal {first_associated_deal_id} to Job Scheduled stage")
        update_hubspot_deal(
            first_associated_deal_id,
            {"job_date": formatted_date},
        )
        update_hubspot_deal_stage(first_associated_deal_id, JOB_SCHEDULED_PIPELINE_ID)

    else:
        logging.info(
            f"Ignoring JobActivity for deal {deal_id}: stage '{current_stage}' requires no action."
        )
