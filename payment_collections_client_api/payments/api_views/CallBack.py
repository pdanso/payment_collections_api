
from mesika_utils.Base import json
from mesika_utils.Base import JsonResponse
from django.conf import settings
from mesika_utils.RandomTransactionIds import generate_sso_token
from django.views.decorators.http import require_POST
from payments.models import Transactions
from mesika_plugins.sms_notifications.tasks import post_sms_via_adb
from mesika_plugins.sms_notifications.tasks import post_sms_via_mesika

#from plugins.notifications.tasks import post_sms

LOG_HANDLER = settings.LOG_HANDLER


@require_POST
def callback_receiver(request):

    module = "callback"
    LOG_HANDLER.writelog(module, f"INBOUND PAYLOAD >>> {request.body}")

    pl = json.loads(request.body)

    LOG_HANDLER.writelog(module, f"INBOUND DICT >>> {pl}")

    # trx_status = (pl['status']).upper()
    our_reference_number = ""
    response = {}

    try:

        our_reference_number = pl['payer_reference_number']
        transaction_status = pl["transaction_status"]
        status_description = pl["status_description"]
        provider_reference = pl["provider_reference_number"]

        find_transaction = Transactions.objects.using('payment_collections_client').filter(
            payer_reference_number=our_reference_number)

        if not find_transaction:
            response['status'] = 404
            response['reason'] = f"Transaction with Payer Reference {our_reference_number} Not Found"
        else:
            if transaction_status == "PAID":
                trx_update = find_transaction.update(status=transaction_status,
                                                     status_description=status_description,
                                                     provider_reference_number=provider_reference)

                LOG_HANDLER.writelog(module, f"TRANSACTION UPDATE DB:{trx_update}")
            else:
                trx_update = find_transaction.update(status=transaction_status,
                                                     status_description=status_description)
                LOG_HANDLER.writelog(module, f"TRANSACTION UPDATE DB:{trx_update}")

            try:
                LOG_HANDLER.writelog(module,
                                     f"ATTEMPTING SMS DELIVERY AFTER CALLBACK")
                get_for_sms = find_transaction.values()[0]
                payer_msisdn = get_for_sms['payer_msisdn']
                pay_amount = get_for_sms['amount']

                if transaction_status == "PAID":

                    sms_message = f"Dear customer, your payment of GHS.{pay_amount} was successful"
                else:
                    sms_message = f"Dear customer, your payment of GHS.{pay_amount} was not successful.Your payment provider did not approve your payment."

                sender_id = settings.SMS_SOURCE_ADDRESS

                payer_ref = generate_sso_token()

                #post_sms.delay(sender_id, sms_message, payer_msisdn, payer_ref)
                sm = post_sms_via_mesika.delay(f"{settings.CLIENT}", sms_message, payer_msisdn, payer_ref)
                LOG_HANDLER.writelog(module, f"DELIVERING ACCT MSG: {sm.id}")
            except:
                LOG_HANDLER.log_error_detailed(module, module)
                LOG_HANDLER.writelog(module, f"Could not send SMS on Call Back Receipt")

            response['status'] = 200
            response['reason'] = "Transaction Updated With Callback Response Successfully"

    except Transactions.DoesNotExist:
        response['status'] = 404
        response['reason'] = f"Transaction with Payer Reference {our_reference_number} Not Found"

    except:
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"Exception Updating Transaction {ler}"

    LOG_HANDLER.writelog(module, f"UPDATE RESPONSE ::: {response}")

    return JsonResponse(response)
