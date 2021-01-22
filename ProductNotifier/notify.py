import json
import os
import uuid

import azure.functions as func
from scraper_pipeline.models import notification
from scraper_pipeline.models import state_change_notification
from scraper_pipeline.models import subscriber
from scraper_pipeline.notify import notifier
from scraper_pipeline.notify.plugin import gmail_notifier


def main(msg: func.ServiceBusMessage, notifications, subscriptionsblob: str):
    json_str = msg.get_body().decode('utf-8')
    change_notif = state_change_notification.StateChangeNotification(**json.loads(json_str))
    previous_notifications = [
        notification.Notification(page_id=obj['page_id'], address=obj['address'], last_notify_time=obj['last_notify_time'])
        for obj in json.loads(notifications)
    ]

    # the subscriptions are stored in the format key=sku, val=(email,wait)
    # so this needs to be expanded into a list of objects that are
    # Subscriber objects that have all (sku,email,wait) encapsulated in the object
    subscriber_sku_mapping = json.loads(subscriptionsblob)
    subscribers = []
    for sku in subscriber_sku_mapping:
        for email_wait in subscriber_sku_mapping[sku]:
            subscribers.append(subscriber.Subscriber(page_id=sku, address=email_wait['email'], wait_seconds=email_wait['wait']))

    notifier_obj = notifier.Notifier(send_mail)

    new_notifications = notifier_obj.notify_change(change_notif, previous_notifications, subscribers)

    notification_rows = []
    for notif in new_notifications:
        row_key = str(uuid.uuid4())
        notification_rows.append(
            {
                'PartitionKey': notif.page_id,
                'RowKey': row_key,
                **notif._asdict()
            }
        )

    return json.dumps(notification_rows)

def send_mail(sku, old, new, addr, metadata):
    gmail = gmail_notifier.GmailNotifier(os.environ['NotifierEmail'], os.environ['NotifierPw'])

    with gmail.connect():
        subject = f"SKU {sku} in stock"
        body = f"Link: {metadata['url']}"
        gmail.send(addr, subject, body)