from . import db
from .notifications import send_sms


SMS_MIN_ALERT_LEVEL = 2


def raise_alert(name, msg, level):
    db.add_alert(name, msg)
    if level < SMS_MIN_ALERT_LEVEL:
        return
    send_sms(msg)


def delete_old():
    db.delete_old_alerts()
