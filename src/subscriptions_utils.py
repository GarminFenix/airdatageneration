# src/subscription_utils.py
import requests
import logging

subscriptions = []

def notify_subscribers(subscription_type, data, action="INSERT"):
    """
    Notify subscribers about changes in pollution data.
    """
    for sub in subscriptions:
        if subscription_type in sub["subscriptions"]:
            # Group data by systemCodeNumber and wrap dynamics
            grouped_data = {}
            for entry in data:
                site_id = entry["systemCodeNumber"]
                dynamic_entry = {k: v for k, v in entry.items() if k != "systemCodeNumber"}
                grouped_data.setdefault(site_id, []).append(dynamic_entry)

            # Build UTMC-style payload
            notification_data = [
                {
                    "systemCodeNumber": site_id,
                    "dynamics": dynamics
                }
                for site_id, dynamics in grouped_data.items()
            ]

            payload = {
                "subscriptionId": str(subscriptions.index(sub)),
                "notifications": [{
                    "subscription": subscription_type,
                    "action": action,
                    "notificationData": notification_data
                }]
            }

            try:
                requests.post(sub["notificationUrl"], json=payload)
            except Exception as e:
                logging.error(f"Failed to notify {sub['notificationUrl']}: {e}")
