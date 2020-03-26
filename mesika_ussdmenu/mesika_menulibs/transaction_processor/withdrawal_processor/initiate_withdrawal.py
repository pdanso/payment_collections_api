import transaction_processor.withdrawal_processor as withdrawal_processor
import core_processor
import session_processor
import api_processor

import json

logfile = "initiate_withdrawal"


def initiate_withdrawal(request, last_position, pos, goback_message):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "WTDBNK":
#        message = "Please select a Financial Institution:^1. ADB^2. NIB^3. GCB^4. Stanchart^5. Stanbic^6. Cal Bank"
 #       menu_response = core_processor.make_response.make_response(request, "more", message)
  #      session_processor.store_session.store_session(msisdn, sessionid, networkid, "WTDSTA")
#        withdrawal_processor.libhandler.writelog(logfile, f"Message: {message}")

#    elif last_position == "WTDSTA":
 #       message = "Please enter Mobile Banking Phone Number Eg: 0565438908"
  #      menu_response = core_processor.make_response.make_response(request, "more", message)
   #     session_processor.store_menupoint.store_menupoint(request, "WTDPHN", "")

   # elif last_position == "WTDPHN":

    #    extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        #mbank_num = userdata

     #   if not mbank_num.isdigit():
      #      message = "Phone Number Entered is Invalid.^Enter your Mobile Banking Phone Number again"  # ^0. Go Back"
 #           menu_response = core_processor.make_response.make_response(request, "more", message)
  #          withdrawal_processor.libhandler.writelog(logfile, f"message = {message}")
   #         session_processor.store_menupoint.store_menupoint(request, "WTDPHN", extract)

    #    elif mbank_num.isdigit():
     #       if len(mbank_num) < 10 or len(mbank_num) > 10:
      #          message = "Please check phone number entered!^Enter phone number again"
#                menu_response = core_processor.make_response.make_response(request, "more", message)
 #               session_processor.store_menupoint.store_menupoint(request, "WTDPHN", extract)

#            elif len(userdata) == 10:
 #               stored_data = f"{extract}|{mbank_num}"
  #              message = "Please enter your Mobile Banking secret PIN"
 #               menu_response = core_processor.make_response.make_response(request, "more", message)
  #              session_processor.store_menupoint.store_menupoint(request, "WTDPIN", stored_data)

   #         else:
    #            menu_response = core_processor.unknown_option.thrown_unknown_option(request, "", goback_message)

  #  elif last_position == "WTDPIN":
        #extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
   #     mbank_pin = userdata

    #    extract_reply = extract.split('|')
     #   mbank_num = extract_reply[1]

        # payload = {"msisdn": mbank_num, "pin": mbank_pin}
        # response = self.core_processor.call_api(url, payload, "cowrybank", "customerLogin")
        # status = response['status']
    #    status = 200

        #if status == 200:
            # account_results = self.request_account(bank_id, url, service_id, extract, last_position, goback_message)
            # payment_processor.libhandler.writelog(logfile, f"Request_account Response = {account_results}")

            # ==================== account list and count ============================

         #   account_results = {"status": 200, "count": 2, "account_list": [{"id": 1, "account_number": "12345987098"},
                                                                      #     {"id": 2, "account_number": "09876789878"}]}

          #  if account_results['status'] == 200:
           #     acc_count = account_results['count']
            #    account_list = account_results['account_list']

#                if acc_count >= 1:
 #                   message = ""
  #                  count = 0
   #                 for n in account_results['account_list']:
    #                    acct_id = n['id']
     #                   source_account = n['account_number']
      #                  count += 1
       #                 message += str(count) + '. ' + str(source_account) + '^'

        ##            str_conv = json.dumps(account_list)
          #          stored_data = f"{str_conv}?{extract}"

                    #message = f"Please select an Account Number for this transaction^{message}"  # ^0. Go back"
            message = f"Please enter an Account Number for this transaction"  # ^0. Go back"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "WTDACC", "")
            withdrawal_processor.libhandler.writelog(logfile, f"Message: {message}")

            #    else:
             #       message = "Account numbers cannot be displayed right now. Please try again later"
              #      menu_response = core_processor.goto_start.goto_start(request, message, goback_message)
               #     withdrawal_processor.libhandler.writelog(logfile, f"Message: {message}")

 #           else:
  #              message = "Account numbers cannot be displayed right now. Please try again later"
   #             menu_response = core_processor.goto_start.goto_start(request, message, goback_message)
    #            withdrawal_processor.libhandler.writelog(logfile, f"Message: {message}")


     #   else:
      #      message = "Invalid Credentials. Please try again later. Eg: 0561012334"
       #     menu_response = core_processor.goto_start.goto_start(request, "", message)
        #    withdrawal_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "WTDACC":
       # extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
       # extract_reply = extract.split('?')
       # acct_list = extract_reply[0]
       # data = extract_reply[1]

        #sel0 = userdata
        #sel0 = int(sel0)
        #sel = sel0 - 1
        #withdrawal_processor.libhandler.writelog(logfile, f"sel = {sel}")

        #withdrawal_processor.libhandler.writelog(logfile, f"Extract = {acct_list}")

        #acct_list = json.loads(acct_list)
        #acct_id = acct_list[sel]['id']
        #withdrawal_processor.libhandler.writelog(logfile, f"act id = {acct_id}")
        #source_account = acct_list[sel]['account_number']
        #withdrawal_processor.libhandler.writelog(logfile, f"acct = {source_account}")

        #extract_reply = data.split('|')

        #mbank_num = extract_reply[1]

        #stored_data = f"{extract}|{source_account}"

        # stored_data = f"{service_id}:{category_id}:{product_id}:{prod_name}:{biller_num}:{amount}:{pay_id}:{
        # source_account}"

        acctnum = userdata
        stored_data = f"{acctnum}"
        message = "Enter Amount Eg: 5"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "WTDAMT", stored_data)
        withdrawal_processor.libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "WTDAMT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        amount = userdata
#        extract_reply = extract.split('|')

 #       mbank_num = extract_reply[1]

        if not amount.isdigit():
            message = "Amount entered is invalid.^Enter Amount again. Eg: 5"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "WTDAMT", extract)
            withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

        elif amount.isdigit():
            if len(amount) < 1 or len(amount) > 4 or amount == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "WTDAMT", extract)
                withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

            else:
                mbank_num = '0243310119'
                message = f"Transaction Token will be generated and sent to {mbank_num} to withdraw Ghc" \
                          f" {amount}^Is this OK?^1. Yes^2. No"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "WTDCNF", extract)
                withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")


    elif last_position == "WTDCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        if userdata == "1":
            withdrawal_processor.libhandler.writelog(logfile, "Option chosen: %s" % userdata)

            # payload = {"customer_msisdn": cust_msisdn, "amount": amount, "account_id": acct_id, "agent_msisdn": msisdn,
            #            "service_id": service_id}
            # response = call_api(payload, "cowrybank", "agentWithdrawal")
            # status = response['status']

            message = "Transaction Token will be " \
                      "sent shortly"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

        elif userdata == "2":
            message = "Transaction Token cancelled. Transaction cannot be completed"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            withdrawal_processor.libhandler.writelog(logfile, f"Message {message}")

        else:
            menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

    return menu_response



