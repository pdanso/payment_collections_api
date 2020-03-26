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

def internal(request, endpoint, bank_code, data, last_position, goback_message, pos):
    menu_response = ""

    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    token = data

    if last_position == "FNDACL":
        url = f"{endpoint}customers/list-customer-accounts/{msisdn}/"
        headers = {"X-CUSTOMER-AUTH-TOKEN": token}
        payload = {}

        account_results = api_processor.api_json.call_api(url, "post", payload, headers)
        ft_processor.libhandler.writelog(logfile, f"Account_list: {account_results}")
        # account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "1000800051501"},
        #                                                                {"id": 2, "account_number": "2000100611001"}]}

        if account_results['status'] == 200:
            account_profile_uuid = account_results['account_profile_uuid']
            account_number = account_results['account_number']
            is_active = account_results['active']

            if is_active:
                stored_data = f"{account_profile_uuid}|{account_number}"
                acc_count = 1
                if acc_count == 1:
                    message = f"Please select an Account Number for this transaction^1. {account_number}"  # ^0. Go back"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "FNDACT", stored_data)
                    ft_processor.libhandler.writelog(logfile, f"Message: {message}")

                else:
                    menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

            else:
                menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

        elif last_position == "FNDACT":
            sel0 = userdata
            sel0 = int(sel0)
            sel = sel0 - 1
            ft_processor.libhandler.writelog(logfile, f"sel = {sel}")

            extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
            ft_processor.libhandler.writelog(logfile, f"Extract = {extract}")
            # extract_list = json.loads(extract)


            # acct_id = acct_list[sel]['id']
            # acct_num = acct_list[sel]['account_number']

            # stored_data = f"{data}|{acct_num}"

            message = f"Please enter the {bank_code} account number to credit"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            ft_processor.libhandler.writelog(logfile, f"Message: {message}")
            session_processor.store_menupoint.store_menupoint(request, "FNDCRD", extract)

        elif last_position == "FNDCRD":
            extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
            credit_acct_num = userdata

            if not credit_acct_num.isdigit():
                message = "Account Number entered is Invalid. Please enter again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "FNDCRD", extract)
                ft_processor.libhandler.writelog(logfile, f"Message = {message}")

            elif credit_acct_num.isdigit():
                url = f"{endpoint}/customers/search/msisdn/{msisdn}/"
                headers = {"X-CUSTOMER-AUTH-TOKEN": token}
                response = api_processor.api_json.call_api(url, "get", {}, headers)
                ft_processor.libhandler.writelog(logfile, f"Response: {response}")

                status = response['status']
                ft_processor.libhandler.writelog(logfile, f"Status: {status}")

                if status == 200:
                    #  provides details
                    stored_data = f"{extract}|{credit_acct_num}|{response['fullname']}"
                    message = f"Please enter amount to be transferred to {response['fullname']}"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "FNDAMT", stored_data)
                    ft_processor.libhandler.writelog(logfile, f"Message: {message}")

                else:
                    message = "The account number you entered cannot be verified. Please enter account number again"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "FNDCRD", extract)
                    ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "FNDAMT":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                ft_processor.libhandler.writelog(logfile, f"Extract: {extract}")
                extract_reply = extract.split('|')
                account_profile_uuid = extract_reply[1]
                account_number = extract_reply[2]
                credit_acct_num = extract_reply[3]
                fullname = extract_reply[4]
                amount = userdata
                stored_data = f"{extract}|{amount}"

                if not amount.isdigit():
                    message = "Amount entered is Invalid. Please enter again"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "FNDAMT", extract)
                    ft_processor.libhandler.writelog(logfile, f"Message = {message}")

                elif amount.isdigit():
                    if len(userdata) < 1 or userdata == "0":
                        message = "Please check amount entered!^Enter amount again"
                        menu_response = core_processor.make_response.make_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "FNDAMT", extract)

                    else:
                        url = f"{endpoint}/transactions/get-bank-balance/{account_profile_uuid}/{amount}/"
                        headers = {"X-CUSTOMER-AUTH-TOKEN": token}
                        response = api_processor.api_json.call_api(url, "get", {}, headers)
                        ft_processor.libhandler.writelog(logfile, f"Response: {response}")

                        status = response['status']
                        ft_processor.libhandler.writelog(logfile, f"Status: {status}")

                        if status == 200:
                            message = response['message']
                            message = f"{message}^Your account {account_number} will be debited with Ghc{amount} " \
                                      f"to credit {fullname}." \
                                      f"^Is this OK?^1. Yes^2. No"
                            menu_response = core_processor.make_response.make_response(request, "more", message)
                            ft_processor.libhandler.writelog(logfile, f"Message: {message}")
                            session_processor.store_menupoint.store_menupoint(request, "FNDCNF", stored_data)

                        else:
                            message = response['message']
                            message = f"{message}^Kindly enter a new amount for this transfer. Eg: 5"
                            menu_response = core_processor.make_response.make_response(request, "more", message)
                            ft_processor.libhandler.writelog(logfile, f"Message: {message}")
                            session_processor.store_menupoint.store_menupoint(request, "FNDAMT", extract)

                elif last_position == "FNDCNF":
                    extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                    ft_processor.libhandler.writelog(logfile, f"Extract: {extract}")
                    extract_reply = extract.split('|')
                    token = extract_reply[0]
                    account_profile_uuid = extract_reply[1]
                    account_number = extract_reply[2]
                    credit_acct_num = extract_reply[3]
                    fullname = extract_reply[4]
                    amount = extract_reply[5]

                    trxid = gen_trx()

                    if userdata == "1":
                        pl = {
                            'account_profile_uuid': account_profile_uuid,
                            'destination_account': credit_acct_num,
                            'amount': amount,
                            'narration': f"{bank_code} Internal Funds Transfer",
                            'transaction_id': trxid
                        }
                        ft_processor.libhandler.writelog(logfile, f"Payload: {payload}")

                        url = f"{endpoint}transactions/funds-transfer/{msisdn}/"
                        headers = {"X-CUSTOMER-AUTH-TOKEN": token}
                        response = api_processor.api_json.call_api(url, "get", {}, headers)
                        ft_processor.libhandler.writelog(logfile, f"Response: {response}")

                        status = response['status']
                        ft_processor.libhandler.writelog(logfile, f"Status: {status}")

                        if status == 200:
                            refid = response['response'][0]['referenceId']
                            message = f"Funds transfer of Ghc {amount} to {fullname} is being processed.^Ref ID is {trxid}."
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






