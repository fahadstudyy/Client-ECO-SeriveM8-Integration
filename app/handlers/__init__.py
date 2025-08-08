from .job_activity import handle_job_activity
from .job import handle_job_quote_sent
from .consult_visit import handle_consult_visit
from .create_job import handle_create_job
from .quote_accept import handle_job_quote_accepted

webhook_handlers = {
    "JobActivity": handle_job_activity,
    "Job": handle_job_quote_sent,
    "CreateJob": handle_create_job,
    "ConsultVisit": handle_consult_visit,
    "QuoteSent": handle_job_quote_sent,
    "QuoteAccepted": handle_job_quote_accepted,
}
