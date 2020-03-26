import transaction_processor.loans_processor as loans_processor
import core_processor
import session_processor
import api_processor
import trxid_processor.get_alph_id

import json
import requests

logfile = "loans"


def loans(request, msg, bank_code, last_position, pos, goback_message):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "LONSTA":
        # start of loans session

        # check if client is on local api

        url = f"https://10.85.85.80:34567/api/mobile-loans/v2/customer/check-mobile-profile/{msisdn}"
        result = requests.get(url, verify=False, timeout=10)
        results = result.text
        loans_processor.libhandler.writelog(logfile, f"Response: {results}")

        # obtaining status code and customer status

        respo = results.split(',')
        first_resp = respo[0]
        response = first_resp.split(':')
        status = response[1]

        cust_respo = respo[2]
        response = cust_respo.split(':')
        c_status = response[1]
        loans_processor.libhandler.writelog(logfile, f"Status - {status} and customer_status - {c_status}")

        cust_sta = c_status.split('"')
        loans_processor.libhandler.writelog(logfile, f"Message: {cust_sta[1]}")

        cust_status = cust_sta[1]
        stored_data = cust_status

        if cust_status == "ACTIVATED" or cust_status == "INTERESTED":
            message = f"{msg}^Please select an option:^1. " \
                      f"Request for Loan" \
                      f"^2. Make Enquiries^3. Terms and Conditions"
            menu_response = f"{networkid}|more|{msisdn}|{sessionid}|{message}"
            loans_processor.libhandler.writelog(logfile, f"Message: {menu_response}")
            session_processor.store_menupoint.store_menupoint(request, "LONOPT", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif cust_status == 'DISABLED' or cust_status == "DISABLE":
            # account has been disabled and can
            message = f"Your account has been disabled.Please contact {bank_code} for more information."
            menu_response = core_processor.make_response.make_response(request, "end", message)
            loans_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif cust_status == 'BLACKLISTED' or cust_status == "BLACKLIST":
            message = f"Your account has been disabled.Please contact {bank_code} for more information."
            menu_response = core_processor.make_response.make_response(request, "end", message)
            loans_processor.libhandler.writelog(logfile, f"Message: {message}")


        else:
            # could be first time viewers
            # # check the network id of phone number dialing the menu
            loans_processor.libhandler.writelog(logfile, f"Network [ {networkid} ]")

            if networkid == 'MTN_GH_DIRECT':
                netwid = '38'

            else:
                netw = networkid.lstrip('GH4HUB_')
                network = netw.rstrip('_GH')
                loans_processor.libhandler.writelog(logfile, f"Network strip [ {network} ]")

                if network == 'VODAFONE' or network == 'Vodafone':
                    netwid = '37'

                elif network == "AIRTEL" or network == "Airtel" or network == "TIGO" or network == "Tigo":
                    netwid = '39'

                elif network == 'MTN' or network == 'Mtn':
                    netwid = '38'

                elif networkid == 'MTN_GH_DIRECT':
                    netwid = '38'

                else:
                    netwid = ''

            loans_processor.libhandler.writelog(logfile, f"Pay test ")

            payload = {
                'trx': f"{trxid_processor.get_alph_id.get_alph_trxid(bank_code)}",
                # "trx": "adb8909090",
                'mno_id': netwid,
                'msisdn': msisdn
            }
            loans_processor.libhandler.writelog(logfile, f"Payload [ {payload} ]")

            # call postNameEnquiry
            # verifying the msisdn
            url = "http://10.85.85.60:24766/cbs/adb/ghipss-momo/postNameEnquiry/"
            response = requests.post(url, json=payload, verify=False)

            loans_processor.libhandler.writelog(logfile, f"{response.text}")

            extract_reply = response.text.split('|')
            extract_split = extract_reply[0]
            status_split = extract_split.split(':')
            status = status_split[1]

            # phone number from menu dial is registered on momo

            if status == "SUCCESSFUL" or status == "SUCCESS":

                # partially register their phone number to move status to interested.
                url = f"https://10.85.85.80:34567/api/mobile-loans/v2/customer/register-mobile-number/{msisdn}/"
                loans_processor.libhandler.writelog(logfile, f"Url: {url}")
                re = requests.post(url, verify=False, timeout=10)
                loans_processor.libhandler.writelog(logfile, f"Re: {re}")
                resp = re.text
                loans_processor.libhandler.writelog(logfile, f"Resp: {resp}")

                respo = resp.split(',')
                respo1 = respo[0]
                response = respo1.split(':')

                stat = response[1]
                status = int(stat)

                cust_respo1 = respo[3]
                response = cust_respo1.split(':')
                c_status = response[1]
                loans_processor.libhandler.writelog(logfile, f"Status - {status} and customer_status - {c_status}")

                cust_sta = c_status.split('"')
                loans_processor.libhandler.writelog(logfile, f"Message: {cust_sta[1]}")

                cust_status = cust_sta[1]
                stored_data = cust_status

                if status == 200 or status == 406:
                    message = f"Welcome to {bank_code} Mobile Loans by MeSIKA.^Please select an option:^1. " \
                              f"Request for Loan" \
                              f"^2. Make Enquiries^3. Terms and Conditions"
                    menu_response = f"{networkid}|more|{msisdn}|{sessionid}|{message}"
                    loans_processor.libhandler.writelog(logfile, f"Message: {menu_response}")
                    session_processor.store_menupoint.store_menupoint(request, "LONOPT", stored_data)
                    loans_processor.libhandler.writelog(logfile, f"Message: {message}")

                else:
                    message = "Your mobile number could not be registered. Please try again later."
                    menu_response = core_processor.make_response.make_response(request, "end", message)
                    loans_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                # phone number from menu dial is not registered on momo
                message = "Kindly dial with a registered mobile money number."
                menu_response = core_processor.make_response.make_response(request, "end", message)
                loans_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "LONOPT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        status = extract
        stored_data = status

        if userdata == "1":  # Request for Loan
            message = "Terms and Conditions:^^No collateral required.^Monthly Interest rate of 3.5%.^" \
                      "Enter 0 to Continue"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONTER", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif userdata == "2":  # enquiries
            message = "Please select an option:^1. Loan Balance^2. Loan Requirements^3. Loan Charges"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONENQ", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif userdata == "3":
            # submit request for sms to be sent
            # call charges function
            message = "Terms and Conditions:^No collateral required.^Interest rate of 3.5% per month.^" \
                      "4.5% of loan amount charged as processing fee.^Vist adomsl.mesika.org/ts to review " \
                      "this in full."
            menu_response = core_processor.make_response.make_response(request, "end", message)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, stored_data, goback_message)

    # ================ Session begins ========================================

    elif last_position == "LONTER":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        cust_status = extract
        stored_data = cust_status

        if userdata == "0":
            message = "4.5% of loan amount as processing fee.^Vist adomsl.mesika.org/ts to review this in " \
                      "full.^Enter 0 to continue."
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONCON", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, stored_data, goback_message)

    elif last_position == "LONCON":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        cust_status = extract
        stored_data = cust_status

        if userdata == "0":
            message = "Are you a government worker?^1. Yes^2. No"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONGOV", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, stored_data, goback_message)

    elif last_position == "LONGOV":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        cust_status = extract
        stored_data = cust_status

        if userdata == "1":
            gov = 1

        elif userdata == "2":
            gov = 0

        else:
            gov = ""

        if cust_status == "INTERESTED" or cust_status == "INTEREST":
            # id_name to be passed to api

            url = f"https://10.85.85.80:34567/api/mobile-loans/v2/customer/get-id-types/"
            re = requests.get(url, verify=False, timeout=10)
            resp = re.text
            loans_processor.libhandler.writelog(logfile, f"Response: {resp}")
            res = json.loads(resp)

            # obtaining status code and customer status

            status = res['status']
            id_list = res['id_type_list']

            loans_processor.libhandler.writelog(logfile, f"Status - {status} and List -{id_list} ")

            if status == 200:
                message = ""
                count = 0
                for n in id_list:
                    id_uuid = n['id_uuid']
                    id_name = n['id_name']
                    count += 1
                    message += str(count) + '. ' + str(id_name) + '^'

                str_conv = json.dumps(id_list)
                stored_data = f"{str_conv}|{cust_status}|{gov}"

                message = f"Select your ID Type^{message}"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "LONTYP", stored_data)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

            else:
                message = "List of IDs cannot be displayed right now. Kindly try again later."
                menu_response = core_processor.goto_start(message, stored_data, goback_message)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif cust_status == "ACTIVATED" or cust_status == "ACTIVE":
            # status|gov|id_type|id_number|staff_id
            id_type = ""
            id_number = ""
            staff_id = ""
            stored_data = f"{cust_status}|{gov}|{id_type}|{id_number}|{staff_id}"
            message = f"Enter amount Eg: 5"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONAMT", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = f"You are not registered for this service. Kindly contact {bank_code}"
            menu_response = core_processor.goto_start(message, stored_data, goback_message)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

    # ================= Registration ========================================= """

    elif last_position == "LONTYP":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('|')

        list = extract_reply[0]
        cust_status = extract_reply[1]
        gov = extract_reply[2]

        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        id_list = json.loads(list)

        id_uuid = id_list[sel]['id_uuid']
        id_name = id_list[sel]['id_name']
        loans_processor.libhandler.writelog(logfile, f"ID Type = {id_uuid}")

        stored_data = f"{cust_status}|{gov}|{id_uuid}"
        message = f"Enter your {id_name} Number"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "LONNUM", stored_data)
        loans_processor.libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "LONNUM":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('|')

        gov = extract_reply[1]

        id_num = userdata

        stored_data = f"{extract}|{id_num}"

        if gov == "0":
            staff_id = ""
            stored_data = f"{stored_data}|{staff_id}"
            message = "Enter amount Eg: 5"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONAMT", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif gov == "1":
            message = "Enter your Staff ID"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONSTF", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, stored_data, goback_message)

    elif last_position == "LONSTF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        staff_id = userdata

        stored_data = f"{extract}|{staff_id}"

        message = "Enter amount Eg: 5"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "LONAMT", stored_data)
        loans_processor.libhandler.writelog(logfile, f"Message = {message}")

    # ================= Completing loan request ============================== """

    elif last_position == "LONAMT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        stored_data = extract

        amount = userdata

        if not amount.isdigit():
            message = "Value entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONAMT", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif amount.isdigit():
            if amount == "0":
                message = "Amount entered cannot be GHS 0^Kindly enter amount again."
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "LONAMT", stored_data)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

            else:
                stored_data = f"{extract}|{amount}"
                message = "Enter your expected monthly income Eg: 10056"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "LONINC", stored_data)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "LONINC":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        stored_data = extract

        income = userdata
        loans_processor.libhandler.writelog(logfile, f"Amount = {type(income)}")

        if not income.isdigit():
            message = "Value entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONINC", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif income.isdigit():
            if income == "0":
                message = "Your income cannot be GHS 0^Kindly enter your monthly income again."
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "LONINC", stored_data)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

            # elif income > 0:
            else:
                stored_data = f"{extract}|{income}"

                message = f"Enter period for loan in months.^Limit is 36 months."
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "LONACT", stored_data)
                loans_processor.libhandler.writelog(logfile, f"Message: {message}")

                # else:
                #     message = "Value entered is Invalid. Please enter again"
                #     menu_response = core_processor.make_response.make_response(request, "more", message)
                #     session_processor.store_menupoint.store_menupoint("LONAMT|{stored_data}")
                #     loans_processor.libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "LONACT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('|')
        loans_processor.libhandler.writelog(logfile, f"Extract: {extract_reply}")

        status = extract_reply[0]
        amount = extract_reply[5]
        loans_processor.libhandler.writelog(logfile, f"Extract: {status} and {amount}")

        stored_data = extract

        tenure = int(userdata)
        # if not num.isdigit():
        #     message = "Value entered is Invalid. Please enter again"
        #     menu_response = core_processor.make_response.make_response(request, "more", message)
        #     session_processor.store_menupoint.store_menupoint("LONACT|{stored_data}")
        #     loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        # elif num.isdigit():
        if tenure <= 0 or tenure > 36:
            message = "Value entered is not within the valid period for this loan.^Kindly enter period " \
                      "again."
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "LONACT", stored_data)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif tenure > 1 or tenure <= 36:
            stored_data = f"{extract}|{tenure}"

            # list charges

            url = "https://10.85.85.80:34567/api/mobile-loans/v2/charges/list-charges/"
            re = requests.get(url, verify=False, timeout=10)
            resp = re.text
            loans_processor.libhandler.writelog(logfile, f"Response: {resp}")

            respo = resp.split(',')
            first_resp = respo[0]
            first_respo1 = first_resp.split(':')
            status = first_respo1[1]

            status = 200
            if status == 200:
                # calculate charge

                amt = float(amount)

                # total = processing_fee * amt + service_fee
                total = 0.055 * amt
                loans_processor.libhandler.writelog(logfile, f"Total Charge = {total}")

                total_charge = "%.2f" % total
                loans_processor.libhandler.writelog(logfile, f"Charge format = {total_charge}")

                final = amt - float(total_charge)
                final_amount = "%.2f" % final

                message = f"Your charge on this loan request for {tenure} months is GHS{total_charge}" \
                          f"^You will receive a total of GHS{final_amount} Continue?^1. Yes^2. No"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "LONCNF", stored_data)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

            else:
                message = "Charge cannot be displayed on this transaction. Please try again later"
                menu_response = core_processor.goto_start(message, status, goback_message)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "LONCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('|')

        # if registered, pass without id type and number

        cust_status = extract_reply[0]
        gov = extract_reply[1]
        id_type = extract_reply[2]
        id_number = extract_reply[3]
        staff_id = extract_reply[4]
        amount = extract_reply[5]
        income = extract_reply[6]
        tenure = extract_reply[7]

        loans_processor.libhandler.writelog(logfile, f"Extract: {extract}")

        if userdata == "1":
            first_application = 0

            if cust_status == 'INTERESTED':
                first_application = 1

            elif cust_status == 'ACTIVATED':
                first_application = 0

            payload = {
                "msisdn": msisdn,
                "is_government_worker": gov,
                "id_type": id_type,
                "id_number": id_number,
                "staff_id": staff_id,
                "amount": amount,
                "monthly_income": income,
                "tenure": tenure,
                "first_application": first_application
            }
            loans_processor.libhandler.writelog(logfile, f"Payload: {payload}")

            message = f"Your loan application of GHS {amount} for {tenure} months has been received.^" \
                      f"You will receive a notification in less than 24 hours."
            menu_response = core_processor.goto_start(message, cust_status, goback_message)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

            url = "https://10.85.85.80:34567/api/mobile-loans/v2/loans/apply/"
            re = requests.post(url, json=payload, verify=False, timeout=10)

            response = re.json()
            loans_processor.libhandler.writelog(logfile, f"Response: {response}")

            # respo = resp.split(',')
            # first_resp = respo[0]
            # first_respo1 = first_resp.split(':')
            # status = first_respo1[1]

            # else:
            #     message = "You do not qualify for this loan.Please try again "
            #     menu_response = core_processor.goto_start(message, cust_status, goback_message)
            #     loans_processor.libhandler.writelog(logfile, f"Message = {message}")

            # process loan

        elif userdata == "2":
            message = "Your loan application has been cancelled.^Your request will not be submitted."
            menu_response = core_processor.goto_start(message, cust_status, goback_message)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, cust_status, goback_message)

    # ================= Enquiries ============================================

    elif last_position == "LONENQ":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        status = extract
        stored_data = status

        if userdata == "1":
            # loan balance
            # get the balances for the loans
            url = f"https://10.85.85.80:34567/api/mobile-loans/v2/loans/checkBalance/{msisdn}/"
            loans_processor.libhandler.writelog(logfile, f"Balance Endpoint: {url}")
            re = requests.get(url, verify=False, timeout=10)
            resp = re.text
            loans_processor.libhandler.writelog(logfile, f"Response: {resp}")

            respo = resp.split(',')
            first_resp = respo[0]
            first_respo1 = first_resp.split(':')
            status = first_respo1[1]
            loans_processor.libhandler.writelog(logfile, f"Balance Status: {type(status)}")
            status = int(status)
            # status = 200

            if status == 200:
                message = "Your loan balance is GHS 400.76"
                menu_response = core_processor.goto_start(message, stored_data, goback_message)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

            elif status == 404:
                message = "You have not applied for a loan yet."
                menu_response = core_processor.goto_start(message, stored_data, goback_message)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")

            else:
                message = "Your balance cannot be viewed right now. Please try again later."
                menu_response = core_processor.goto_start(message, stored_data, goback_message)
                loans_processor.libhandler.writelog(logfile, f"Message = {message}")
                # if status == "ACTIVATED" or status == "ACTIVE":
                #
                #
                # elif status == "INTERESTED" or status == "INTEREST":
                #     message = f"You do not have any loans with {bank_code}."
                #     menu_response = core_processor.goto_start(message, stored_data, goback_message)
                #     loans_processor.libhandler.writelog(logfile, f"Message = {message}")
                #
                # else:
                #     message = "You do not have any loan yet."
                #     menu_response = core_processor.goto_start(message, stored_data, goback_message)
                #     loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif userdata == "2":
            # requirements
            message = "To request for a loan, you need:^1. Valid government staff id^2. " \
                      "Valid identification number^3. Registered Mobile Money number for disbursement^"
            menu_response = core_processor.goto_start(message, stored_data, goback_message)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif userdata == "3":
            # list charges
            url = "https://10.85.85.80:34567/api/mobile-loans/v2/charges/list-charges/"
            re = requests.get(url, verify=False, timeout=10)
            resp = re.text
            loans_processor.libhandler.writelog(logfile, f"Response: {resp}")

            respo = resp.split(',')
            first_resp = respo[0]
            first_respo1 = first_resp.split(':')
            status = first_respo1[1]

            # message = f"Loan Charges:^1. Service Fee - {service_fee}% of amount ^2. Bank Processing Fee - " \
            #           f"{pro_fee}% of amount^"
            message = "Charges:^5.5% of amount."
            menu_response = core_processor.goto_start(message, stored_data, goback_message)
            loans_processor.libhandler.writelog(logfile, f"Message = {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, stored_data, goback_message)  #

    return menu_response
