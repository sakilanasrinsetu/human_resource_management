import logging
from django.dispatch import receiver
from .signals import order_created
from .services import send_fcm_push_notification_appointment

logger = logging.getLogger(__name__)

@receiver(order_created)
def send_order_created_notification(sender, **kwargs):
    logger.info("send_order_created_notification signal received")
    
    order = kwargs.get('order')
    user = kwargs.get('user')

    # Assuming get_user_fcm_tokens is a function that retrieves FCM tokens for the user
    # tokens_list = get_user_fcm_tokens(user)
    
    message_title = "Order Created"
    message_body = f"Your order #{order.id} has been created successfully."

    success = send_fcm_push_notification_appointment(
        status="OrderReceived",
        table_no=order.table_no,
        msg='',
        qs=None,
        order_no=order.id,
        message_title=message_title,
        message_body=message_body
    )
    
    if success:
        logger.info("Notification sent successfully for order %s", order.id)
    else:
        logger.error("Failed to send notification for order %s", order.id)
