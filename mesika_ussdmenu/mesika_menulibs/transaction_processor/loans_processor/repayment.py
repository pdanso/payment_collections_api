import transaction_processor.loans_processor as loans_processor
import core_processor
import session_processor
import api_processor
import trxid_processor.get_alph_id

import json
import requests

logfile = "repayment"


def loans_repayment(request, msg, bank_code, last_position, pos, goback_message):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "REPSTA":
        repayment_results = {"status": 200,
                             "repayment_list": [{"id": 1, "name": "Loan Repayment"},
                                                {"id": 2, "name": "Interest Repayment"}]}

        message = ""
        count = 0

        for type in repayment_results['repayment_list']:
            repayment_id = type['id']
            repayment_name = type['name']
            count += 1
            message += str(count) + '. ' + str(repayment_name) + '^'

        str_conv = json.dumps(repayment_results['repayment_list'])
        stored_data = f"{str_conv}"

        message = f"Please select an option:^{message}"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "REPOPT", stored_data)
        loans_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "REPOPT":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        repayment_list = extract

        repayment_list = json.loads(repayment_list)

        repayment_id = repayment_list[sel]['id']
        repayment_name = repayment_list[sel]['name']

        loan_results = {"status": 200,
                       "loan_list": [{"id": 1, "name": "Funeral Loan"},
                                     {"id": 2, "name": "Personal Loan "}]}

        message = ""
        count = 0

        for type in loan_results['loan_list']:
            loan_id = type['id']
            loan_name = type['name']
            count += 1
            message += str(count) + '. ' + str(loan_name) + '^'

        str_conv = json.dumps(loan_results['loan_list'])
        stored_data = f"{str_conv}?{repayment_id}|{repayment_name}"

        message = f"Please select loan type^{message}"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "REPAMT", stored_data)
        loans_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position  == "REPAMT":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('?')
        loan_list = extract_reply[0]
        rest = extract_reply[1]

        loan_list = json.loads(loan_list)

        loan_id = loan_list[sel]['id']
        loan_name = loan_list[sel]['name']
        stored_data = f"{rest}|{loan_id}|{loan_name}"

        message = "Please enter amount: Eg: 5"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MDEPAY", stored_data)
        loans_processor.libhandler.writelog(logfile, f"Message: {message}")

    else:
        menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    return menu_response





