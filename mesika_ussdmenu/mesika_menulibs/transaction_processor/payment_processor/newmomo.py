import transaction_processor.payment_processor as payment_processor
import core_processor
import session_processor
import api_processor

import requests

logfile = "momo_payment"
momocharge = 0.009

def momo_pay(request, url, stored_data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "CROENT":
        message = "Please enter mobile money number Eg: 0565438908"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MPMNUM", stored_data)
        payment_processor.libhandler.writelog(logfile, f"Message = {message}")

    elif last_position == "CROMOM":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        libhandler.writelog(logfile, f"Extract: {extract}")
        extract_reply = extract.split('|')
        ccuname = extract_reply[0]
        payer = extract_reply[1]
        dues_name = extract_reply[2]
        dues_id = extract_reply[3]
        amount = extract_reply[4]
        pay_name = extract_reply[6]
        pay_id = extract_reply[5]

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
                                      f"{dues_name} from {momonum}. Is this ok?^1. Yes^2. No"
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
                ccuname = extract_reply[0]
                payer = extract_reply[1]
                dues_name = extract_reply[2]
                dues_id = extract_reply[3]
                amount = extract_reply[4]
                pay_name = extract_reply[6]
                pay_id = extract_reply[5]
                momonum = extract_reply[7]
                total_amount = extract_reply[8]
                charge = extract_reply[9]

                # url = "https://microwatch-api.mesika.org/api/client-collections/v1/transactions/submit/"
                # libhandler.writelog(logfile, f"Payload: {url}")

                trxid = get_secret_trxid()

                libhandler.writelog(logfile, f"Payload: {trxid}")

                if userdata == "1":
                    if pay_id == "1":
                        voucherid = ""
                        message = f"Your payment for {dues_name} and processing charge GHC {charge} is" \
                                  f" being processed.Press ok to get Mesika approval prompt"
                        menu_response = core_processor.make_response.notitle_response(request, "end", message)
                        core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

                        payload = {"payer": payer, "reference_number": trxid,
                                   "account_number": momonum, "payer_msisdn": msisdn, "billed_amount": amount,
                                   "processing_fees": charge, "provider": "MTN", "narration": dues_name,
                                   "voucher_code": voucherid,
                                   "extra_details": {"dues": dues_name, "credit_union": ccuname}
                                   }
                        libhandler.writelog(logfile, f"Payload: {payload}")

                    elif pay_id == "2":
                        voucherid = extract_reply[9]
                        message = f"Your payment for {dues_name} and processing charge GHC {charge} is" \
                                  f" being processed. Thank you."
                        menu_response = core_processor.make_response.notitle_response(request, "end", message)
                        core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

                        payload = {"payer": payer, "reference_number": trxid,
                                   "account_number": momonum, "payer_msisdn": msisdn, "billed_amount": amount,
                                   "processing_fees": charge, "provider": "VODAFONE", "narration": dues_name,
                                   "voucher_code": voucherid,
                                   "extra_details": {"dues": dues_name, "credit_union": ccuname}
                                   }
                        libhandler.writelog(logfile, f"Payload: {payload}")

                    # response = requests.post(url, json=payload, verify=False)
                    # libhandler.writelog(logfile, f"Submit Response: {response.text}")

                elif userdata == "2":
                    message = f"You have cancelled this registration."
                    menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                    libhandler.writelog(logfile, f"Message: {message}")

                else:
                    data = ""
                    menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

            elif last_position == "CROVDF":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")
                extract_reply = extract.split('|')

                ccuname = extract_reply[0]
                payer = extract_reply[1]
                dues_name = extract_reply[2]
                dues_id = extract_reply[3]
                amount = extract_reply[4]
                pay_name = extract_reply[6]
                pay_id = extract_reply[5]
                momonum = extract_reply[7]


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
                                  f"{dues_name} registration fee from {momonum}.Is this ok?^1.Yes^2.No"
                        menu_response = core_processor.make_response.notitle_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "CROCNF", stored_data)
                        libhandler.writelog(logfile, f"Message: {message}")



                    else:
                        menu_response = core_processor.unknown_option.throw_unknown_option(request, "",
                                                                                           goback_message)

     return
