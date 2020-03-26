import transaction_processor.payment_processor as payment_processor
import core_processor
import session_processor
import api_processor

import json
import requests

logfile = "bank_payment"


def bank_pay(request, url, stored_data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "MPBENT":
        message = "Please enter Mobile Banking Phone Number Eg: 0565438908"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MPBPHN", stored_data)

    elif last_position == "MPBPHN":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        mbank_num = userdata

        if not mbank_num.isdigit():
            message = "Phone Number Entered is Invalid.^Enter your Mobile Banking Phone Number again"  # ^0. Go Back"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            payment_processor.libhandler.writelog(logfile, f"message = {message}")
            session_processor.store_menupoint.store_menupoint(request, "MPBPHN", extract)

        elif mbank_num.isdigit():
            if len(mbank_num) < 10 or len(mbank_num) > 10:
                message = "Please check phone number entered!^Enter phone number again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MPBPHN", extract)

            elif len(userdata) == 10:
                stored_data = f"{extract}|{mbank_num}"
                message = "Please enter your Mobile Banking secret PIN"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MPBPIN", stored_data)

            else:
                menu_response = core_processor.unknown_option.thrown_unknown_option(request, "", goback_message)

    elif last_position == "MPBPIN":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        mbank_pin = userdata

        extract_reply = extract.split('|')
        mbank_num = extract_reply[6]

        # payload = {"msisdn": mbank_num, "pin": mbank_pin}
        # response = self.core_processor.call_api(url, payload, "cowrybank", "customerLogin")
        # status = response['status']
        status = 200

        if status == 200:
            # account_results = self.request_account(bank_id, url, service_id, extract, last_position, goback_message)
            # payment_processor.libhandler.writelog(logfile, f"Request_account Response = {account_results}")

            # ==================== account list and count ============================

            account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "12345987098"},
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
                    stored_data = f"{str_conv}?{extract}"

                    message = f"Please select an Account Number for this transaction^{message}"  # ^0. Go back"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "MPBACC", stored_data)
                    payment_processor.libhandler.writelog(logfile, f"Message: {message}")

                else:
                    message = "Account numbers cannot be displayed right now. Please try again later"
                    menu_response = core_processor.goto_start.goto_start(request, message, goback_message)
                    payment_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Account numbers cannot be displayed right now. Please try again later"
                menu_response = core_processor.goto_start.goto_start(request, message, goback_message)
                payment_processor.libhandler.writelog(logfile, f"Message: {message}")


        else:
            message = "Invalid Credentials. Please try again later. Eg: 0561012334"
            menu_response = core_processor.goto_start.goto_start(request, "", message)
            payment_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MPBACC":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('?')
        acct_list = extract_reply[0]
        data = extract_reply[1]
        # acc_count = extract_reply[0]
        # acc_count = int(acc_count)

        # if extract_reply[0] == 1:
        #     rest = extract_reply[1]
        # extract_reply = extract.split(':')
        # service_id = extract_reply[0]
        # category_id = extract_reply[1]
        # product_id = extract_reply[2]
        # prod_name = extract_reply[3]
        # biller_num = extract_reply[4]
        # amount = extract_reply[5]
        # pay_id = extract_reply[6]
        # source_account = extract_reply[7]

        # rest = extract_reply[1]
        #
        # extract_reply = extract.split('-')

        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        payment_processor.libhandler.writelog(logfile, f"sel = {sel}")

        acct_list = json.loads(acct_list)
        payment_processor.libhandler.writelog(logfile, f"Extract = {acct_list}")

        acct_id = acct_list[sel]['id']
        source_account = acct_list[sel]['account_number']

        extract_reply = data.split('|')
        # service_id = extract_reply[0]
        # category_id = extract_reply[1]
        # product_id = extract_reply[2]
        # prod_name = extract_reply[3]
        # biller_num = extract_reply[4]
        # amount = extract_reply[5]
        # pay_id = extract_reply[6]

        product_uuid = extract_reply[0]
        product_name = extract_reply[1]
        # category_id = extract_reply[1]
        # product_id = extract_reply[2]
        # prod_name = extract_reply[3]
        biller_num = extract_reply[2]
        amount = extract_reply[3]
        pay_id = extract_reply[4]
        pay_name = extract_reply[5]
        mbank_num = extract_reply[6]
        
        stored_data = f"{extract}|{source_account}"

        # stored_data = f"{service_id}:{category_id}:{product_id}:{prod_name}:{biller_num}:{amount}:{pay_id}:{source_account}"
        prod_name = product_name.title()

        message = f"Account {source_account} will be debited with Ghc {amount} for this bill:{biller_num}." \
                  f"^Is this OK?^1.Yes^2. No"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MPBCNF", stored_data)
        payment_processor.libhandler.writelog(logfile, f"Message = {message}")


        # elif acc_count > 1:
        #     rest = extract_reply[1]
        #
        #     extract_reply = rest.split('-')
        #     acct_list = extract_reply[0]
        #     data = extract_reply[1]
        #
        #     sel0 = self.userdata
        #     sel0 = int(sel0)
        #     sel = sel0 - 1
        #     libhandler.writelog(logfile, f"sel = {sel}")
        #
        #     acct_list = json.loads(acct_list)
        #     libhandler.writelog(logfile, f"Extract = {acct_list}")
        #
        #     acct_id = acct_list[sel]['id']
        #     source_account = acct_list[sel]['account_number']
        #
        #     extract_reply = rest.split(':')
        #     service_id = extract_reply[0]
        #     category_id = extract_reply[1]
        #     product_id = extract_reply[2]
        #     prod_name = extract_reply[3]
        #     biller_num = extract_reply[4]
        #     amount = extract_reply[5]
        #     pay_id = extract_reply[6]
        #
        #     stored_data = f"{rest}:{source_account}"
        #
        #     message = f"Account {source_account} will be debited with Ghc {amount} for {prod_name}: {biller_num}." \
        #               f"^Is this OK?^1.Yes^2. No"
        #     menu_response = core_processor.make_response.make_response(request, "more", message)
        #     self.core_processor.storeSession(self.msisdn, self.sessionid, self.networkid, f"MDECNF|{stored_data}")
        #     libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "MPBCNF":
        if userdata == "1":
            extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
            payment_processor.libhandler.writelog(logfile, f"extract: {extract}")
            extract_reply = extract.split('|')

            # service_id = extract_reply[0]
            # # category_id = extract_reply[1]
            # # product_id = extract_reply[2]
            # # prod_name = extract_reply[3]
            # # biller_num = extract_reply[4]
            # amount = extract_reply[2]
            # pay_id = extract_reply[3]
            # #acct_id = extract_reply[7]
            # source_account = extract_reply[4]

            product_uuid = extract_reply[0]
            product_name = extract_reply[1]
            biller_num = extract_reply[2]
            amount = extract_reply[3]
            pay_id = extract_reply[4]
            pay_name = extract_reply[5]
            mbank_num = extract_reply[6]
            source_account = extract_reply[7]
            payment_processor.libhandler.writelog(logfile, f"EXTRACT: {extract_reply}")

            # payload = {"msisdn": self.msisdn, "biller_number": bille"r_num, "payment_method_id": pay_id,
            #            "source_account": source_account,
            #            "product_id": product_id, "amount": amount, "is_customer_paid": True, "name": "John Doe",
            #            "is_agent_paid": False}
            #
            # response = self.core_processor.call_api(url, payload, "cowrypay", "collection")
            # status = response['status']

            # status = 200
            # if status == 200:
            message = "Payment is successful.^Sms Notification with payment details will be sent to you " \
                      "shortly."
            # menu_response = self.core_processor.goto_start(message, "", goback_message)
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            payment_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

            payload = {"product_uuid": product_uuid, "payer_msisdn": msisdn, "invoice_number": biller_num,
                       "payment_method_uuid": pay_id, "payment_method": pay_name,
                       "payer_account": source_account,
                       "payer_amount": amount, "other_details": ""}
            url = "https://10.85.85.80:47777/api/digital-payment-collections/payments/post-transaction/"

            response = requests.post(url, json=payload, verify=False)
            payment_processor.libhandler.writelog(logfile, f"post-transaction Api call:{response.text}")


            # else:
            #     message = "Payment could not be completed. Please try again"
            #     menu_response = self.core_processor.goto_start(message, "", goback_message)
            #     payment_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

        elif userdata == "2":
            extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
            message = "Payment has been cancelled.^Your account will not be debited."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            payment_processor.libhandler.writelog(logfile, f"Message: {menu_response}")


        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    else:
        menu_response = core_processor.unknown_option.thrown_unknown_option(request, "", goback_message)

    return menu_response



