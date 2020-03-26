from mesika_utils.Base import JsonResponse, require_GET

from django.conf import settings


from payments.models import Transactions
from payments.models import ExtraDetails

LOG_HANDLER = settings.LOG_HANDLER


@require_GET
def view_transactions(request, transaction_id):

    module = "payments.view_transactions"

    response = {}

    LOG_HANDLER.writelog(module, f"VIEWING {transaction_id}")

    try:

        trx_search = Transactions.objects.using(
            'payment_collections_client').get(transaction_id=transaction_id)

        if not trx_search:
            response['status'] = 404
            response['reason'] = "Transaction Does Not Exist"
        else:
            # Check if extra details and get all
            full_details = {}

            try:
                ex_det = ExtraDetails.objects.using(
                    'payment_collections_client').get(trx_search)

                if not ex_det:
                    LOG_HANDLER.writelog(module, f"{trx_search} -- HAS NO EXTRA DETAILS")
                    full_details = trx_search.get_details()
                else:
                    full_details = ex_det.get_details()
            except:
                LOG_HANDLER.log_error_detailed(module, module)

            response['status'] = 200
            response['transaction_details'] = full_details
            response['reason'] = "Transaction Found"

    except Transactions.DoesNotExist:
        response['status'] = 404
        response['reason'] = "Transaction Does Not Exist"

        response['status'] = 200
        response['reason'] = "Transaction Saved"

    except:
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"Exception Viewing Transactions {ler}"

    LOG_HANDLER.writelog(module, f"RESPONSE ::: {response}")

    return JsonResponse(response)
