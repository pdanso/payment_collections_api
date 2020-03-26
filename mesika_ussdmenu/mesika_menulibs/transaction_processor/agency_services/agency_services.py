import transaction_processor.deposit_processor as deposit_processor
import transaction_processor.withdrawal_processor as withdrawal_processor
import transaction_processor.loans_processor.repayment as loans_repayment

import transaction_processor.payment_processor.payment_methods as payment_processor
import transaction_processor.payment_processor.momo as pay_momo
import transaction_processor.payment_processor.bank as pay_bank

import core_processor
import session_processor
from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher
import secrets
import json

""" Initialising the logger """
host = "127.0.0.1"
port = 24777
libhandler = Logger("ussd_agency_services", host, port)

logfile = "Agency"
mtntelco_charge = 0.014
vdftelco_charge = 0.019
bank_code = "pccu"

def get_secret_trxid(code=bank_code.lower(), size=5):
    trxid = secrets.token_urlsafe(size)
    trxid = trxid.replace('_', '')
    trxid = trxid.replace('-', '')
    trxid = code + trxid

    return trxid

def magnet_agent(request, bank_code, url, last_position, pos, goback_message):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "MAGSUB":
        count = 0
        message = ""
        response = {"reason": "hello", "services": [{"id": 1, "name": "Pay Loan"},
                                                    {"id": 2, "name": "Deposit"},
                                                    {"id": 3, "name": "Withdrawal"},
                                                    {"id": 4, "name": "Other Income"}]}
        for n in response['services']:
            service_id = n['id']
            service = n['name']
            service = service.title()
            count += 1
            message += str(count) + '. ' + str(service) + '^'

        str_conv = json.dumps(response['services'])  # converting list to json string

        message = f"Please select an option:^{message}"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MAGNET", str_conv)
        libhandler.writelog(logfile, f"Message:{message}")

    elif last_position == "MAGNET":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        service_list = json.loads(extract)

        service_id = service_list[sel]['id']
        service_name = service_list[sel]['name']
        libhandler.writelog(logfile, f"extract1: {service_id}")
        libhandler.writelog(logfile, f"extract2: {service_name}")

        if service_id == 1:  # view commission balance
            # # payload = {"msidsn": msisdn, "service_id": service_id}
            # # response = core_processor.call_api(url, payload, "agency_banking", "getAgentBalance",
            # # api_version=1)
            # # status = response['status']
            #
            # status = 200
            # if status == 200:
            #     message = "Your Magnet Commission balance is GHS200"
            #     # message = f"Your Magnet Commission balance is GHS{balance}"
            #     menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            #     libhandler.writelog("agentuat_menu", f"Message: {message}")
            #
            # else:
            #     data = ""
            #     message = "Magnet Commission Balance cannot be viewed right now. Please try again later"
            #     menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
            #     libhandler.writelog("agentuat_menu", f"Message: {message}")

            menu_response = loans_repayment.loans_repayment(request, "", bank_code, "REPSTA", pos, goback_message)

        elif service_id == 2:  # deposit
            menu_response = deposit_processor.deposit.deposit(request, bank_code, url, 2, "DEPSTA", pos,
                                                              goback_message)

        elif service_id == 3:  # withdrawal
            message = "Please select an option:^1. Initiate Withdrawal^2. Dispense Cash"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            libhandler.writelog(logfile, f"message = {message}")
            session_processor.store_session.store_session(msisdn, sessionid, networkid, "MAGOPT")

        elif service_id == 4: # other income
            response = {"reason": "hello", "services": [{"id": 1, "name": "Entrance Fees"},
                                                        {"id": 2, "name": "Loan Application Fees"}]}
            count = 0
            message = ""
            for n in response['services']:
                service_id = n['id']
                service = n['name']
                service = service.title()
                count += 1
                message += str(count) + '. ' + str(service) + '^'

            str_conv = json.dumps(response['services'])  # converting list to json string

            message = f"Please select an option:^{message}"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "MAGFEE", str_conv)
            libhandler.writelog(logfile, f"Message:{message}")


        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    elif last_position == "MAGFEE":

        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        service_list = json.loads(extract)

        fee_id = service_list[sel]['id']
        fee_name = service_list[sel]['name']
        libhandler.writelog(logfile, f"extract1: {fee_id}")
        libhandler.writelog(logfile, f"extract2: {fee_name}")

        storeddata = f"{fee_id}|{fee_name}"
        menu_response = deposit_processor.deposit.deposit(request, bank_code, url, 2, "DEPSTA", pos,
                                                              goback_message)
