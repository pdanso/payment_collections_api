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
    return trx

def internal(request, endpoint, bank_code, data, last_position, goback_message, pos):
    menu_response = ""

    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    token = data

    if last_position == "FTRACL":
        url = f"{endpoint}customers/list-customer-accounts/{msisdn}/"
        headers = {"X-CUSTOMER-AUTH-TOKEN": token}
        payload = {}

        account_results = api_processor.api_json.call_api(url, "post", payload, headers)
        ft_processor.libhandler.writelog(logfile, f"Account_list: {account_results}")
        # account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "1000800051501"},
        #                                                                {"id": 2, "account_number": "2000100611001"}]}

        if account_results['status'] == 200:
            message = ""
            count = 0
            is_active = False
            account_profile_uuid = ""
            account_number = 0

            for n in account_results['accounts']:
                account_profile_uuid = n['account_profile_uuid']
                account_number = n['account_number']
                is_active = n['active']
                count += 1
                message += str(count) + '. ' + str(account_number) + '^'

            str_conv = json.dumps(account_results['accounts'])  # converting list to json string

            acc_count = 1
            if acc_count == 1:
                stored_data = f"{str_conv}|{token}"
                message = f"Please select an Account Number for this transaction^{message}"  # ^0. Go back"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "FTRACT", stored_data)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                menu_response = core_processor.unknown_option.throw_unknown_option(request, token, goback_message)


        else:
            message = "Your account cannot be displayed right now. Please try again later"
            menu_response = core_processor.goto_start.goto_start(request, message, token, goback_message)
            ft_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "FTRACT":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        ft_processor.libhandler.writelog(logfile, f"sel = {sel}")

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        ft_processor.libhandler.writelog(logfile, f"Extract = {extract}")

        extractreply = extract.split('|')

        account_list = extractreply[0]
        token = extractreply[1]

        account_list = json.loads(account_list)
        account_profile_uuid = account_list[sel]['account_profile_uuid']
        account_number = account_list[sel]['account_number']

        stored_data = f"{token}|{account_profile_uuid}|{account_number}"

        message = f"Please enter the {bank_code} account number to credit"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        ft_processor.libhandler.writelog(logfile, f"Message: {message}")
        session_processor.store_menupoint.store_menupoint(request, "FTRCRD", stored_data)

    elif last_position == "FTRCRD":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        credit_acct_num = userdata

        extractreply = extract.split('|')
        token = extractreply[1]
        ft_processor.libhandler.writelog(logfile, f"Token = {token}")
        if not credit_acct_num.isdigit():
            message = "Account Number entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "FTRCRD", extract)
            ft_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif credit_acct_num.isdigit():
            url = f"http://progressive-ccu-efs.mesika.org:8484/cusoft-api/account-enquiry/"
            payload = {"account_number": credit_acct_num}
            response = api_processor.api_json.call_api(url, "post", payload, "")
            ft_processor.libhandler.writelog(logfile, f"Cusoft Account Enquiry Response: {response}")

            status = response['status']
            ft_processor.libhandler.writelog(logfile, f"Status: {response}")

            if status == '200':
                #  provides details
                stored_data = f"{extract}|{credit_acct_num}|{response['account_name']}"
                message = f"Please enter amount to be transferred to {response['account_name']}"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "FTRAMT", stored_data)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "The account number you entered cannot be verified. Please enter account number again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "FTRCRD", extract)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "FTRAMT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        ft_processor.libhandler.writelog(logfile, f"Extract: {extract}")
        extract_reply = extract.split('|')
        token = extract_reply[0]
        account_profile_uuid = extract_reply[1]
        account_number = extract_reply[2]
        credit_acct_num = extract_reply[3]
        fullname = extract_reply[4]
        amount = userdata
        stored_data = f"{extract}|{amount}"

        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "FTRAMT", extract)
            ft_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif amount.isdigit():
            if len(userdata) < 1 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "FTRAMT", extract)

            else:
                url = f"{endpoint}/transactions/transaction-balance-check/{account_profile_uuid}/{amount}/"
                headers = {"X-CUSTOMER-AUTH-TOKEN": token}
                response = api_processor.api_json.call_api(url, "get", {}, headers)
                ft_processor.libhandler.writelog(logfile, f"Response: {response}")

                status = response['status']
                ft_processor.libhandler.writelog(logfile, f"Status: {status}")

                    #balance = response['balance']
                message = f"Your account {account_number} will be debited with Ghc{amount} " \
                          f"to credit {fullname}." \
                          f"^Is this OK?^1. Yes^2. No"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                ft_processor.libhandler.writelog(logfile, f"Message: {message}")
                session_processor.store_menupoint.store_menupoint(request, "FTRCNF", stored_data)


                #elif status == 200 and response['has_funds'] == 0:
                #  #  balance = response['balance']
                 #   balance = 0
                  #  message = f"You do not have enough funds - current balance is GHC{balance}^Kindly enter a new amount for this transfer. Eg: 5"
                   # menu_response = core_processor.make_response.make_response(request, "more", message)
                  #  ft_processor.libhandler.writelog(logfile, f"Message: {message}")
                   # session_processor.store_menupoint.store_menupoint(request, "FTRAMT", extract)

         #       else:
          #          message = "" 

    elif last_position == "FTRCNF":
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
            
            message = f"Funds transfer of Ghc {amount} to {fullname} is being processed.^Ref ID is {trxid}."
            menu_response = core_processor.goto_start.goto_start(request, message, token, goback_message)
            ft_processor.libhandler.writelog(logfile, f"Message: {message}")

            pl = {
                'account_profile_uuid': account_profile_uuid,
                'destination_account': credit_acct_num,
                'amount': amount,
                'narration': f"{bank_code} Internal Funds Transfer",
                'transaction_id': trxid
            }
            ft_processor.libhandler.writelog(logfile, f"Payload: {pl}")

            url = f"{endpoint}transactions/funds-transfer/{msisdn}/"
            headers = {"X-CUSTOMER-AUTH-TOKEN": token}
            response = api_processor.api_json.call_api(url, "post", pl, headers)
            ft_processor.libhandler.writelog(logfile, f"Response: {response}")



        elif userdata == "2":
            message = "Funds transfer has been cancelled"
            menu_response = core_processor.goto_start.goto_start(request, message, token, goback_message)
            ft_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            data = ""
            menu_response = core_processor.unknown_option.throw_unknown_option(request, token, goback_message)

    return menu_response






