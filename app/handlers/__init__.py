from .job import handle_job_quote_sent
from .consult_visit import handle_consult_visit
from .create_job import handle_create_job
from .quote_accept import handle_job_quote_accepted

webhook_handlers = {
    "JobActivity": handle_consult_visit,
    "Job": handle_job_quote_sent,
    "CreateJob": handle_create_job,
    "QuoteSent": handle_job_quote_sent,
    "QuoteAccepted": handle_job_quote_accepted,
}
