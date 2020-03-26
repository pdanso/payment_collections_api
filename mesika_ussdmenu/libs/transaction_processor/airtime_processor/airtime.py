import transaction_processor.airtime_processor as airtime_processor
import transaction_processor.account_processor as account_processor
import service_processor
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
        airtime_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "AIRWHO":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        airtime_processor.libhandler.writelog(logfile, f"sel = {sel}")

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        airtime_processor.libhandler.writelog(logfile, f"Extract: {extract}")

        extract_reply = extract.split('|')
        airtime_list = extract_reply[0]
        service_id = extract_reply[1]

        airtime_type = json.loads(airtime_list)
        airtime_id = airtime_type[sel]['id']
        airtime_name = airtime_type[sel]['name']
        airtime_processor.libhandler.writelog(logfile, f"Airtime: {airtime_id}. {airtime_name}")

        stored_data = f"{service_id}|{airtime_id}"
        airtime_processor.libhandler.writelog(logfile, f"Stored data: {stored_data}")

        menu_response = service_processor.get_merchantlist(url, request, stored_data, "AIRTME", goback_message)

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
        airtime_processor.libhandler.writelog(logfile, f"Merchant: {merchant_id}. {merchant_name}")

        extract_reply = rest.split('|')
        airtime_id = extract_reply[1]
        service_id = extract_reply[0]

        stored_data = f"{rest}|{merchant_name}"

        account_results = account_processor.get_accountlist(url, request,
                                                            stored_data, "AIRAMT", goback_message)

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
        airtime_processor.libhandler.writelog(logfile, f"Id: {acct_id} and num: {acct_num}")

        extract_reply = rest.split('|')
        airtime_id = extract_reply[1]
        service_id = extract_reply[0]
        merchant_name = extract_reply[2]

        stored_data = f"{rest}|{acct_id}"

        if airtime_id == "1":
            message = "Please enter amount Eg: 5"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "AIRSLF", stored_data)
            airtime_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif airtime_id == "2":
            message = "Please enter phone number to topup"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "AIRPHN", stored_data)
            airtime_processor.libhandler.writelog(logfile, f"Message: {message}")

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
            airtime_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif other_msisdn.isdigit():
            if len(userdata) < 10 or len(userdata) > 10:
                message = "Please check phone number entered!^Enter phone number again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIRPHN", extract)

            elif len(userdata) == 10:
                ph_num = other_msisdn.rstrip('\t\n\r')
                ph_num = ph_num.lstrip('0')
                source_account = '233' + ph_num
                airtime_processor.libhandler.writelog(logfile, f"PH_NUM: {source_account}")
                stored_data = f"{extract}|{source_account}"

                message = "Please enter amount to topup Eg: 5 "
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "AIRENT", stored_data)
                airtime_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "AIRENT":
        amount = userdata
        airtime_processor.libhandler.writelog(logfile, f"AMOUNT: {amount}")

        stored_data = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = stored_data.split('|')
        other_msisdn = extract_reply[4]
        airtime_processor.libhandler.writelog(logfile, f"Stored data: {stored_data}")

        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "AIRENT", stored_data)
            airtime_processor.libhandler.writelog(logfile, f"Message = {message}")

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
                airtime_processor.libhandler.writelog(logfile, f"Message: {message}")

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
                core_processor.goto_start.goto_start(request, message, "", goback_message)
                airtime_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Airtime topup request failed. Please ty again"
                core_processor.goto_start.goto_start(request, message, "", goback_message)
                airtime_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif userdata == "2":
            message = "Airtime topup has been cancelled."
            core_processor.goto_start.goto_start(request, message, "", goback_message)
            airtime_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

    else:
        menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

    return menu_response
