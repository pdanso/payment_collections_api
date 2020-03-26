import transaction_processor.funds_transfer_processor as ft_processor
import core_processor
import session_processor
import api_processor

import json

logfile = "ft_gip"


def gip(request, url, bank_code, service_id, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "GIPSUB":
        # list of banks on GIP

        gip_list = {"status": 200, "bank_list": [{"id": 26, "bank_name": "Standard Chartered", "shortname": "StanChart"},
                                                 {"id": 25, "bank_name": "Stanbic Bank", "shortname": "Stanbic"},
                                                 {"id": 2, "bank_name": "Access Bank", "shortname": "Access"},
                                                 {"id": 27, "bank_name": "Ghana Commercial Bank", "shortname": "GCB"}
                                                 ]}

        # payload = {"service_id": service_id}
        #
        # response = self.core_processor.call_api(url, payload, "cowrybank", "getSubService")
        # status = response['status']

        status = 200
        if status == 200:
            message = ""
            count = 0

            for n in gip_list['bank_list']:
                bank_id = n['id']
                bank_name = n['bank_name']
                shortname = n['shortname']
                count += 1

                message += str(bank_id) + ' - ' + str(shortname) + '^'

            str_conv = json.dumps(gip_list['bank_list'])
            message = f"Select a bank:^{message}"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "GIPSEL", str_conv)
            ft_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "GIPSEL":
        sel0 = userdata
        sel = int(sel0)
        # sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        gip_banklist = json.loads(extract)

        for n in gip_banklist:

            if sel == 26:
                bank_id = n['id']
                bank_name = n['bank_name']
                shortname = n['shortname']

                stored_data = f"{bank_id}|{bank_name}|{shortname}"

                message = f"Enter the {bank_name} account number you want to transfer funds to:"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "GIPACT", stored_data)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Bank code entered does not exist.^Enter any digit to go back to GIP list"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_session.store_session(msisdn, sessionid, networkid, "GIPSUB")
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "GIPACT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        act_num = userdata

        if not act_num.isdigit():
            message = "Account Number entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "GIPACT", extract)
            ft_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif act_num.isdigit():
            # payload = {"account_number": credit_acct_num}
            # response = call_api(payload, "cowrybank", "verifyAccountnumber")
            # status = response['status']

            status = 200
            recipient_name = "Miriam Aidoo-Mensah"

            if status == 200:
                # elikem provides details
                stored_data = f"{extract}|{act_num}|{recipient_name}"
                message = f"Please enter amount to be transferred to {recipient_name}"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "GIPAMT", stored_data)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "The account number you entered is invalid. Please check and try again later."
                menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "GIPAMT":
        amount = userdata
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "GIPAMT", extract)
            ft_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif amount.isdigit():
            if len(userdata) < 1 or len(userdata) > 4 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "GIPAMT", extract)

            else:
                account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "12345987389"},
                                                                               {"id": 2, "account_number": "09876789878"}]}

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
                        stored_data = f"{str_conv}?{extract}|{amount}"

                        message = f"Please select an Account Number for this transaction^{message}"  # ^0. Go back"
                        menu_response = core_processor.make_response.make_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "GIPACL", stored_data)
                        ft_processor.libhandler.writelog(logfile, f"Message: {message}")

                    elif account_list == 1:
                        message = ""

    elif last_position == "GIPACL":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        ft_processor.libhandler.writelog(logfile, f"sel = {sel}")

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        ft_processor.libhandler.writelog(logfile, f"Extract = {extract}")
        # extract_list = json.loads(extract)

        extract_reply = extract.split('?')
        acct_list = extract_reply[0]
        rest = extract_reply[1]

        acct_list = json.loads(acct_list)

        ft_processor.libhandler.writelog(logfile, f"Extract = {acct_list}")

        acct_id = acct_list[sel]['id']
        acct_num = acct_list[sel]['account_number']

        rest_reply = rest.split('|')
        bank_name = rest_reply[1]
        recipient_name = rest_reply[4]
        amount = rest_reply[5]

        stored_data = f"{rest}|{acct_id}"

        message = f"You are transferring GHC {amount} to {recipient_name} with account number {acct_num}" \
                  f" at {bank_name}. Is this correct?^1. Yes^2. No"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        ft_processor.libhandler.writelog(logfile, f"Message: {message}")
        session_processor.store_menupoint.store_menupoint(request, "GIPCNF", stored_data)

    elif last_position == "GIPCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        ft_processor.libhandler.writelog(logfile, f"Extract: {extract}")

        extract_reply = extract.split('|')
        bank_id = extract_reply[0]
        bank_name = extract_reply[1]
        shortname = extract_reply[2]
        recipient_acct_num = extract_reply[3]
        recipient_name = extract_reply[4]
        amount = extract_reply[5]
        acct_id =extract_reply[6]

        if userdata == "1":
            payload = {"sender_msisdn": msisdn, "credit_account": recipient_acct_num, "debit_account_id": acct_id,
                       "amount": amount, "service_id": service_id}
            ft_processor.libhandler.writelog(logfile, f"Payload: {payload}")
            # response = call_api(payload, "cowrybank", "processTransaction")
            # status = response['status']

            status = 200
            if status == 200:
                message = f"GIP transfer of Ghc {amount} to account number {recipient_name} is successful."
                menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "GIP Funds transfer failed. Please try again later"
                menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif userdata == "2":
            message = "GIP transfer has been cancelled"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            ft_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            data = ""
            menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    return menu_response
