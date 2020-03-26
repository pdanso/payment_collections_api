import transaction_processor.mobile_money_processor as momo_processor
import core_processor
import session_processor
import api_processor

import json

logfile = "wallet_to_bank"


def momo_debit(request, url, bank_code, data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "MDBCHG":  # list all the momo channels available
        message = ""
        count = 0

        # payload = {}
        # response = self.core_processor.call_api(url, payload, "cowrypay", "getMoMoList")
        # status = response['status']

        response = {"reason": "hello", "momo": [{"id": 1, "name": "MTN"},
                                                {"id": 2, "name": "AirtelTigo"},
                                                {"id": 3, "name": "Vodafone"}]}

        for n in response['momo']:
            momo_id = n['id']
            momo_name = n['name']
            count += 1
            message += str(count) + '. ' + str(momo_name) + '^'

        str_conv = json.dumps(response['momo'])
        message = f"Please select a network:^{message}"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MDBTME", str_conv)
        momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MDBTME":  # get account details, skips to next session if acct count == 1
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        momo_list = json.loads(extract)
        momo_id = momo_list[sel]['id']
        momo_name = momo_list[sel]['name']

        stored_data = f"{momo_id}|{momo_name}"

        message = f"Please enter the phone number to transfer {momo_name} momo from . Eg: 0503987678 "
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MDBNUM", stored_data)
        momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MDBNUM":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        momo_num = userdata
        momo_processor.libhandler.writelog(logfile, f"Momo Num entered: {momo_num}")

        if not momo_num.isdigit():
            message = "Phone Number entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "MDBNUM", extract)
            momo_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif momo_num.isdigit():
            if len(userdata) < 10 or len(userdata) > 10:
                message = "Please check phone number entered!^Enter phone number again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MDBNUM", extract)

            elif len(userdata) == 10:
                ph_num = momo_num.rstrip('\t\n\r')
                ph_num = ph_num.lstrip('0')
                source_account = '233' + ph_num
                momo_processor.libhandler.writelog(logfile, f"PH_NUM: {source_account}")
                stored_data = f"{extract}|{source_account}"

                message = "Please Enter the Amount Eg: 5"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MDBAMT", stored_data)
                momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MDBAMT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        amount = userdata
        momo_processor.libhandler.writelog(logfile, f"Amount entered: {amount}")

        extract_reply = extract.split('|')
        momo_name = extract_reply[1]

        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "MDBAMT", extract)
            momo_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif amount.isdigit():
            if len(userdata) < 1 or len(userdata) > 4 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MDBAMT", extract)

            else:
                stored_data = f"{extract}|{amount}"

                account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "12345987"},
                                                                               {"id": 2,
                                                                                "account_number": "09876789878"}]}

                # acct_response = self.request_account(bank_id, url, service_id, data="", next_position="",
                #                                      goback_message="", module="")

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
                        session_processor.store_menupoint.store_menupoint(request, "MDBACC", stored_data)
                        momo_processor.libhandler.writelog(logfile, f"Message: {message}")

                    elif account_results['count'] == 1:
                        data = ""
                        # menu_response = self.request_account(bank_id, url, service_id, data, f"MOMDST|{momo_id}",
                        #                                      goback_message, module)

                    else:
                        menu_response = core_processor.unknown_option.thrown_unknown_option(request, data,
                                                                                            goback_message)

                else:
                    message = "Account Numbers cannot be viewed right now. Please try again later"
                    menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
                    momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MDBACC":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('?')
        acc_list = extract_reply[0]
        rest = extract_reply[1]

        acct_list = json.loads(acc_list)

        acct_id = acct_list[sel]['id']
        acct_num = acct_list[sel]['account_number']
        momo_processor.libhandler.writelog(logfile, f"Id: {acct_id} and num: {acct_num}")

        stored_data = f"{rest}|{acct_id}|{acct_num}"

        extra = rest.split('|')
        momo_name = extra[1]
        momo_num = extra[2]
        amount = extra[3]

        message = f"Your {momo_name} account {momo_num} will be debited with Ghc {amount} to send to account number" \
                  f" {acct_num}.^" \
                  f"Is this correct?^1. Yes^2. No "
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MDBCNF", stored_data)
        momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MDBCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        extra = extract.split('|')
        momo_name = extra[1]
        momo_num = extra[2]
        amount = extra[3]
        acct_num = extra[5]

        if userdata == "1":
            message = f"Ghc {amount} will be sent to account {acct_num} from {momo_name} {momo_num} shortly."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            momo_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif userdata == "2":
            message = f"You have cancelled this transaction. Your account will not be debited"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    else:
        menu_response = core_processor.unknown_option.thrown_unknown_option(request, data, goback_message)
    return menu_response
