import os
import logging
import requests
from datetime import date

SERVICEM8_API_KEY = os.getenv("SERVICEM8_API_KEY")
HUBSPOT_API_TOKEN = os.getenv("HUBSPOT_API_TOKEN")


def fetch_hubspot_contact_sm8_client_id(contact_id):
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    params = {"properties": "sm8_client_id"}
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        properties = resp.json().get("properties", {})
        sm8_client_id = properties.get("sm8_client_id")
        logging.info(f"Fetched sm8_client_id for contact {contact_id}: {sm8_client_id}")
        return sm8_client_id
    except Exception as e:
        logging.error(f"Error fetching HubSpot contact {contact_id} sm8_client_id: {e}")
        return None


def update_hubspot_contact_sm8_client_id(contact_id, client_uuid):
    url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"properties": {"sm8_client_id": client_uuid}}

    try:
        resp = requests.patch(url, json=data, headers=headers)
        resp.raise_for_status()
        logging.info(
            f"Updated HubSpot contact {contact_id} with sm8_client_id: {client_uuid}"
        )
        return True
    except Exception as e:
        logging.error(f"Error updating HubSpot contact {contact_id}: {e}")
        return False


def create_servicem8_client(full_name):
    url = "https://api.servicem8.com/api_1.0/company.json"
    headers = {"X-Api-Key": SERVICEM8_API_KEY, "Content-Type": "application/json"}
    payload = {"name": full_name}

    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        client_uuid = resp.headers.get("x-record-uuid")
        logging.info(f"Created ServiceM8 client UUID: {client_uuid}")
        return client_uuid
    except Exception as e:
        logging.error(f"Error creating ServiceM8 client: {e}")
        return None


def create_servicem8_job(job_data, client_uuid):
    url = "https://api.servicem8.com/api_1.0/job.json"
    headers = {"X-Api-Key": SERVICEM8_API_KEY, "Content-Type": "application/json"}
    job_data["company_uuid"] = client_uuid

    try:
        resp = requests.post(url, json=job_data, headers=headers)
        resp.raise_for_status()
        job_uuid = resp.headers.get("x-record-uuid")
        logging.info(f"Created ServiceM8 Job UUID: {job_uuid}")
        return job_uuid
    except Exception as e:
        logging.error(f"Error creating ServiceM8 job: {e}")
        return None


def create_servicem8_job_contact(job_uuid, contact):
    url = "https://api.servicem8.com/api_1.0/jobcontact.json"
    headers = {"X-Api-Key": SERVICEM8_API_KEY, "Content-Type": "application/json"}
    contact_payload = {
        "job_uuid": job_uuid,
        "first": contact.get("firstname"),
        "last": contact.get("lastname"),
        "phone": contact.get("phone"),
        "email": contact.get("email"),
        "type": "JOB",
        "is_primary_contact": 1,
    }
    try:
        resp = requests.post(url, json=contact_payload, headers=headers)
        resp.raise_for_status()
        logging.info(f"Created JobContact for job: {job_uuid}")
        return True
    except Exception as e:
        logging.error(f"Error creating JobContact: {e}")
        return False


def update_hubspot_deal_sm8_job_id(deal_id, job_uuid):
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"properties": {"sm8_job_id": job_uuid}}
    try:
        resp = requests.patch(url, json=data, headers=headers)
        resp.raise_for_status()
        logging.info(f"Updated HubSpot deal {deal_id} with sm8_job_id: {job_uuid}")
        return True
    except Exception as e:
        logging.error(f"Error updating HubSpot deal {deal_id}: {e}")
        return False


def fetch_hubspot_deal_properties(deal_id):
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    params = {
        "properties": "contact_email,contact_first_name,contact_last_name,contact_phone_number,enquiry_notes,service_category,contact_record_id"
    }
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        deal_properties = resp.json().get("properties", {})
        logging.info(f"Fetched HubSpot deal {deal_id} properties: {deal_properties}")
        return deal_properties
    except Exception as e:
        logging.error(f"Error fetching HubSpot deal {deal_id}: {e}")
        return None


def format_value(label, value):
    items = [item.strip() for item in value.split(";") if item.strip()]
    return f"{label}: {', '.join(items)}" if items else f"{label}:"


def handle_create_job(event_data):
    deal_id = event_data.get("deal_record_id")
    deal_properties = fetch_hubspot_deal_properties(deal_id)
    if not deal_properties:
        return

    contact_record_id = deal_properties.get("contact_record_id", "")

    # Check if contact already has an sm8_client_id
    client_uuid = None
    if contact_record_id:
        client_uuid = fetch_hubspot_contact_sm8_client_id(contact_record_id)

    # If not found, create a new client in ServiceM8
    if not client_uuid:
        first = deal_properties.get("contact_first_name", "")
        last = deal_properties.get("contact_last_name", "")
        full_name = f"{first} {last}".strip()
        client_uuid = create_servicem8_client(full_name)
        if not client_uuid:
            return

        # Save the new client UUID back to HubSpot
        if contact_record_id:
            update_hubspot_contact_sm8_client_id(contact_record_id, client_uuid)

    # Step 2: Create job
    service_category = deal_properties.get("service_category", "")
    enquiry_notes = deal_properties.get("enquiry_notes", "")
    job_description = (
        f"{format_value('Service Category', service_category)}\n"
        f"Enquiry Notes: {enquiry_notes.strip()}"
    )
    job_data = {
        "job_description": job_description,
        "status": "Quote",
        "date": str(date.today()),
    }
    job_uuid = create_servicem8_job(job_data, client_uuid)
    if not job_uuid:
        return
    print(f"Created job in sm8 with UUID: {job_uuid}")

    # Step 3: Create job contact
    contact = {
        "firstname": deal_properties.get("contact_first_name"),
        "lastname": deal_properties.get("contact_last_name"),
        "phone": deal_properties.get("contact_phone_number"),
        "email": deal_properties.get("contact_email"),
    }
    create_servicem8_job_contact(job_uuid, contact)

    # Step 4: Update HubSpot deal
    if deal_id:
        update_hubspot_deal_sm8_job_id(deal_id, job_uuid)
