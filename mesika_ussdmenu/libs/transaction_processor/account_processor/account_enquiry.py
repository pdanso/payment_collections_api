import transaction_processor.account_processor as account_processor
import core_processor
import session_processor
import api_processor

logfile = "account_enquiry"


def account_enquiry(url, account_number):
    payload = {"account_number": account_number}
    account_processor.libhandler.writelog(logfile, f"Payload:{payload}")

    response = api_processor.call_api(url, "get", "", 'account_enquiry', payload)
    status = response['status']

    return status