#
 #       message = f"Enter amount"
  #      menu_response = core_processor.make_response.make_response(request, "more", message)
   #     session_processor.store_menupoint.store_menupoint(request, "CRORES", storeddata)
    #    libhandler.writelog(logfile, f"Message:{message}")

    elif last_position == "MAGOPT":
        libhandler.writelog(logfile, f"message")
        if userdata == "1":     
            libhandler.writelog(logfile, f"testing")
            menu_response = withdrawal_processor.initiate_withdrawal.initiate_withdrawal(request, "WTDBNK", pos, goback_message)

        elif userdata == "2":
            menu_response = withdrawal_processor.dispense_cash.dispense_cash(request, "", "WTHBNK", pos, goback_message)

    elif last_position == "CRORES":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        libhandler.writelog(logfile, f"Extract: {extract}")
    
        amount = userdata
    
        if not amount.isdigit():
            message = "Amount entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "CRORES", extract)
            libhandler.writelog(logfile, f"Message = {message}")
    
        elif amount.isdigit():
            if len(userdata) < 1 or len(userdata) > 4 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "CRORES", extract)
    
            else:
                stored_data = f"{extract}|{amount}"
    
                response = {"reason": "hello", "products": [{"id": 1, "name": "MTN Mobile Money"},
                                                            {"id": 2, "name": "Vodafone Cash"}]}
                #                    {"id": 3, "name": "AirtelTigo Cash"}]}
    
                message = ""
                count = 0
    
                for n in response['products']:
                    acct_id = n['id']
                    source_account = n['name']
                    count += 1
                    message += str(count) + '. ' + str(source_account) + '^'
    
                store_array = response['products']
                str_conv = json.dumps(store_array)
                stored_data = f"{stored_data}?{str_conv}"
    
                # message = f"Please select a payment method:^1. MTN Mobile Money"
                message = f"Please select a payment method^{message}"
                menu_response = core_processor.make_response.notitle_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "CROPAY", stored_data)
                libhandler.writelog(logfile, f"Message: {message}")
    
    elif last_position == "CROPAY":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        libhandler.writelog(logfile, f"Extract: {extract}")
    
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        libhandler.writelog(logfile, f"sel = {sel}")
    
        extract_reply = extract.split('?')
        rest = extract_reply[0]
        payment_list = extract_reply[1]
    
        payment_list = json.loads(payment_list)
        pay_id = payment_list[sel]['id']
        pay_name = payment_list[sel]['name']
    
        stored_data = f"{rest}|{pay_id}|{pay_name}"
        message = f"Enter {pay_name} number"
    
        menu_response = core_processor.make_response.notitle_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "CROMOM", stored_data)
        libhandler.writelog(logfile, f"Message: {message}")
    
    elif last_position == "CROMOM":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        libhandler.writelog(logfile, f"Extract: {extract}")
        extract_reply = extract.split('|')
        fee_name = extract_reply[1]
        fee_id = extract_reply[0]
        amount = extract_reply[2]
        pay_name = extract_reply[4]
        pay_id = extract_reply[3]
    
        momonum = userdata
    
        if not momonum.isdigit():
            message = f"{pay_name} entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "CROMOM", extract)
            libhandler.writelog(logfile, f"Message = {message}")
    
        elif momonum.isdigit():
            if len(userdata) < 10 or len(userdata) > 10:
                message = f"Please check {pay_name} number entered!^Enter {pay_name} number again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "CROMOM", extract)
    
            elif len(userdata) == 10:
                ph_num = momonum.rstrip('\t\n\r')
                ph_num = ph_num.lstrip('0')
                momonum = '233' + ph_num
    
                stored_data = f"{extract}|{momonum}"
                charge = 0
    
                if pay_id == "2":
                    message = "Enter Voucher ID"
                    menu_response = core_processor.make_response.notitle_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "CROVDF", stored_data)
                    libhandler.writelog(logfile, f"Message: {message}")
    
                elif pay_id == "1":
                    charge = 0
    
                    charge = float(amount) * float(mtntelco_charge)
                    libhandler.writelog(logfile, f"Charge: {charge}")
    
                    total_amount = float(amount) + float(charge)
                    libhandler.writelog(logfile, f"total: {total_amount}")
    
                    stored_data = f"{stored_data}|{total_amount}|{charge}"
                    libhandler.writelog(logfile, f"Total amount: {total_amount}")
    
                    message = f"Processing Charge: GHC{charge}^You are paying a total of " \
                              f"GHC {total_amount} as " \
                              f"{fee_name} from {momonum}. Is this ok?^1. Yes^2. No"
                    menu_response = core_processor.make_response.notitle_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "CROCNF", stored_data)
                    libhandler.writelog(logfile, f"Message: {message}")
    
                else:
                    menu_response = core_processor.unknown_option.throw_unknown_option(request, "",
                                                                                       goback_message)
    
    elif last_position == "CROCNF":
        voucherid = ""
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        libhandler.writelog(logfile, f"Extract: {extract}")
        extract_reply = extract.split('|')
        fee_name = extract_reply[1]
        fee_id = extract_reply[0]
        amount = extract_reply[2]
        pay_name = extract_reply[4]
        pay_id = extract_reply[3]

        momonum = extract_reply[5]
        total_amount = extract_reply[6]
        charge = extract_reply[7]
    
        # url = "https://microwatch-api.mesika.org/api/client-collections/v1/transactions/submit/"
        # libhandler.writelog(logfile, f"Payload: {url}")
    
        trxid = get_secret_trxid()
    
        libhandler.writelog(logfile, f"Payload: {trxid}")
    
        if userdata == "1":
            if pay_id == "1":
                voucherid = ""
                message = f"Your payment for {fee_name} and processing charge GHC {charge} is" \
                          f" being processed.Press ok to get Mesika approval prompt"
                menu_response = core_processor.make_response.notitle_response(request, "end", message)
                core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")
    
     #           payload = {"payer": payer, "reference_number": trxid,
      #                     "account_number": momonum, "payer_msisdn": msisdn, "billed_amount": amount,
       #                    "processing_fees": charge, "provider": "MTN", "narration": dues_name,
        #                   "voucher_code": voucherid,
     #                      "extra_details": {"dues": dues_name, "credit_union": ccuname}
      #                     }
    #            libhandler.writelog(logfile, f"Payload: {payload}")
    
            elif pay_id == "2":
                voucherid = extract_reply[8]
                message = f"Your payment for {fee_name} and processing charge GHC {charge} is" \
                          f" being processed. Thank you."
                menu_response = core_processor.make_response.notitle_response(request, "end", message)
                core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")
    
   #             payload = {"payer": payer, "reference_number": trxid,
                           #"account_number": momonum, "payer_msisdn": msisdn, "billed_amount": amount,
                           #"processing_fees": charge, "provider": "VODAFONE", "narration": dues_name,
                           #"voucher_code": voucherid,
                          # "extra_details": {"dues": dues_name, "credit_union": ccuname}
                          # }
             #   libhandler.writelog(logfile, f"Payload: {payload}")
    
            # response = requests.post(url, json=payload, verify=False)
            # libhandler.writelog(logfile, f"Submit Response: {response.text}")
    
        elif userdata == "2":
            message = f"You have cancelled this transaction."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            libhandler.writelog(logfile, f"Message: {message}")
    
        else:
            data = ""
            menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)
    
    elif last_position == "CROVDF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        libhandler.writelog(logfile, f"Extract: {extract}")
        extract_reply = extract.split('|')
    
        fee_name = extract_reply[1]
        fee_id = extract_reply[0]
        amount = extract_reply[2]
        pay_name = extract_reply[4]
        pay_id = extract_reply[3]

        momonum = extract_reply[5]
    
        voucherid = userdata
    
        if not voucherid.isdigit():
            message = "Voucher id entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "CROVDF", extract)
            libhandler.writelog(logfile, f"Message = {message}")
    
        elif voucherid.isdigit():
            if len(userdata) < 6 or len(userdata) > 6:
                message = f"Please check voucher id entered!^Enter voucher id again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "CROVDF", extract)
    
            elif len(userdata) == 6:
                charge = 0
    
                charge = float(amount) * float(vdftelco_charge)
                charge = "{0:.2f}".format(charge)
                libhandler.writelog(logfile, f"Charge: {charge}")
    
                total_amount = float(amount) + float(charge)
                stored_data = f"{extract}|{total_amount}|{charge}|{voucherid}"
                libhandler.writelog(logfile, f"Total amount: {total_amount}")
    
                message = f"Processing Charge:GHC{charge}^You are paying a total of GHC {total_amount} as " \
                          f"{fee_name} from {momonum}.Is this ok?^1.Yes^2.No"
                menu_response = core_processor.make_response.notitle_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "CROCNF", stored_data)
                libhandler.writelog(logfile, f"Message: {message}")
    
    
    
            else:
                menu_response = core_processor.unknown_option.throw_unknown_option(request, "",
                                                                                   goback_message)


    elif pos[0:3] == "DEP":
        menu_response = deposit_processor.deposit.deposit(request, bank_code, url, 3, last_position, pos,
                                                          goback_message)

    elif pos[0:3] == "WTH":
        menu_response = withdrawal_processor.dispense_cash.dispense_cash(request, "", last_position, pos, goback_message)

    elif pos[0:3] == "WTD":
        menu_response = withdrawal_processor.initiate_withdrawal.initiate_withdrawal(request, last_position, pos, goback_message)

    elif pos[0:3] == "DEP":
        menu_response = deposit_processor.deposit.deposit(request, bank_code, url, 3, last_position, pos,
                                                          goback_message)

    elif pos[0:3] == "REP":
        menu_response = loans_repayment.loans_repayment(request, "", bank_code, last_position, pos, goback_message)

    elif pos[0:3]  == "MDE":
        menu_response = payment_processor.pay_methods(request, url, "", last_position, goback_message, pos)

    elif pos[0:3]  == "MPM":
         menu_response = pay_momo.momo_pay(request, url, "", last_position, goback_message, pos)

    elif pos[0:3] == "MPB":
         menu_response = pay_bank.bank_pay(request, url, "", last_position, goback_message, pos)


    return menu_response


def magnet_cust(request, bank_code, url, last_position,pos, goback_message):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "WTDBNK":
        menu_response = withdrawal_processor.initiate_withdrawal.initiate_withdrawal(request, "WTDBNK", pos, goback_message)

    elif pos[0:3] == "WTD":
        menu_response = withdrawal_processor.initiate_withdrawal.initiate_withdrawal(request, last_position, pos, goback_message)

    return menu_response

