# src/subscription_utils.py
import requests
import logging

subscriptions = []

def notify_subscribers(subscription_type, data, action="INSERT"):
    """    Notify subscribers about changes in pollution data.
    """
    for sub in subscriptions:
        if subscription_type in sub["subscriptions"]:
            payload = {
                "subscriptionId": str(subscriptions.index(sub)),
                "notifications": [{
                    "subscription": subscription_type,
                    "action": action,
                    "notificationData": data
                }]
            }
            try:
                requests.post(sub["notificationUrl"], json=payload)
            except Exception as e:
                logging.error(f"Failed to notify {sub['notificationUrl']}: {e}")
