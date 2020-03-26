import transaction_processor.airtime_processor as trans_airtime
import transaction_processor.account_processor as trans_account
import core_processor
import session_processor
import api_processor

import json
import requests
import datetime

logfile = "airtime"


def airtime(request, url, data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "AIRSUB":

        response = [{"id": 1, "name": "Topup for myself"}, {"id": 2, "name": "Topup Another Number"}]
        str_conv = json.dumps(response)
        data = f"{str_conv}|{data}"

        message = "Select type of transfer:^1. Topup for myself^2. Topup Another Number"
        session_processor.store_menupoint.store_menupoint(request, "AIRWHO", data)
        menu_response = core_processor.make_response.make_response(request, "more", message)
        trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "AIRWHO":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        trans_airtime.libhandler.writelog(logfile, f"sel = {sel}")

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        trans_airtime.libhandler.writelog(logfile, f"Extract: {extract}")

        extract_reply = extract.split('|')
        airtime_list = extract_reply[0]
        service_id = extract_reply[1]

        airtime_type = json.loads(airtime_list)
        airtime_id = airtime_type[sel]['id']
        airtime_name = airtime_type[sel]['name']
        trans_airtime.libhandler.writelog(logfile, f"Airtime: {airtime_id}. {airtime_name}")

        stored_data = f"{service_id}|{airtime_id}"
        trans_airtime.libhandler.writelog(logfile, f"Stored data: {stored_data}")

        response = {"reason": "hello", "merchants": [{"id": 1, "name": "MTN"},
                                                    {"id": 2, "name": "AirtelTigo"},
                                                    {"id": 3, "name": "Vodafone"}]}

        # payload = {}
        # response = api_processor.api_json.api_js(url, payload, "cowrybank", "getMerchantlist")
        # status = response['status']
        status = 200

        if status == 200:
            message = ""
            count = 0
            for n in response['merchants']:
                merchant_id = n['id']
                merchant_name = n['name']
                count += 1
                message += str(count) + '. ' + str(merchant_name) + '^'

            str_conv = json.dumps(response['merchants'])

            stored_data = f"{stored_data}?{str_conv}"
            message = f"Please select a network:^{message}"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            trans_airtime.libhandler.writelog(logfile, f"Message: {message}")
            session_processor.store_menupoint.store_menupoint(request, "AIRTME", stored_data)

        else:
            message = "Merchant list cannot be displayed right now. Please try again later"
            msg = f"{message}^Enter 1 for the Main Menu or 2 for Customer Care."
            menu_response = core_processor.make_response.make_response(request, "more", msg)
            session_processor.store_session.store_session(msisdn, sessionid, networkid, "GOBACK")
            trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "AIRTME":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('?')
        merchant_list = extract_reply[1]
        rest = extract_reply[0]

        merchant = json.loads(merchant_list)
        merchant_id = merchant[sel]['id']
        merchant_name = merchant[sel]['name']
        trans_airtime.libhandler.writelog(logfile, f"Merchant: {merchant_id}. {merchant_name}")

        extract_reply = rest.split('|')
        airtime_id = extract_reply[1]
        service_id = extract_reply[0]

        stored_data = f"{rest}|{merchant_name}"

        # account_results = trans_account.request_accountlist(request, url, service_id, stored_data, "",
        #                                                              goback_msg)
        account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "1000800051501"},
                                                                       {"id": 2, "account_number": "2000100611001"}]}


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
                    message += str(count) + '. ' + str(source_account)+ '^'

                str_conv = json.dumps(account_list)
                stored_data = f"{str_conv}?{stored_data}"

                message = f"Please select an Account Number for this transaction^{message}"  # ^0. Go back"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIRAMT", stored_data)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Account numbers cannot be displayed right now. Please try again later"
                menu_response = core_processor.goto_start.goto_start(request, message, goback_message)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = "Account numbers cannot be displayed right now. Please try again later"
            menu_response = core_processor.goto_start.goto_start(request, message, goback_message)
            trans_airtime.libhandler.writelog(logfile, f"Message: {message}")


    elif last_position == "AIRAMT":
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
        trans_airtime.libhandler.writelog(logfile, f"Id: {acct_id} and num: {acct_num}")

        extract_reply = rest.split('|')
        airtime_id = extract_reply[1]
        service_id = extract_reply[0]
        merchant_name = extract_reply[2]

        stored_data = f"{rest}|{acct_id}"

        if airtime_id == "1":
            message = "Please enter amount Eg: 5"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "AIRSLF", stored_data)
            trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

        elif airtime_id == "2":
            message = "Please enter phone number to topup"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "AIRPHN", stored_data)
            trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

    # ========================== self =====================================================

    elif last_position == "AIRSLF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        amount = userdata
        trans_airtime.libhandler.writelog(logfile, f"Amount entered: {amount}")

        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "AIRSLF", extract)
            trans_airtime.libhandler.writelog(logfile, f"Message = {message}")

        elif amount.isdigit():
            if len(userdata) < 1 or len(userdata) > 4 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIRSLF", extract)

            else:
                stored_data = f"{extract}|{amount}"

                message = f"Your number {msisdn} will be credited with airtime of Ghc {amount}^" \
                          f"Is this correct?^1. Yes^2. No "
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIRCNF", stored_data)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "AIRCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('|')

        airtime_id = extract_reply[1]
        service_id = extract_reply[0]
        merchant_name = extract_reply[2]
        acct_id = extract_reply[3]
        amount = extract_reply[4]

        if userdata == "1":
            payload = {"msisdn": msisdn, "amount": amount, "service_id": service_id,
                       "merchant_name": merchant_name, "account_id": acct_id}
            # response = api_processor.api_json.api_json(url, payload, "cowrybank", "processTransaction")
            # status = response['status']

            status = 200
            if status == 200:
                message = f"Airtime worth Ghc {amount} will be sent to {msisdn} shortly"
                menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Airtime topup request failed. Please ty again"
                menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

        elif userdata == "2":
            message = "Airtime topup has been cancelled."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

    # ================= other =========================================

    elif last_position == "AIRPHN":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('|')

        airtime_id = extract_reply[1]
        service_id = extract_reply[0]
        merchant_name = extract_reply[2]
        acct_id = extract_reply[3]

        other_msisdn = userdata

        if not other_msisdn.isdigit():
            message = "Phone Number entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "AIRPHN", extract)
            trans_airtime.libhandler.writelog(logfile, f"Message = {message}")

        elif other_msisdn.isdigit():
            if len(userdata) < 10 or len(userdata) > 10:
                message = "Please check phone number entered!^Enter phone number again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIRPHN", extract)

            elif len(userdata) == 10:
                ph_num = other_msisdn.rstrip('\t\n\r')
                ph_num = ph_num.lstrip('0')
                source_account = '233' + ph_num
                trans_airtime.libhandler.writelog(logfile, f"PH_NUM: {source_account}")
                stored_data = f"{extract}|{source_account}"

                message = "Please enter amount to topup Eg: 5 "
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIRENT", stored_data)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "AIRENT":
        amount = userdata
        trans_airtime.libhandler.writelog(logfile, f"AMOUNT: {amount}")

        stored_data = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = stored_data.split('|')
        other_msisdn = extract_reply[4]
        trans_airtime.libhandler.writelog(logfile, f"Stored data: {stored_data}")

        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "AIRENT", stored_data)
            trans_airtime.libhandler.writelog(logfile, f"Message = {message}")

        elif amount.isdigit():
            if len(userdata) < 1 or len(userdata) > 4 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIRENT", stored_data)

            else:
                stored_data = f"{stored_data}|{amount}"

                message = f"Phone Number {other_msisdn} will be credited with Ghc {amount}^Do you want to continue?^" \
                          f"1. Yes^2. No"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIR2NF", stored_data)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "AIR2NF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('|')
        airtime_id = extract_reply[1]
        service_id = extract_reply[0]
        merchant_name = extract_reply[2]
        acct_id = extract_reply[3]
        other_msisdn = extract_reply[4]
        amount = extract_reply[5]

        if userdata == "1":
            payload = {"msisdn": other_msisdn, "amount": amount, "service_id": service_id,
                       "merchant_name": merchant_name, "account_id": acct_id}
            # response = api_processor.api_json.api_json(url, payload, "cowrybank", "processTransaction")
            # status = response['status']

            status = 200
            if status == 200:
                message = f"Airtime worth Ghc {amount} will be sent to {other_msisdn} shortly"
                menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Airtime topup request failed. Please ty again"
                menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

        elif userdata == "2":
            message = "Airtime topup has been cancelled."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

    else:
        menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

    return menu_response

