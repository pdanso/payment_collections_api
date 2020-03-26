# from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from payments.models import Transactions
from payments.vodafone import main
import time
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

        #provider_list = settings.PAYMENT_PROVIDER_ENDPOINT
        provider_list = [{"MTN": "https://10.85.85.65:24766/api/prymo-momo/debit-wallet/"},{"VODAFONE": "https://10.85.85.65:24766/api/vodafonecash/debit-wallet/"},{"AIRTELTIGO": "https://10.85.85.65:24766/api/prymo-momo/debit-wallet/"}]
        LOG_HANDLER.writelog(module, f"PAMENT PROVIDERS ENDPOINT::: {provider_list}")
        sender_id = settings.SMS_SOURCE_ADDRESS

        endpoint = ""
        call_provider = ""
        status_sms = ""

        for providers in provider_list:
            for kv in providers:
                LOG_HANDLER.writelog(module, f"Provider {kv}")
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
            response = call_provider.json() 
            provider_ref = response['provider_reference_number']
            LOG_HANDLER.writelog(module, f"PROVIDER REFERENCE NUMBER ::: {provider_ref}")
            
            time.sleep(5)
            record = main(provider_ref)
            status_sms = record[0]

            if status_sms == "PAID":
                status_sms = "SUCCESSFUL"

            elif status_sms == "UNPAID":
                status_sms = "FAILED"



        elif valid_provider and provider == "MTN": 
            pload = {
            "account": account,
            "amount": billed_amount,
            "trxid": payer_ref,
        }
            LOG_HANDLER.writelog(module, f"POSTING ::: {pload} to {endpoint}")
            call_provider = requests.post(endpoint, params=pload, verify=False)

            LOG_HANDLER.writelog(module, f"CALL RESPONSE CODE ::: {call_provider.status_code}")
            LOG_HANDLER.writelog(module, f"CALL RESPONSE ::: {call_provider.text}")
            status_split = call_provider.text.split('|')
            status_sms = status_split[0].split(':')
            status_sms = status_sms[1]

            if status_sms == "COMPLETED":
                status_sms = "SUCCESSFUL"

        elif valid_provider and provider == "AIRTELTIGO":
            pload = {
            "account": account,
            "amount": billed_amount,
            "trxid": payer_ref,
        }
            newone = 'https://10.85.85.65:24766/api/prymo-momo/debit-wallet/'
            LOG_HANDLER.writelog(module, f"POSTING ::: {pload} to {newone}")
            call_provider = requests.post(newone, params=pload, verify=False)

            LOG_HANDLER.writelog(module, f"CALL RESPONSE CODE ::: {call_provider.status_code}")
            LOG_HANDLER.writelog(module, f"CALL RESPONSE ::: {call_provider.text}")
            status_split = call_provider.text.split('|')
            status_sms = status_split[0].split(':')
            status_sms = status_sms[1]

            if status_sms == "COMPLETED":
                status_sms = "SUCCESSFUL"

    #    elif valid_provider and provider == "AIRTELTIGO" or provider == "AirtelTigo":
     #       pload = {
      #          "msisdn": account,
       #         "amount": billed_amount,
#                "product_name": narration,
 #               "misika247_transaction_id": payer_ref,
  #              "narration": narration,
   #         }
    #        LOG_HANDLER.writelog(module, f"POSTING ::: {pload} to {endpoint}")
     #       call_provider = requests.post(endpoint, json=pload, verify=False, timeout=40)
      #      LOG_HANDLER.writelog(module, f"CALL RESPONSE ::: {call_provider.text}")

        else:
            response['status'] = 303
            response['reason'] = f"Provider {provider} UNKNOWN"

        text = f"""Dear customer, your payment of GHS.{amount} via {provider} to {sender_id} {status_sms} -Ref:{payer_ref}."""

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

        try:
            trx_search = Transactions.objects.filter(payer_reference_number=payer_ref)
            LOG_HANDLER.writelog(module, f"TRANSACTION RESULT ||| {trx_search} |||")

            if not trx_search:
                trx_search.update(status='TRXN NOT FOUND')
                LOG_HANDLER.writelog(module, f"TRANSACTION NOT FOUND")

            else:
                trx_search.update(status=status_sms)
                LOG_HANDLER.writelog(module, f"TRANSACTION UPDATED TO {status_sms}")

        except:
            ler = LOG_HANDLER.log_error_detailed(module, module)

            LOG_HANDLER.writelog(module, f"Exception due to {ler}")



    except:
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"Exception Processing Payment Request of GHS.{amount} {ler}"

    LOG_HANDLER.writelog(module, f"RESPONSE ::: {response}")

    return response

