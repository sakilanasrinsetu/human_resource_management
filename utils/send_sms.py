import requests
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from base.models import SMSMailSendLog
from user.models import UserAccount


def otp_send_sms(body, subject, phone):
    response = None
    try:
        # Prepare SMS data
        
        if phone.startswith("+880"):
            phone = phone[3:]  # Remove the '+880' prefix
        elif phone.startswith("880"):
            phone = phone[2:]
        elif not phone.startswith("01"):
            phone = "0" + phone 
            
        sms_data = {
            'api_token': settings.SSL_SMS_API_TOKEN,
            'sid': settings.SSL_SID,
            'sms': body,
            'msisdn': phone,
            'csms_id': "35434029384" + timezone.now().date().__str__()
        }
        
        # Send POST request to SMS API endpoint
        response = requests.post(
            url="https://smsplus.sslwireless.com/api/v3/send-sms",
            data=sms_data
        )
        
        res = response.raise_for_status()  # Raise HTTPError for non-2xx responses
        
        print('Sending SMS with data:', res, response.json())  # For debugging
        
        # Determine SIM type based on phone number prefix
        sim_type = None
        
        if phone.startswith("017") or phone.startswith("013"):
            sim_type = "GRAMEENPHONE"
        elif phone.startswith("018") or phone.startswith("014"):
            sim_type = "ROBI"
        elif phone.startswith("019") or phone.startswith("015"):
            sim_type = "BANGLALINK"
        elif phone.startswith("015"):
            sim_type = "TELETALK"
        elif phone.startswith("016"):
            sim_type = "AIRTEL"
        
        type = 'SMS'
        
        # Create SMSMailSendLog entry for logging

        
    except requests.exceptions.RequestException as e:
        body = f"Failed to send SMS: {str(e)}"
        
        # raise Exception(f"Failed to send SMS: {str(e)}")
    
        print(body)
    
    user_qs = UserAccount.objects.filter(id=1).last()  # Adjust query as needed
    public_ip = None
    
    # Fetch public IP address for logging
    ip_response = requests.get('https://api.ipify.org?format=json')
    if ip_response.status_code == 200:
        data = ip_response.json()
        public_ip = data['ip']
    
    # Create SMSMailSendLog instance
    SMSMailSendLog.objects.create(
        username=phone,
        subject=subject,
        body=body,
        type=type,
        sim_type=sim_type,
        created_by=user_qs,
        ip_address=public_ip,
        status=response.json(),
    )
        
    return response

def send_email(email, subject, body):
    response = None
    mail_text = body if isinstance(body, str) else "\n".join(body)  # Ensure mail_text is a string
    
    mail_from = "GProjukti.com <" + settings.EMAIL_HOST_USER + ">"
    mail_to = [email]
    
    print('Sending mail to:', mail_to)
    
    public_ip = None
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            data = response.json()
            public_ip = data['ip']
            print('Public IP:', public_ip)
    except Exception as e:
        print('Failed to retrieve public IP:', e)
    
    user_qs = UserAccount.objects.filter(id=1).last()
    
    for mail in mail_to:
        SMSMailSendLog.objects.create(
            username=mail, 
            subject=subject, 
            body=body, 
            type='EMAIL', 
            sim_type='GMAIL',
            created_by=user_qs, 
            ip_address=public_ip
        )

        try:
            msg = EmailMultiAlternatives(subject, mail_text, mail_from, [mail])
            msg.attach_alternative(mail_text, "text/html")
            msg.send()
            print(f"Email sent successfully to {mail}")
        except Exception as e:
            # Handle exceptions (e.g., logging the error)
            print(f"Failed to send email to {mail}: {e}")

    return response