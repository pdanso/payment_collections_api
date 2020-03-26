from mesika_utils.Base import json
from mesika_utils.Base import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST

from payments.models import Transactions

LOG_HANDLER = settings.LOG_HANDLER


@require_POST
def update_transaction(request, reference_type, transaction_id):

    module = "payments.update_transaction"
    LOG_HANDLER.writelog(module, f"INBOUND PAYLOAD >>> {request.body}")

    pl = json.loads(request.body)

    LOG_HANDLER.writelog(module, f"INBOUND DICT >>> {pl}")

    # trx_status = (pl['status']).upper()

    response = {}

    try:

        if reference_type == "payer_reference":
            trx_search = Transactions.objects.using('payment_collections_client').filter(payer_reference_number=transaction_id)
        elif reference_type == "mesika_reference":
            trx_search = Transactions.objects.using('payment_collections_client').filter(mesika_reference_number=transaction_id)
        elif reference_type == "provider_reference":
            trx_search = Transactions.objects.using('payment_collections_client').filter(provider_reference_number=transaction_id)
        else:
            trx_search = Transactions.objects.filter(transaction_id=transaction_id)

        LOG_HANDLER.writelog(module, f"TRANSACTION RESULT ||| {trx_search} |||")

        if not trx_search:
            response['status'] = 404
            response['reason'] = f"Transaction reference ||{reference_type}||::{trx_search} Does Not Exist"
        else:
            trx_search.update(status=pl['status'])
            response['status'] = 200
            response['reason'] = "Transaction Updated"

    except Transactions.DoesNotExist:
        response['status'] = 404
        response['reason'] = f"Transaction ||{transaction_id}|| Does Not Exist in [[{reference_type}]]"

    except:
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"Exception Updating Transaction {ler}"

    LOG_HANDLER.writelog(module, f"UPDATE RESPONSE ::: {response}")

    return JsonResponse(response)
