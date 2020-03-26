import transaction_processor.funds_transfer_processor as ft_processor
import core_processor
import api_processor
import session_processor
import secrets
import requests
import json

logfile = "ft_internal"

def gen_trx():

    trx = secrets.token_hex(12)
    trx = trx.replace('_', '')
    trx = trx.replace('-', '')
    trx = trx[8]
    return trx

def internal(request, url, bank_code, data, last_position, goback_message, pos):
    menu_response = ""

    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "FNDACL":
        account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "1000800051501"},
                                                                       {"id": 2, "account_number": "2000100611001"}]}

        if account_results['status'] == 200:
            acc_count = account_results['count']
            account_list = account_results['account_list']

            if acc_count >= 1:
                message = ""
                count = 0
                for n in account_list:
                    acct_id = n['id']
                    source_account = n['account_number']
                    count += 1
                    message += str(count) + '. ' + str(source_account) + '^'

                str_conv = json.dumps(account_list)
                stored_data = f"{str_conv}?{data}"

                message = f"Please select an Account Number for this transaction^{message}"  # ^0. Go back"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "FNDACT", stored_data)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            elif account_list == 1:
                message = ""

    elif last_position == "FNDACT":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        ft_processor.libhandler.writelog(logfile, f"sel = {sel}")

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        ft_processor.libhandler.writelog(logfile, f"Extract = {extract}")
        # extract_list = json.loads(extract)

        extract_reply = extract.split('?')
        acct_list = extract_reply[0]
        service_id = extract_reply[1]

        acct_list = json.loads(acct_list)

        ft_processor.libhandler.writelog(logfile, f"Extract = {acct_list}")

        acct_id = acct_list[sel]['id']
        acct_num = acct_list[sel]['account_number']

        stored_data = f"{data}|{acct_num}"

        message = f"Please enter the {bank_code} account number to credit"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        ft_processor.libhandler.writelog(logfile, f"Message: {message}")
        session_processor.store_menupoint.store_menupoint(request, "FNDCRD", stored_data)

    elif last_position == "FNDCRD":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        credit_acct_num = userdata
        stored_data = f"{extract}|{credit_acct_num}"

        if not credit_acct_num.isdigit():
            message = "Account Number entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "FNDCRD", extract)
            ft_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif credit_acct_num.isdigit():

            # payload = {"account_number": credit_acct_num}
            # response = call_api(payload, "cowrybank", "verifyAccountnumber")
            # status = response['status']

            status = 200

            if status == 200:
                #  provides details
                message = "Please enter amount to be transferred"
                menu_response = core_processor.make_response.make_response(request,"more", message)
                session_processor.store_menupoint.store_menupoint(request, "FNDAMT", stored_data)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "The account number you entered is invalid. Please check and try again later."
                menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "FNDAMT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        ft_processor.libhandler.writelog(logfile, f"Extract: {extract}")
        extract_reply = extract.split('|')
        acct_num = extract_reply[1]
        credit_acct_num = extract_reply[2]
        amount = userdata
        stored_data = f"{extract}|{amount}"

        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "FNDAMT", extract)
            ft_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif amount.isdigit():
            if len(userdata) < 1 or len(userdata) > 4 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "FNDAMT", extract)

            else:
                message = f"Your account {acct_num} will be debited with Ghc{amount} to credit account number {credit_acct_num}." \
                          f"^Is this OK?^1. Yes^2. No"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")
                session_processor.store_menupoint.store_menupoint(request, "FNDCNF", stored_data)

    elif last_position == "FNDCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        ft_processor.libhandler.writelog(logfile, f"Extract: {extract}")
        extract_reply = extract.split('|')
        service_id = extract_reply[0]
        acct_num = extract_reply[1]
        credit_acct_num = extract_reply[2]
        amount = extract_reply[3]
    
        trxid = gen_trx()

        if userdata == "1":
            narration = "Mesika Test Transfer"
            payload = {
                "sending_account": acct_num,
                "receiving_account": credit_acct_num,
                "amount": amount,
                "narration": narration,
                "transaction_id": trxid
}
         #   payload = {"sender_msisdn": msisdn, "credit_account": credit_acct_num, "debit_account_id": acct_id,
         #              "amount": amount, "service_id": service_id}
            ft_processor.libhandler.writelog(logfile, f"Payload: {payload}")

            url = "https://10.85.85.65:34799/api/adehyeman-quipu/v1/funds-transfer/"
            rc = requests.post(url, json=payload, verify=False)
            ft_processor.libhandler.writelog(logfile, f"Response: {rc}.json()")
            # response = call_api(payload, "cowrybank", "processTransaction")
            # status = response['status']
            
            response = rc.json()
            status = response['status']
          
            if status == 200:
                refid = response['response'][0]['referenceId']
                message = f"Funds transfer of Ghc {amount} to account number {credit_acct_num} is being processed.^Ref ID is {refid}."
                menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Funds transfer failed. Please try again later"
                menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif userdata == "2":
            message = "Funds transfer has been cancelled"
            menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
            ft_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            data = ""
            menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    return menu_response

