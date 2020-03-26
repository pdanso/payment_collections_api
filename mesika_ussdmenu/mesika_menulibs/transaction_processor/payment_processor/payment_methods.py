import core_processor
import session_processor
import transaction_processor.payment_processor as payment_processor

import json

logfile = "payment_methods"


def pay_methods(request, url, data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
    # extract_reply = extract.split('|')
    # product_id = extract_reply[2]

    if last_position == "MDEPAY":
        amount = userdata

        if not amount.isdigit():
            message = "The value you have entered is Invalid. Enter the amount again"  # ^0. Go Back"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            payment_processor.libhandler.writelog(logfile, f"message = {message}")
            session_processor.store_menupoint.store_menupoint(request, "MDEPAY", data)

        elif amount.isdigit():
            if len(userdata) < 1 or len(userdata) > 4 or userdata == "0":
                message = "Please check amount entered!^Enter amount again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MDEPAY", data)

            else:

                # payload = {"product_id": product_id}
                # response = self.core_processor.call_api(url, payload, "cowrypay", "getPaymentMethod")
                # status = response['status']
                # stored_data = f"{extract}:{amount}"
                response = {"reason": "hello", "products": [{"id": 1, "name": "MTN Mobile Money"},
                                                            {"id": 2, "name": "Vodafone Cash"},
                                                            {"id": 3, "name": "AirtelTigo Cash"}]}
                status = 200
                if status == 200:
                    try:
                        message = ""
                        count = 0
                        for n in response['products']:
                            pay_id = n['id']
                            pay_name = n['name']
                            count += 1

                            message += str(count) + '. ' + str(pay_name) + '^'

                        store_array = response['products']
                        str_conv = json.dumps(store_array)
                        # stored_data = f"{data}?{str_conv}"
                        stored_data = f"{extract}|{amount}?{str_conv}"

                        message = f"Please select mode of payment^^{message}" # 0. Go Back"
                        menu_response = core_processor.make_response.make_response(request, "more", message)
                        payment_processor.libhandler.writelog(logfile, f"Message: {message}")
                        session_processor.store_menupoint.store_menupoint(request, "MDESEL", stored_data)

                    except:
                        payment_processor.libhandler.log_error_detailed(logfile, "This option is disabled")

                else:
                    message = "List of payment methods cannot be displayed right now."
                    menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
                    payment_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MDESEL":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        payment_processor.libhandler.writelog(logfile, f"Extract: {extract}")

        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        payment_processor.libhandler.writelog(logfile, f"sel = {sel}")

        extract_reply = extract.split('?')
        rest = extract_reply[0]
        payment_list = extract_reply[1]

        payment_list = json.loads(payment_list)
        pay_id = payment_list[sel]['id']
        pay_name = payment_list[sel]['name']

        if pay_id == 0:
            message = "You cannot pay with cash now.^Please choose another option."
            payment_processor.libhandler.writelog(logfile, f"Message: {message}")
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "MDEPAY", extract)

        elif pay_id == 2 or pay_id == 3  or pay_id == 1:
            stored_data = f"{rest}|{pay_id}|{pay_name}"
            menu_response = payment_processor.momo.momo_pay(request, url, stored_data, "MPMENT", goback_message, pos)

#        elif pay_id == 5 or pay_id == 6 or pay_id == 4:
 #           stored_data = f"{rest}|{pay_id}|{pay_name}"
  #          menu_response = payment_processor.bank.bank_pay(request, url, stored_data, "MPBENT", goback_message, pos)

        elif pos[0:3] == "MPM":
            menu_response = payment_processor.momo.momo_pay(request, url, "", last_position, goback_message, pos)

        elif pos[0:3] == "MPB":
            menu_response = payment_processor.bank.bank_pay(request, url, "", last_position, goback_message, pos)

        else:
            menu_response = core_processor.unknown_option.thrown_unknown_option(request, data, goback_message)

    return menu_response

