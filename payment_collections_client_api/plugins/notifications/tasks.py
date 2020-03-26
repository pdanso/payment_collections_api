from django.core.mail import EmailMultiAlternatives
from celery import shared_task
from django.conf import settings
from mesika_utils.MsisdnManager import format_msisdn_to_ghana
import requests
from plugins.notifications.models import Messages
from plugins.notifications.models import Channel

LOG_HANDLER = settings.LOG_HANDLER


@shared_task(queue="pcc", routing_key="pcc", exchange="pcc")
def post_mail(source_email, subject, body, recipient_list):
    """POST EMAIL"""
    module = "notifications.post_email"
    post_status = {}

    try:
        LOG_HANDLER.writelog(module,
                             f"Posting to {recipient_list} \nBody:{body}")

        # subject, from_email, to = 'hello', 'from@example.com',
        # 'to@example.com'

        # html_content = '<p>This is an <strong>important</strong> message.</p>'

        msg = EmailMultiAlternatives(subject, body, source_email, recipient_list)

        # msg.attach_alternative(html_content, "text/html")

        response = msg.send()

        LOG_HANDLER.writelog(module, f"Mail Response:{response}")

    except:
        errors = LOG_HANDLER.log_error_detailed(module, module)
        LOG_HANDLER.writelog(module, f"{post_mail} Errors: {errors}")

    return post_status


def url_encode(text):
    module = "post_sms"

    data = {}
    data['text'] = "%s" % (text)
    import urllib.parse
    url_values = urllib.parse.urlencode(data)
    encoded_text = "" + url_values[5:len(url_values)]
    LOG_HANDLER.write_local(module, "ENCODED TEXT==%s" % str(encoded_text))
    return encoded_text


@shared_task(queue="pcc", routing_key="pcc", exchange="pcc")
def post_sms(sender_id, text, delivery_msisdn, extid="NAN"):
    """POST EMAIL"""
    module = "notifications.post_sms"
    post_status = {}

    msisdn = format_msisdn_to_ghana(delivery_msisdn)

    try:

        try:
            chobj = Channel.objects.get(id=3)
            ms = Messages(message_id=extid, channel=chobj,subject="SMS", source=sender_id,
                          content=text, destination=delivery_msisdn)
            ms.save()

        except:
            LOG_HANDLER.writelog(module, f"ERROR SAVING MESSAGE IN DB")

        if len(msisdn) == 12 and len(sender_id) > 0:

            exid_add = "messageid=%s" % (extid)

            LOG_HANDLER.writelog(module, f"DLR URL {settings.KANNEL_DLR_ENDPOINT}")

            dlr_url = f"{settings.KANNEL_DLR_ENDPOINT}/?status=%d&oa=%p&da=%P&smsc=%i&time=%t&{exid_add}"

            LOG_HANDLER.write_local(module, f"DLR URL ::: {dlr_url}")

            LOG_HANDLER.writelog(module,
                                 f"Posting to {msisdn}. Body:{text}. From:{sender_id}")

            # out_text = url_encode(text)

            payload = (('username', f'{settings.KANNEL_USERNAME}'),
                       ('password', f'{settings.KANNEL_PASSWORD}'),
                       ('text', text),
                       ('to', msisdn),
                       ('from', sender_id),
                       ('dlr-mask', '63'),
                       ('dlr-url', dlr_url),
                       ('smsc', 'infobip'),
                       # ('dlr-url', str(url_encode(dlr_url))),
                       ('coding', '0'),
                       ('charset', 'ISO-8859-1')
                       )

            LOG_HANDLER.writelog(module, "POSTING NEW REQUEST WITH PAYLOAD ::: %s " % str(payload))

            endpoint = f"http://{settings.KANNEL_HOST}:{settings.KANNEL_PORT}/cgi-bin/sendsms"
            r = requests.get(endpoint, params=payload)
            LOG_HANDLER.writelog(module, f"REQUEST ::: {r.url}")
            LOG_HANDLER.writelog(module, f"MESSAGE_ID:{extid} | KANNEL_RESPONSE:{r.text}")
            post_status['status'] = 200
            post_status['reason'] = "Accepted for posting"

        else:
            # Send Failure Message Back
            dlr_url = f"{settings.KANNEL_DLR_ENDPOINT}/?status=16&messageid={extid}"
            rp = requests.get(dlr_url)
            LOG_HANDLER.writelog(module, f"UPDATE RESPONSE {rp.text}")
            post_status['status'] = 400
            post_status['reason'] = "Message Rejected"
    except:
        errors = LOG_HANDLER.log_error_detailed(module, module)
        LOG_HANDLER.writelog(module, f"{post_mail} Errors: {errors}")
        post_status['status'] = 500
        post_status['reason'] = f"Exception in delivery. {errors}"

    return post_status
