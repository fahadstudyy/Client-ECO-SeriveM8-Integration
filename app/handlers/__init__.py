from .create_job import handle_create_job
from app.utility.webhook import handle_job_event
from .consult_visit import handle_consult_visit
from .pre_install import pre_installed_inspection
from .quote_accept import handle_hubspot_job_quote_accepted

webhook_handlers = {
    "JobActivity": handle_consult_visit,
    "Job": handle_job_event,
    "CreateJob": handle_create_job,
    "QuoteAccepted": handle_hubspot_job_quote_accepted,
    "preinstalled_inspection": pre_installed_inspection,
}
