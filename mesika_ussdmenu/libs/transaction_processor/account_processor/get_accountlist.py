import transaction_processor.account_processor as account_processor
import core_processor
import session_processor
import api_processor

import json

logfile = "get_accountlist"


def get_accountlist(url, request, stored_data, next_position, goback_message):
    msisdn = request.GET["msisdn"]


    # payload = {"account_number": account_number}
    # account_processor.libhandler.writelog(logfile, f"Payload:{payload}")

    # account_results = api_processor.call_api(url, "get", modul, "getAccountlist", payload)
    # status = account_results['status']
    account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "12345987"},
                                                                   {"id": 2, "account_number": "09876789878"}]}

    if account_results['status'] == 200:
        acc_count = account_results['count']
        account_list = account_results['account_list']

        if acc_count >= 1:
            message = ""
            count = 0
            for n in account_results['account_list']:
                acct_id = n['id']
                source_account = n['account_number']
                count += 1
                message += str(count) + '. ' + str(source_account) + '^'

            str_conv = json.dumps(account_list)
            stored_data = f"{str_conv}?{stored_data}"

            message = f"Please select an Account Number for this transaction^{message}"  # ^0. Go back"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, next_position, stored_data)
            account_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = "Account numbers cannot be displayed right now. Please try again later"
            menu_response = core_processor.goto_start.goto_start(request, message, stored_data, goback_message)
            account_processor.libhandler.writelog(logfile, f"Message: {message}")

    else:
        message = "Account numbers cannot be displayed right now. Please try again later"
        menu_response = core_processor.goto_start.goto_start(request, message, stored_data, goback_message)
        account_processor.libhandler.writelog(logfile, f"Message: {message}")

    return menu_response
