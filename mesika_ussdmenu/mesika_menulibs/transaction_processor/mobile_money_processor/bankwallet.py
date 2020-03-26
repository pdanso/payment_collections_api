import transaction_processor.mobile_money_processor as momo_processor
import core_processor
import session_processor
import api_processor
import requests

import json

logfile = "bank_to_wallet"



def momo_credit(request, url, bank_code, data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "MCRCHG":  # list all the momo channels available
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
        session_processor.store_menupoint.store_menupoint(request, "MCRTME", str_conv)
        momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MCRTME":  # get account details, skips to next session if acct count == 1
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        momo_list = json.loads(extract)
        momo_id = momo_list[sel]['id']
        momo_name = momo_list[sel]['name']

        stored_data = f"{momo_id}|{momo_name}"
        payload = {"msisdn": msisdn}

        # url = f"https://demo.mesika.org:5000/api/democbs/get_balance/"
        # response = requests.get(url=url, json=payload, verify=False)
        # response = response.json()
        # momo_processor.libhandler.writelog(logfile, f"Response: {response}")
        #
        # balance = response['details']['balance']
        # acct_num = response['details']['acctnumber']
        # status = response['status']
        #
        # stored_data = f"{stored_data}|{balance}|{acct_num}"
        # momo_processor.libhandler.writelog(logfile, f"Storeddata: {stored_data}")

        # acct_response = self.getAccountlist(bank_id, url)

        account_results = {"status": 200, "count": 1, "account_list": [{"id": 1, "account_number": "12345987"},
                                                                       {"id": 2, "account_number": "09876789878"}]}

        # acct_response = self.request_account(bank_id, url, service_id, data="", next_position="",
        #                                      goback_message="", module="")




            # if acc_count >= 1:
        message = ""
        count = 0
        for n in account_results['account_list']:
            acct_id = n['id']
            source_account = n['account_number']
            # count += 1
            message += str(count) + '. ' + str(source_account)+ '^'

        str_conv = json.dumps(account_results['account_list'])
        stored_data = f"{str_conv}?{stored_data}"


        message = f"Please select an Account Number for this transaction^1. {message}"  # ^0. Go back"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MCRACC", stored_data)
        momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MCRACC":
        sel0 = userdata
        # sel0 = int(sel0)
        # sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        momo_processor.libhandler.writelog(logfile, f"{extract}")

        message = "Please Enter the Amount Eg: 5"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MCRAMT", extract)
        momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MCRAMT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        amount = userdata
        momo_processor.libhandler.writelog(logfile, f"Amount entered: {amount}")

        extract_reply = extract.split('|')
        momo_name = extract_reply[1]

        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "MCRAMT", extract)
            momo_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif amount.isdigit():
            if len(userdata) < 1 or len(userdata) > 4 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MCRAMT", extract)

            else:
                stored_data = f"{extract}|{amount}"

                message = f"Please enter the phone number to send {momo_name} momo to. Eg: 0503987678 "
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MCRNUM", stored_data)
                momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MCRNUM":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        momo_num = userdata
        momo_processor.libhandler.writelog(logfile, f"Momo Num entered: {momo_num}")

        extract_reply = extract.split('|')
        balance = extract_reply[2]
        acct_num = extract_reply[3]
        amount = extract_reply[4]
        momo_name = extract_reply[1]

        if not momo_num.isdigit():
            message = "Phone Number entered is Invalid. Please enter again.Eg: 0503987678"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "MCRNUM", extract)
            momo_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif momo_num.isdigit():
            if len(userdata) < 10 or len(userdata) > 10:
                message = "Please check phone number entered!^Enter phone number again. Eg: 0503987678"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MCRNUM", extract)

            elif len(userdata) == 10:
                ph_num = momo_num.rstrip('\t\n\r')
                ph_num = ph_num.lstrip('0')
                source_account = '233' + ph_num
                momo_processor.libhandler.writelog(logfile, f"PH_NUM: {source_account}")
                stored_data = f"{extract}|{source_account}"

                message = f"Your Account will be debited with Ghc {amount} to send {momo_name} momo to {momo_num}^" \
                          f"Is this correct?^1. Yes^2. No "
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MCRCNF", stored_data)
                momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MCRCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        momo_num = userdata
        momo_processor.libhandler.writelog(logfile, f"Momo Num entered: {momo_num}")

        extract_reply = extract.split('|')
        balance = extract_reply[2]
        acct_num = extract_reply[3]
        amount = extract_reply[4]
        momo_name = extract_reply[1]
        source_account = extract_reply[5]

        if userdata == "1":

            message = f"{momo_name} momo worth Ghc {amount} will be sent to {msisdn} shortly."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            momo_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif userdata == "2":
            message = f"You have cancelled this transaction. Your account will not be debited."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            momo_processor.libhandler.writelog(logfile, f"Message: {message}")


    else:
        menu_response = core_processor.unknown_option.thrown_unknown_option(request, data, goback_message)

    return menu_response

