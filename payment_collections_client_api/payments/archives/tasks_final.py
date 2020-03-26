# from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
#from plugins.notifications.tasks import post_sms
from mesika_plugins.sms_notifications.tasks import post_sms_via_adb
from mesika_plugins.sms_notifications.tasks import post_sms_via_mesika

import requests

LOG_HANDLER = settings.LOG_HANDLER


@shared_task(route="pcc", queue="pcc", exchange="pcc",
             name="payment_collections_client_api.payments.tasks.process_payment_request",
             store_errors_even_if_ignored=True)
def process_payment_request(provider, account, amount,  billed_amount, payer_ref,
                            narration, payer_msisdn, voucher_code):
    module = "task.process_payment_request"
    response = {}
    valid_provider = False
    LOG_HANDLER.writelog(module,
                         f"RECEIVED ::provider:{provider},account:{account},"
                         f"amount:{amount},payer_ref:{payer_ref},"
                         f"narration:{narration},payer_msisdn:{payer_msisdn}")

    # Get Provider

    # Load Providers END POINTS from JSON FILE

    # Post Payment Debit Request+Callback and wait for response on update page
    # when successful

    # Update Transaction table as required

    try:

        LOG_HANDLER.writelog(module,
                             f"PROCESSING WITH PROVIDERS:{settings.PAYMENT_PROVIDER_ENDPOINT} "
                             f"and SMS:{settings.SMS_SOURCE_ADDRESS} and "
                             f"{settings.TRANSACTION_CALLBACK}")

        # pload = {
        #     "account_number": account,
        #     "amount": amount,
        #     "reference_number": payer_ref,
        #     "narration": narration,
        #     "callback": settings.TRANSACTION_CALLBACK
        # }

        # LOG_HANDLER.writelog(module, f"PAYLOAD SET TO {pload}")

        provider_list = settings.PAYMENT_PROVIDER_ENDPOINT
        sender_id = settings.SMS_SOURCE_ADDRESS

        endpoint = ""
        call_provider = ""

        for providers in provider_list:
            for kv in providers:
                LOG_HANDLER.writelog(module, f"{kv}")
                if kv == provider:
                    endpoint = providers[kv]
                    valid_provider = True
                    break

        if valid_provider and provider == "VODAFONE":
            pload = {
            "account_number": account,
            "amount": billed_amount,
            "reference_number": payer_ref,
            "narration": narration,
            "voucher_code": voucher_code,
            "callback": settings.TRANSACTION_CALLBACK
        }

            LOG_HANDLER.writelog(module, f"POSTING ::: {pload} to {endpoint}")
            call_provider = requests.post(endpoint, json=pload, verify=False, timeout=40)

        elif valid_provider and provider == "MTN":
            pload = {
            "account": account,
            "amount": billed_amount,
            "trxid": payer_ref,
        }
            LOG_HANDLER.writelog(module, f"POSTING ::: {pload} to {endpoint}")
            call_provider = requests.post(endpoint, params=pload, verify=False)

        elif valid_provider and provider == "AIRTELTIGO":
            pload = {
                "account_number": account,
                "amount": billed_amount,
                "reference_number": payer_ref,
                "narration": narration,
                "callback": settings.TRANSACTION_CALLBACK
            }
            LOG_HANDLER.writelog(module, f"POSTING ::: {pload} to {endpoint}")
            call_provider = requests.post(endpoint, json=pload, verify=False, timeout=40)

        else:
            response['status'] = 303
            response['reason'] = f"Provider {provider} UNKNOWN"

        LOG_HANDLER.writelog(module, f"CALL RESPONSE CODE ::: {call_provider.status_code}")
        LOG_HANDLER.writelog(module, f"CALL RESPONSE ::: {call_provider.text}")
        status_split = call_provider.text.split('|')
        status_sms = status_split[0].split(':')
        statussms = status_sms[1]

        text = f"""Dear customer, your payment of GHS.{amount} via {provider} to {sender_id} {statussms} -Ref:{payer_ref}."""

        # if provider == "MTN":
        #     text = f"{text}dial *170# to approve."

        try:
            sm = ""
            #post_sms.delay(sender_id, text, payer_msisdn, payer_ref)
           # post_sms_via_mesika.delay(sender_id, text, payer_msisdn, payer_ref)
            sm = post_sms_via_mesika.delay(sender_id, text,payer_msisdn)
            LOG_HANDLER.writelog(module, f"DELIVERING ACCT MSG: {sm.id}")

        except:
            LOG_HANDLER.log_error_detailed(module, module)

        response = {
            "status": 200,
            "delivery_id": sm.id,
            "reason": "Processing Completed"
        }

        endpoint = "https://multione-enterprise-non-rfi-api.mesika.org:24443/api/client-collections/v1/transactions/update/payer_reference/{payer_ref}/"
        payload = {"status": statussms}
        response = requests.post(endpoint, json=payload, verify=False)
        LOG_HANDLER.writelog(module, f"CALL RESPONSE ::: {call_provider.text}")


    except:
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"Exception Processing Payment Request of GHS.{amount} {ler}"

    LOG_HANDLER.writelog(module, f"RESPONSE ::: {response}")

    return response

