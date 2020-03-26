from mesika_utils.Base import json, transaction
from mesika_utils.Base import JsonResponse
from mesika_utils.ExceptionManager import IntegrityError
from django.conf import settings
from payments.tasks import process_payment_request
from django.db import DatabaseError

from payments.models import Transactions
from payments.models import ExtraDetails

LOG_HANDLER = settings.LOG_HANDLER


def post_transaction(request):

    module = "payments.post_transaction"

    LOG_HANDLER.writelog(module, f"PAYLOAD >>> {request.body}")

    pl = json.loads(request.body)

    response = {}
    extra_usable_information = {}
    try:
        voucher_code = ""
        reference = pl['reference_number']
        narration = pl['narration']
        payer_msisdn = pl['payer_msisdn']
        account = pl['account_number']
        amount = pl['billed_amount']
        processing_fees = pl['processing_fees']

        try:
            voucher_code = pl["voucher_code"]
        except:
            LOG_HANDLER.writelog(module, f"NO VOUCHER CODE INCLUDED FOR THIS REQUEST")
            voucher_code = ""
        provider = pl['provider']
        stored = False

        # Extra
        extra_usable_information = pl['extra_details']
        LOG_HANDLER.writelog(module, f"EXTRA DETAILS: {extra_usable_information}")
        extra_usable_information['voucher_code'] = voucher_code

        with transaction.atomic():
            trx = Transactions(
                payer_reference_number=reference,
                payer_msisdn=payer_msisdn,
                account_number=account,
                provider=provider,
                amount=amount,
                processing_charge=processing_fees,
            )
            trx.save(using="payment_collections_client")

            ed = ExtraDetails(transaction=trx, details=extra_usable_information)
            ed.save(using="payment_collections_client", force_insert=True)
            stored = True

        if stored:
            LOG_HANDLER.writelog(module, f"SENDING {reference} TO PROCESSING QUEUE")
            # Forward to Celery Job For Processing
            pnum = process_payment_request.delay(provider, account, amount,
                                                 reference, narration, 
                                                 payer_msisdn, voucher_code)

            response['status'] = 201
            response['mesika_reference_number'] = trx.mesika_reference_number
            response['transaction_reference_number'] = trx.transaction_id
            response['processing_number'] = pnum.id
            response['payer_reference_number'] = trx.payer_reference_number
            response['reason'] = "Transaction Saved For Processing"
        else:
            transaction.rollback()
            response['status'] = 901
            response['reason'] = "Database Could Not Store This Transaction.Please retry."

    except IntegrityError:
        transaction.rollback()
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 900
        response['reason'] = f"Duplicate Transaction ID-{ler['error_value']}"

    except DatabaseError:
        transaction.rollback()
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 901
        response['reason'] = "Database Could Not Store This Transaction.Please retry."

    except KeyError:
        transaction.rollback()
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 407
        response['reason'] = f"Missing Key {ler['error_value']}"

    except:
        transaction.rollback()
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"Exception Storing Transaction {ler}"

    LOG_HANDLER.writelog(module, f"OUTBOUND RESPONSE ::: {response}")

    return JsonResponse(response)
