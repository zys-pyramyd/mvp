import os
import requests
import logging

logger = logging.getLogger(__name__)

ZEPTOMAIL_TOKEN = os.environ.get("ZEPTOMAIL_TOKEN")
ZEPTOMAIL_URL = "https://api.zeptomail.com/v1.1/email"
FROM_ADDRESS = os.environ.get("ZEPTOMAIL_FROM_ADDRESS", "noreply@pyramydhub.com")

def send_zeptomail(to_email: str, subject: str, html_content: str, to_name: str = "User"):
    if not ZEPTOMAIL_TOKEN:
        logger.warning(f"ZeptoMail token not configured. Skipping email: '{subject}' to {to_email}")
        return False
        
    headers = {
        "Authorization": f"Zoho-enczapikey {ZEPTOMAIL_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "from": {
            "address": FROM_ADDRESS,
            "name": "Pyramyd"
        },
        "to": [
            {
                "email_address": {
                    "address": to_email,
                    "name": to_name
                }
            }
        ],
        "subject": subject,
        "htmlbody": html_content
    }
    
    try:
        response = requests.post(ZEPTOMAIL_URL, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Successfully sent ZeptoMail to {to_email}")
        return True
    except requests.exceptions.HTTPError as h:
        logger.error(f"ZeptoMail HTTP Error sending to {to_email}: {h.response.text}")
        return False
    except Exception as e:
        logger.error(f"ZeptoMail Error sending to {to_email}: {e}")
        return False
