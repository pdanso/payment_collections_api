from mesika_utils.Base import *
from plugins.notifications.models import Messages
from django.shortcuts import HttpResponse
LOG_HANDLER = settings.LOG_HANDLER


def update_sms_dlr(request):
    """
    Update the message status after delivery or failure of it
    :param request:
    :return: update_status
    """
    module = "update_sms_dlr_status"

    update_status = "UPDATE FAILED"
    LOG_HANDLER.writelog(module, f"{request.GET}")

    try:
        message_status = request.GET['status']
        update_time = request.GET['time']

        # • 1: delivery success
        # • 2: delivery failure
        # • 4: message buffered
        # • 8: smsc submit
        # • 16: smsc reject
        # • 32: smsc ntermediate notifications

        if message_status == "1" or message_status == 1:
            db_status = "DELIVERED"
            message_uuid = request.GET['messageid']
            update_trx = Messages.objects.filter(message_id=message_uuid).update(
                message_status=db_status, last_update=update_time)
            LOG_HANDLER.writelog(module, f"MSG_ID:{message_uuid} | STATUS:{db_status} | {update_trx}")
            update_status = "UPDATED"
        elif message_status == "8":
            db_status = "SUBMITTED"
            message_uuid = request.GET['messageid']
            update_trx = Messages.objects.filter(message_id=message_uuid).update(
                message_status=db_status, last_update=update_time)
            LOG_HANDLER.writelog(module, f"MSG_ID:{message_uuid} | STATUS:{db_status} | {update_trx}")
            update_status = "UPDATED"

        elif message_status == "4":
            db_status = "BUFFERED"
            message_uuid = request.GET['messageid']
            update_trx = Messages.objects.filter(message_id=message_uuid).update(
                message_status=db_status, last_update=update_time)
            LOG_HANDLER.writelog(module, f"MSG_ID:{message_uuid} | STATUS:{db_status} | {update_trx}")
            update_status = "UPDATED"

        elif message_status == "16":
            db_status = "REJECTED"
            message_uuid = request.GET['messageid']
            update_trx = Messages.objects.filter(message_id=message_uuid).update(
                message_status=db_status, last_update=update_time)
            LOG_HANDLER.writelog(module, f"MSG_ID:{message_uuid} | STATUS:{db_status} | {update_trx}")
            update_status = "UPDATED"

        else:
            db_status = "FAILED"
            message_uuid = request.GET['messageid']
            update_trx = Messages.objects.filter(message_id=message_uuid).update(
                message_status=db_status, last_update=update_time)
            LOG_HANDLER.writelog(module, f"MSG_ID:{message_uuid} | STATUS:{db_status} | {update_trx}")
            update_status = "UPDATED"
    except:
        LOG_HANDLER.log_error_detailed(module, module)
        update_status ="Update Failure"

    return HttpResponse(update_status)
