import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_API_TOKEN = os.getenv("HUBSPOT_API_TOKEN")

ON_SITE_QUOTE_SCHEDULED_PIPELINE_ID = "1690811882"
QUOTE_SENT_PIPELINE_ID = "closedwon"
QUOTE_VIEWED_PIPELINE_ID = "1690215924"


def find_hubspot_deal_by_job_uuid(job_uuid):
    url = "https://api.hubapi.com/crm/v3/objects/deals/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
    }
    payload = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "sm8_job_id",
                        "operator": "EQ",
                        "value": job_uuid,
                    }
                ]
            }
        ],
        "properties": ["dealstage"],
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        if results:
            return results[0].get("id")
        return None
    except Exception as e:
        logging.error(f"Error searching HubSpot deal: {e}")
        return None


def update_hubspot_deal(deal_id, properties_to_update):
    """
    Generic function to update a HubSpot deal with a dictionary of properties.
    """
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
    }
    payload = {"properties": properties_to_update}
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        logging.info(
            f"Successfully updated HubSpot deal {deal_id} with: {properties_to_update}"
        )
        return True
    except Exception as e:
        logging.error(f"Error updating HubSpot deal: {e}")
        return False


def update_hubspot_deal_stage(deal_id, new_stage):
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
    }
    payload = {"properties": {"dealstage": new_stage}}
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        logging.info(
            f"Successfully updated HubSpot deal {deal_id} to stage {new_stage}"
        )
        return True
    except Exception as e:
        logging.error(f"Error updating HubSpot deal: {e}")
        return False
    
def get_hubspot_deal_properties(deal_id, properties):
    """Fetches specific properties for a given HubSpot deal ID."""
    url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}"
    params = {"properties": ",".join(properties)}
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {HUBSPOT_API_TOKEN}",
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("properties", {})
    except Exception as e:
        logging.error(f"Error fetching properties for deal {deal_id}: {e}")
        return None
