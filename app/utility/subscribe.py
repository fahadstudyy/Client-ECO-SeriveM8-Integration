import os
import requests
from dotenv import load_dotenv

load_dotenv()
SERVICEM8_API_KEY = os.getenv("SERVICEM8_API_KEY")

"""
JobActivity
activity_was_scheduled
"""


def main():
    url = "https://api.servicem8.com/webhook_subscriptions"
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "X-Api-Key": SERVICEM8_API_KEY,
    }
    data = {
        "object": "job",
        "fields": "quote_sent,status",
        "callback_url": "https://39626f72cea9.ngrok-free.app/webhook",
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        response_data = response.json()
        print(response_data)
    except Exception as e:
        print(f"Error creating webhook subscription: {e}")
        return None


if __name__ == "__main__":
    main()
