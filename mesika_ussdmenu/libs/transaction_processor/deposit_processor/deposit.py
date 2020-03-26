import transaction_processor.deposit_processor as deposit_processor
import core_processor
import session_processor
import api_processor
import transaction_processor.transaction_id_processor as trxid_processor

logfile = "deposit"


def deposit(request, bank_code, url, service_id, last_position, pos, goback_message):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "DEPSTA":
        # call api
        message = "Please select a Financial Institution:^1. ADB^2. NIB^3. GCB^4. Stanchart^5. Stanbic^6." \
                  " Cal Bank"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_session.store_session(msisdn, sessionid, networkid, "DEPSIT")
        deposit_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "DEPSIT":
        message = "Enter account number of customer"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "DEPNUM", service_id)
        deposit_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "DEPNUM":
        acct_num = userdata
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        service_id = extract
        stored_data = f"{service_id}:{acct_num}"

        if not acct_num.isdigit():
            message = "Account number entered is invalid. Please enter account number again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "DEPNUM", extract)
            deposit_processor.libhandler.writelog(logfile, f"Message {message}")

        elif acct_num.isdigit():
            # verify account

            status = 200
            if status == 200:
                # menu_response = core_processor.request_account(bank_id, stored_data, "ACTSEL",
                #                                                "getCustomerAccountlist", cust_msisdn)
                message = "Please enter amount to be deposited E.g: 1"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "DEPAMT", stored_data)
                deposit_processor.libhandler.writelog(logfile, f"Message {message}")

            elif status == 201:  # account blocked
                message = "This account has been blocked due to irregular activities.Deposit transaction has been " \
                          "cancelled"
                menu_response = core_processor.goto_start(message, stored_data, goback_message)
                deposit_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Account does not exist"
                menu_response = core_processor.goto_start(message, stored_data, goback_message)
                deposit_processor.libhandler.writelog(logfile, f"Message {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    elif last_position == "DEPAMT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        amount = userdata

        if not amount.isdigit():
            message = "Amount entered is invalid.^Enter Amount again. Eg: 5"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "DEPAMT", extract)
            deposit_processor.libhandler.writelog(logfile, f"Message {message}")

        elif amount.isdigit():
            if len(amount) < 1 or len(amount) > 4 or amount == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "DEPAMT", extract)
                deposit_processor.libhandler.writelog(logfile, f"Message {message}")

            else:
                stored_data = f"{extract}:{amount}"

                extract_reply = extract.split(':')
                acct_num = extract_reply[1]

                message = f"Account {acct_num} is depositing GHS {amount}. Is this correct?^1. Yes^2. No"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "DEPCNF", stored_data)
                deposit_processor.libhandler.writelog(logfile, f"Message {message}")

    elif last_position == "DEPCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        # extract_reply = extract.split(':')
        # service_id = extract_reply[0]
        # acct_num = extract_reply[1]
        # amount = extract_reply[2]

        if userdata == "1":
            message = f"Your will receive a response shortly. Your Ref ID is: 93849302930" \
                # f" {trxid_processor.get_alph_id.get_alph_trxid(bank_code)}"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            deposit_processor.libhandler.writelog(logfile, f"Message {message}")

            # call deposit transfer api

        elif userdata == "2":
            message = f"Transaction failed. The account of the customer will not be debited."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            deposit_processor.libhandler.writelog(logfile, f"Message {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    else:
        menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    return menu_response
