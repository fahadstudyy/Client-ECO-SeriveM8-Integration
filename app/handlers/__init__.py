from .create_job import handle_create_job
from .job_activity import handle_job_activity
from .consult_visit import handle_consult_visit
from app.utility.webhook import handle_job_event
from .pre_install import handle_pre_install_inspection
from .quote_accept import handle_hubspot_job_quote_accepted

webhook_handlers = {
    "JobActivity": handle_job_activity,
    "Job": handle_job_event,
    "CreateJob": handle_create_job,
    "ConsultVisit": handle_consult_visit,
    "QuoteAccepted": handle_hubspot_job_quote_accepted,
    "PreInstalledInspection": handle_pre_install_inspection,
}
