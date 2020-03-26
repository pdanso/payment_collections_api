from mesika_utils.Base import JsonResponse
from django.conf import settings
from mesika_utils.Base import require_GET
from payments.models import ExtraDetails
from payments.models import Transactions

LOG_HANDLER = settings.LOG_HANDLER


@require_GET
def search_for_transaction(request, reference_type, transaction_id):

    module = "payments.search_for_transaction"

    LOG_HANDLER.write_local(module,
                            f"SEARCHING FOR >>> ||{reference_type}||>>{transaction_id}")

    response = {}

    try:

        if reference_type == "payer_reference":
            trx_search = Transactions.objects.using(
                'payment_collections_client').get(payer_reference_number=transaction_id)
        elif reference_type == "mesika_reference":
            trx_search = Transactions.objects.using(
                'payment_collections_client').get(mesika_reference_number=transaction_id)
        elif reference_type == "provider_reference":
            trx_search = Transactions.objects.using(
                'payment_collections_client').get(provider_reference_number=transaction_id)
        else:
            trx_search = Transactions.objects.using(
                'payment_collections_client').get(transaction_id=transaction_id)

        LOG_HANDLER.writelog(module, f"GOT TRX RESULT:::{trx_search}")

        if not trx_search:
            response['status'] = 404
            response['reason'] = f"Transaction in ||{reference_type}|| Does Not Exist"
        else:
            # Check if extra details and get all
            full_details = {}

            try:
                ex_det = ExtraDetails.objects.using(
                    'payment_collections_client').get(transaction=trx_search)

                if not ex_det:
                    LOG_HANDLER.writelog(module, f"{trx_search} -- HAS NO EXTRA DETAILS")
                    full_details = trx_search.get_details()
                else:
                    full_details = ex_det.get_details()
            except:
                LOG_HANDLER.log_error_detailed(module, module)

            response = full_details
            response['status'] = 200
            response['reason'] = "Transaction Found"
    except Transactions.DoesNotExist:
        response['status'] = 404
        response['reason'] = f"Transaction ||{transaction_id}|| Does Not Exist in [[{reference_type}]]"

    except:
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"Exception Searching For Transaction {ler}"

    LOG_HANDLER.writelog(module, f"RESPONSE ::: {response}")

    return JsonResponse(response)
