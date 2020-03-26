import transaction_processor.account_processor as account_processor
import core_processor
import session_processor
import api_processor

logfile = "get_accountlist"


def balance_check(url, account_number):
    payload = {"account_number": account_number}
    account_processor.libhandler.writelog(logfile, f"Payload:{payload}")

    response = api_processor.call_api(url, "get", modul, "getBalance", payload)
    status = response['status']

    return response
