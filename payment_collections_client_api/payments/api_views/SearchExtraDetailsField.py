from mesika_utils.Base import json
from mesika_utils.Base import JsonResponse
from django.conf import settings
from payments.models import ExtraDetails

LOG_HANDLER = settings.LOG_HANDLER


def search_extra_details_field(request, field, value):

    module = "payments.view_transactions"

    response = {}

    LOG_HANDLER.writelog(module, f"VIEWING {field}-{value}")

    try:
        response['status'] = 200
        response['reason'] = "Transaction Found"

    except ExtraDetails.DoesNotExist:
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
