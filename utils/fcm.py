import datetime
import json
import requests
from django.conf import settings

def send_fcm_push_notification_appointment(status="CallStaff", table_no=0, msg='', qs=None, **kwargs):
    order_no = kwargs.get('order_no')
    message_title = kwargs.get('message_title', 'Default Title')
    message_body = kwargs.get('message_body', 'Default Body')
    topic = kwargs.get('topic', None)
    condition = kwargs.get('condition', None)
    

    # Define the status value dictionary
    status_value = {
        "OrderReceived": {
            'notification': {'title': message_title, 'body': f'An order has been placed for table {table_no}'},
            'data': {'title': 'Order', 'body': str(datetime.datetime.now())}
        },
        "CallStaff": {
            'notification': {'title': message_title, 'body': message_body},
            'data': {'title': 'CallStaff', 'body': str(datetime.datetime.now())}
        }
    }

    success = False
    error_msg = None

    try:
        data = {
            "notification": status_value[status]['notification'],
            "data": status_value[status]['data'],
            "apns": {
                "headers": {
                    'apns-priority': '10',
                },
                "payload": {
                    "aps": {
                        "sound": 'default',
                    },
                },
            },
        }

        if topic:
            data["to"] = f"/topics/{topic}"
        elif condition:
            data["condition"] = condition
        else:
            raise ValueError("Either 'topic' or 'condition' must be provided")

        # Retrieve the FCM server key from settings
        FCM_SERVER_KEY = settings.FCM_DJANGO_SETTINGS.get('FCM_SERVER_KEY', None)

        if not FCM_SERVER_KEY:
            raise ValueError("FCM_SERVER_KEY is not set in settings.")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'key=' + FCM_SERVER_KEY
        }

        response = requests.post('https://fcm.googleapis.com/fcm/send', headers=headers, data=json.dumps(data))

        if 200 <= response.status_code < 300:
            response_json = response.json()
            if response_json.get('success') >= 1:
                success = True
            else:
                error_msg = response_json.get('results', [{}])[0].get('error', 'Unknown error')
        else:
            error_msg = f"HTTP error {response.status_code}: {response.text}"

    except Exception as e:
        error_msg = str(e)

    return success, error_msg

# Example usage
kwargs = {
    "order_no": 123,
    "message_title": "Order Update",
    "message_body": "Your order has been received",
    "topic": "global"  # Replace with your topic name
    # or "condition": "'stock-GOOG' in topics || 'industry-tech' in topics"
}
success, error = send_fcm_push_notification_appointment(status="OrderReceived", table_no=5, **kwargs)
print("Success:", success, "Error:", error)
