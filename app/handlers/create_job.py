from datetime import date

from app.utility.create_job import (
    fetch_hubspot_contact_sm8_client_id,
    update_hubspot_contact_sm8_client_id,
    update_hubspot_deal_sm8_job_id,
    fetch_hubspot_deal_properties,
    create_servicem8_job_contact,
    get_servicem8_categories,
    create_servicem8_client,
    create_servicem8_job,
    format_value,
)


def handle_create_job(event_data):
    deal_id = event_data.get("deal_record_id")
    deal_properties = fetch_hubspot_deal_properties(deal_id)
    if not deal_properties:
        return

    sm8_job_id = deal_properties.get("sm8_job_id")
    quote_platform = deal_properties.get("quote_platform", "").lower()

    if quote_platform != "servicem8":
        print(f"Quote platform is not ServiceM8: {quote_platform}")
        return

    if sm8_job_id:
        print(f"Job already exists in ServiceM8 with ID: {sm8_job_id}")
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
    service_category = deal_properties.get("service_category") or ""
    enquiry_notes = deal_properties.get("enquiry_notes") or ""

    sm8_service_categories = get_servicem8_categories()

    job_category_uuid = None
    if sm8_service_categories:
        for category in sm8_service_categories:
            if category.get("name", "").lower() == service_category.lower():
                job_category_uuid = category.get("uuid")
                break

    job_description = (
        f"{format_value('Service Category', service_category)}\n"
        f"Enquiry Notes: {enquiry_notes.strip()}"
    )
    job_data = {
        "job_description": job_description,
        "category_uuid": job_category_uuid,
        "status": "Quote",
        "date": str(date.today()),
    }

    print(f"Creating job with data: {job_data}")
    
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
