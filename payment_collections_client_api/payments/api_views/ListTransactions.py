from mesika_utils.Base import JsonResponse
from django.conf import settings

from payments.models import Transactions
from payments.models import ExtraDetails

from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import timedelta,date
LOG_HANDLER = settings.LOG_HANDLER


def list_transactions(request):

    module = "payments.list_transactions"

    response = {}

    trx_list = []

    try:

        #trx = Transactions.objects.using('payment_collections_client'
        #                                 ).order_by('date_submitted').all()
#        trx = Transactions.objects.order_by('date_submitted').all()
        today = date.today()
        tomorrow = today + timedelta(1)

        LOG_HANDLER.writelog(module, f"DATE RANGE:::{today} - {tomorrow}")

        trx = Transactions.objects.filter(Q(date_submitted__gte=today),
                                          Q(date_submitted__lte=tomorrow))

        LOG_HANDLER.writelog(module, f"TRX RESPONSE :: {trx}")



        if not trx:
            response['status'] = 404
            response['reason'] = "No transactions created"

        else:
            response['status'] = 200

            for transaction in trx:

                LOG_HANDLER.writelog(module, f"{transaction}")

                full_details = {}

                try:
                    #ex_det = ExtraDetails.objects.using(
                     #   'payment_collections_client').get(transaction=transaction)
                    ex_det = ExtraDetails.objects.get(transaction=transaction)

                    LOG_HANDLER.writelog(module, f"EXTRA RESULTS:::{ex_det}")

                    if not ex_det:
                        LOG_HANDLER.writelog(module, f"{transaction} -- HAS NO EXTRA DETAILS")
                        LOG_HANDLER.writelog(module, f"{transaction.get_details()}")
                        full_details = transaction.get_details()
                    else:
                        LOG_HANDLER.writelog(module, f"EX-DATA:{ex_det.get_details()}")
                        full_details = ex_det.get_details()
                except:
                    LOG_HANDLER.log_error_detailed(module, module)

                trx_list.append(full_details)

            response['transactions'] = trx_list
            response['status'] = 200
            response['reason'] = "Transactions Found And Loaded"

    except Transactions.DoesNotExist:
        response['status'] = 404
        response['reason'] = "No transactions created"

    except:
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"Exception Storing Transaction {ler}"

    LOG_HANDLER.writelog(module, f"RESPONSE ::: {response}")

    return JsonResponse(response)
