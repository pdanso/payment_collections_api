from mesika_utils.Base import JsonResponse
from django.conf import settings
from payments.models import Transactions 
from payments.models import ExtraDetails
import json
from django.db.models import Q
from django.utils.dateparse import parse_date
LOG_HANDLER = settings.LOG_HANDLER


def report(request):
    module = "payments.report"

    response = {}

    try:
        LOG_HANDLER.writelog(module, f"RQ:: {request.body}")

        pl = json.loads(request.body)

        s_date = pl['start_date']
        e_date = pl['end_date']

        st_date = parse_date(s_date)
        ed_date = parse_date(e_date)

        all_trx = Transactions.objects.filter(Q(date_submitted__gte=st_date),
                                          Q(date_submitted__lte=ed_date))
        trx_list = []

        LOG_HANDLER.writelog(module, f"TRX RESPONSE :: {all_trx}")

        for trx in all_trx:
          #  dt = trx.get_details()
          #  trx_list.append(dt)

          #  LOG_HANDLER.writelog(module, f"{trx}"

            ex_det = ExtraDetails.objects.get(transaction=trx)
            if not ex_det:
                LOG_HANDLER.writelog(module, f"{trx} -- HAS NO EXTRA DETAILS")
                LOG_HANDLER.writelog(module, f"{trx.get_details()}")
                trx_list.append(trx.get_details())
              #  full_details = trx.get_details()

            else:
                LOG_HANDLER.writelog(module, f"EX-DATA:{ex_det.get_details()}")
                trx_list.append(ex_det.get_details())
            #    full_details = ex_det.get_details()


        response['status'] = 200
        response['reason'] = "Transactions List"
        response['transaction_list'] = trx_list
    except Transactions.DoesNotExist:
        response['status'] = 404
        response['reason'] = "Transactions have not been done"
    except:
        ler = LOG_HANDLER.log_error_detailed(module, module)
        response['status'] = 502
        response['reason'] = f"{ler}"

    LOG_HANDLER.writelog(module, f"SENDING RESPONSE :: {response}")

    return JsonResponse(response)
