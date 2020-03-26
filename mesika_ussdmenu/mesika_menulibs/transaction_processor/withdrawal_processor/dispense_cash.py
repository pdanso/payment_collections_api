import transaction_processor.withdrawal_processor as withdrawal_processor
import core_processor
import session_processor
import api_processor

import json

logfile = "dispense_cash"


def dispense_cash(request, data, last_position, pos, goback_message):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]
    
    if last_position == "WTHBNK":
        # get list of banks

#        message = "Please select a Financial Institution:^1. ADB^2. NIB^3. GCB^4. Stanchart^5. Stanbic^6. Cal Bank"
 #       menu_response = core_processor.make_response.make_response(request, "more", message)
  #      session_processor.store_session.store_session(msisdn, sessionid, networkid, "WTHSTA")
   #     withdrawal_processor.libhandler.writelog(logfile, f"Message: {message}")
        
    #elif last_position == "WTHSTA":
        message = "Enter Transaction Token:"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "WTHWAL", data) 
        # session is stored using the agent's msisdn
        withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

    elif last_position == "WTHWAL":
        pay_code = userdata
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        # payload = {"paycode": paycode}
        # response = call_api(payload, "cowrypay", "verifyPaycode")
        # status = response['status']

        count = 0
        status = 200

        amount = "2"
        cust_msisdn = "0504169784"
        paycode_limit = "5"

        if status == 200:
            amount = "1"
#            cust_msisdn = "0504169784"
            # get other information to store for confirmation
            # amount = response['amount']
            # cust_msisdn = response['customer_msisdn']

            stored_data = f"{extract}|{amount}|{cust_msisdn}|{pay_code}"

            message = f"Confirm Withdrawal of Ghc {amount} from customer with phone number {msisdn}.^1. " \
                      f"Yes^2. No"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "WTHCNF", stored_data)
            withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

        elif status == 203:
            message = "This transaction has been blocked. Please contact your bank"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

        else:
            # paycode_limit = response['paycode_limit']
            count += 1
            retries = paycode_limit
            retries -= 1

            if count == paycode_limit and retries == 0:
                message = "This paycode has been blocked as you have exceeded the number of retries.^Please " \
                          "contact your bank."
                menu_response = core_processor.goto_start(request, message, "", goback_message)
                withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

            else:
                message = f"Paycode entered is incorrect.^You have {retries} more attempt(s)^^Enter paycode again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_session.store_session(msisdn, sessionid, networkid, "WTHWAL")
                withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

    elif last_position == "WTHCNF":
        if userdata == "1":
            withdrawal_processor.libhandler.writelog(logfile, f"Option chosen: {userdata}")
            extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
            extract_reply = extract.split('|')
            service_id = extract_reply[0]
            amount = extract_reply[1]
            cust_msisdn = extract_reply[2]
            paycode = extract_reply[3]

            message = "Withdrawal successful. Please give cash to customer."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

            # back end sms sent to customer and agent

        elif userdata == "2":
            message = "Transaction cancelled"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    return menu_response

