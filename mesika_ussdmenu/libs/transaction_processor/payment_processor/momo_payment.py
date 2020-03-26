import transaction_processor.payment_processor as payment_processor
import core_processor
import session_processor
import api_processor

import requests

logfile = "momo_payment"


def momo_pay(request, url, stored_data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "MPMENT":
        message = "Please enter mobile money number Eg: 0565438908"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MPMNUM", stored_data)
        payment_processor.libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "MPMNUM":  # this number is verified if it is registered for mobile money
        stored_data = session_processor.get_ussd_extra.get_ussd_extra(pos)

        num = userdata
        if not num.isdigit():
            message = "Mobile Money Number entered is Invalid. Please enter again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "MPMNUM", stored_data)
            payment_processor.libhandler.writelog(logfile, f"Message = {message}")

        elif num.isdigit():
            if len(num) > 10 or len(num) < 10:
                message = "Mobile Money Number entered is Invalid. Please enter again"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MPMNUM", stored_data)
                payment_processor.libhandler.writelog(logfile, f"Message = {message}")

            elif len(num) == 10:
                ph_num = num.rstrip('\t\n\r')
                ph_num = ph_num.lstrip('0')
                source_account = '233' + ph_num

                extract_reply = stored_data.split('|')
                product_uuid = extract_reply[0]
                product_name = extract_reply[1]
                # category_id = extract_reply[1]
                # product_id = extract_reply[2]
                # prod_name = extract_reply[3]
                biller_num = extract_reply[2]
                amount = extract_reply[3]
                pay_id = extract_reply[4]
                pay_name = extract_reply[5]

                stored_data = f"{stored_data}|{source_account}"
                # prod_name = prod_name.title()

                # store the account number and the amount for this session
                message = f"Account  {source_account} will be debited with Ghc {amount} to pay {product_name}." \
                          f"Is this OK?^1.Yes^2. No"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "MPMCNF", stored_data)
                payment_processor.libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "MPMCNF":
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
            # category_id = extract_reply[1]
            # product_id = extract_reply[2]
            # prod_name = extract_reply[3]
            biller_num = extract_reply[2]
            amount = extract_reply[3]
            pay_id = extract_reply[4]
            pay_name = extract_reply[5]
            source_account = extract_reply[6]
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
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message )
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

    return menu_response

