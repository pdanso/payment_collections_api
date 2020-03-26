'''
Created: November 6, 2019 9:28pm
author: d33v4sn1p3r1
'''

from django.shortcuts import render_to_response

from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

import core_processor.make_response
import core_processor.goto_start
import core_processor.unknown_option
import core_processor.disable_service

import session_processor.store_session
import session_processor.store_menupoint
import session_processor.get_last_step
import session_processor.get_ussd_extra

import transaction_processor.funds_transfer_processor.funds_transfer as ft_processor
import transaction_processor.funds_transfer_processor.internal as internal_ft_processor

import transaction_processor.funds_transfer_processor.gip as gip_processor

import transaction_processor.airtime_processor.airtime as trans_airtime

import transaction_processor.mobile_money_processor.momo as momo_processor
import transaction_processor.mobile_money_processor.bank_wallet as momo_bankwallet
import transaction_processor.mobile_money_processor.wallet_bank as momo_walletbank

import transaction_processor.collections_processor.collections as collections_processor

import transaction_processor.payment_processor.payment_methods as payment_processor
import transaction_processor.payment_processor.momo as pay_momo
import transaction_processor.payment_processor.bank as pay_bank

import transaction_processor.forex_processor.forex as forex_processor

import pin_processor.pin_reset as pin_processor

import transaction_processor.loans_processor.loans as loans_processor
import transaction_processor.loans_processor.repayment as loans_repayment

import transaction_processor.deposit_processor.deposit as deposit_processor
import transaction_processor.withdrawal_processor.initiate_withdrawal as withdraw_initiate
import transaction_processor.withdrawal_processor.dispense_cash as withdrawal_processor

import userstatus_processor.status_check
import userstatus_processor.login
import trxid_processor.get_secret_id as trxid_processor
import api_processor.api_json as api_processor



import json
import string
import random
import requests
import datetime
import secrets
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


''' Initialising the logger '''

libhandler = Logger(app_or_directory_name="CEM_payment_collections_menu", host="logmaster.mesika.org",
                    port=24777, version=1)
logfile = "live_menu"

goback_message = "Enter any digit to continue!"
url = "https://cem-api.mesika.org/"

bank_code = "CEM"
mtntelco_charge = 0.015
vdftelco_charge = 0.017
airteltigo_charge = 0.017


def get_secret_trxid(code=bank_code.lower(), size=5):
    trxid = secrets.token_urlsafe(size)
    trxid = trxid.replace('_', '')
    trxid = trxid.replace('-', '')
    trxid = code + trxid

    return trxid


# make changes to lib for the requests
def view(request):
    menu_response = " "
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    try:
        if mode == "start":
            # message = f"Welcome to VotEazy Voting Platform.^Voting for all events has ended. ^Thank you."
            # menu_response = core_processor.make_response.notitle_response(request, "end", message)
            # libhandler.writelog(logfile, f"Message: {message}")

            message = ""
            count = 0
            response = {"service_list": [{"id": 1, "name": "First Fruit"},
                                         {"id": 2, "name": "Tithe"},
                                         {"id": 3, "name": "Pledge"},
                                         {"id": 4, "name": "Welfare"},
                                         {"id": 5, "name": "Christ To The Rural World"},
                                         {"id": 6, "name": "Day of Help"},
                                         {"id": 7, "name": "General Offering"},
                                         {"id": 0, "name": "More"}
                                     ]}

            for service in response['service_list']:
                service_id = service['id']
                service_name = service['name']
                count += 1
                message += str(count) + '. ' + str(service_name) + '^'

            str_conv = json.dumps(response['service_list'])  # converting list to json string
            stored_data = f"{str_conv}"

            message = f"Welcome to CHARISMATIC EVANGELISTIC MINISTRY Payment Service.^Select:^1. First Fruit^2. Tithe" \
                      f"^3. Pledge^4. Welfare^0. More"
            menu_response = core_processor.make_response.notitle_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "SESSTR", stored_data)
            libhandler.writelog(logfile, f"Message: {message}")

        else:
            pos = session_processor.get_last_step.get_last_step(msisdn, sessionid, networkid)
            last_position = pos[0:6]
            menu_mod = pos[0:3]
            libhandler.writelog(logfile, f"POS: {pos}")

            if last_position == "SESSTR":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")

                if userdata == "0":
                    message = f"Select:^5. Christ to The Rural World^6. Day of Help^7. General Offering"
                    menu_response = core_processor.make_response.notitle_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "SESSTR", extract)

                    libhandler.writelog(logfile, f"Message: {message}")

                elif 1 <= int(userdata) <= 7:
                    sel0 = userdata
                    sel0 = int(sel0)
                    sel = sel0 - 1

                    service_list = json.loads(extract)
                    service_id = service_list[sel]['id']
                    service_name = service_list[sel]['name']
                    libhandler.writelog(logfile, f"Message: {service_id} and {service_name}")

                    stored_data = f"{service_id}|{service_name}"

                    message = f"Enter membership number or 0 to skip"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "CEMMEM", stored_data)
                    libhandler.writelog(logfile, f"Message: {message}")

                else:
                    menu_response = core_processor.unknown_option.throw_unknown_option(request, "",
                                                                                       goback_message)

            elif last_position == "CEMMEM":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")

                if userdata == "0":
                    membership_number = "N/A"

                else:
                    membership_number = userdata

                stored_data = f"{extract}|{membership_number}"

                message = "Enter an amount "
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "CEMAMT", stored_data)
                libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "CEMAMT":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")

                amount = userdata

                if not amount.isdigit():
                    message = "Amount entered is Invalid. Please enter again"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "CEMMEM", extract)
                    libhandler.writelog(logfile, f"Message = {message}")

                elif amount.isdigit():
                    if len(userdata) < 1 or userdata[0] == '0' or userdata == "0":
                        message = "Please check amount entered!^Enter amount again"
                        menu_response = core_processor.make_response.make_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "CEMMEM", extract)

                    else:
                        stored_data = f"{extract}|{amount}"
                        message = "Enter narration - Eg: Payment for x service"
                        menu_response = core_processor.make_response.make_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "CEMNAR", stored_data)
                        libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "CEMNAR":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")

                narration = userdata
                stored_data = f"{extract}|{narration}"

                response = {"reason": "hello", "products": [{"id": 1, "name": "MTN Mobile Money"},
                                                            {"id": 2, "name": "Vodafone Cash"},
                                                            {"id": 3, "name": "AirtelTigo Money"},
                                                            ]}

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
                session_processor.store_menupoint.store_menupoint(request, "CEMPAY", stored_data)
                libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "CEMPAY":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")

                # message = "Pay test"
                # stored_data = ""

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
                session_processor.store_menupoint.store_menupoint(request, "CEMMOM", stored_data)
                libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "CEMMOM":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")
                extract_reply = extract.split('|')
                service_id = extract_reply[0]
                service_name = extract_reply[1]
                membership_number = extract_reply[2]
                amount = extract_reply[3]
                narration = extract_reply[4]
                pay_name = extract_reply[6]
                pay_id = extract_reply[5]

                momonum = userdata
                libhandler.writelog(logfile, f"Momo Number Entered: {momonum}")

                if not momonum.isdigit():
                    message = f"{pay_name} entered is Invalid. Please enter again"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "CEMMOM", extract)
                    libhandler.writelog(logfile, f"Message = {message}")

                elif momonum.isdigit():
                    if len(userdata) < 10 or len(userdata) > 10:
                        message = f"Please check {pay_name} number entered!^Enter {pay_name} number again"
                        menu_response = core_processor.make_response.make_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "CEMMOM", extract)

                    elif len(userdata) == 10:
                        ph_num = momonum.rstrip('\t\n\r')
                        ph_num = ph_num.lstrip('0')
                        momonum = '233' + ph_num

                        stored_data = f"{extract}|{momonum}"
                        charge = 0

                        if pay_id == "2":
                            #menu_response = core_processor.disable_service.service_disabled(request, "", goback_message)
                            message = "Enter Voucher ID"
                            menu_response = core_processor.make_response.notitle_response(request, "more", message)
                            session_processor.store_menupoint.store_menupoint(request, "CEMVDF", stored_data)
                            libhandler.writelog(logfile, f"Message: {message}")

                        elif pay_id == "1":
                            charge = 0

                            charge = float(amount) * float(mtntelco_charge)
                            charge = "{0:.4f}".format(charge)
                            libhandler.writelog(logfile, f"Charge: {charge}")

                            total_amount = float(amount) + float(charge)
                            libhandler.writelog(logfile, f"total: {total_amount}")

                            stored_data = f"{stored_data}|{total_amount}|{charge}"
                            libhandler.writelog(logfile, f"Total amount: {total_amount}")

                            message = f"Processing Charge: GHC{charge}^You are paying a total of " \
                                      f"GHC {total_amount} as " \
                                      f"{service_name} from {momonum}.^Is this ok?^1. Yes^2. No"
                            menu_response = core_processor.make_response.notitle_response(request, "more", message)
                            session_processor.store_menupoint.store_menupoint(request, "CEMCNF", stored_data)
                            libhandler.writelog(logfile, f"Message: {message}")

                        elif pay_id == "3":
                            # menu_response = core_processor.disable_service.service_disabled(request, "", goback_message)
                            charge = float(amount) * float(mtntelco_charge)
                            charge = "{0:.4f}".format(charge)
                            libhandler.writelog(logfile, f"Charge: {charge}")

                            total_amount = float(amount) + float(charge)
                            libhandler.writelog(logfile, f"total: {total_amount}")

                            stored_data = f"{stored_data}|{total_amount}|{charge}"
                            libhandler.writelog(logfile, f"Total amount: {total_amount}")

                            message = f"Processing Charge: GHC{charge}^You are paying a total of " \
                                      f"GHC {total_amount} as " \
                                      f"{service_name} from {momonum}.^Is this ok?^1. Yes^2. No"
                            menu_response = core_processor.make_response.notitle_response(request, "more", message)
                            session_processor.store_menupoint.store_menupoint(request, "CEMCNF", stored_data)
                            libhandler.writelog(logfile, f"Message: {message}")

                        else:
                            menu_response = core_processor.unknown_option.throw_unknown_option(request, "",
                                                                                               goback_message)
                    else:
                        menu_response = core_processor.unknown_option.throw_unknown_option(request, "",
                                                                                           goback_message)

            elif last_position == "CEMCNF":
                voucherid = ""
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")
                extract_reply = extract.split('|')
                service_id = extract_reply[0]
                service_name = extract_reply[1]
                membership_number = extract_reply[2]
                amount = extract_reply[3]
                narration = extract_reply[4]
                pay_name = extract_reply[6]
                pay_id = extract_reply[5]
                momonum = extract_reply[7]
                total_amount = extract_reply[8]
                charge = extract_reply[9]

                url = "https://cem-api.mesika.org/api/client-collections/v1/transactions/submit/"
                libhandler.writelog(logfile, f"Payload: {url}")

                trxid = get_secret_trxid()

                libhandler.writelog(logfile, f"Payload: {trxid}")
                total_votes = 0

                # if event_id == "1" or event_id == "2":
                total_votes = int(amount) * 2

                # elif event_id == "3":
                #     total_votes = int(amount)

                if userdata == "1":
                    if pay_id == "1" or pay_id == "3":
                        provider = ""
                        voucherid = ""
                        message = f"You have chosen to pay for {service_name} with GH{amount} from {momonum}^" \
                                  f"Please confirm by pressing ok and approving the MOMO transaction prompt. Thank you"
                        menu_response = core_processor.make_response.notitle_response(request, "end", message)
                        core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

                        if pay_id == "1":
                            provider = "MTN"

                        elif pay_id == "3":
                            provider = "AIRTELTIGO"

                        payload = {"reference_number": trxid, "account_number": momonum, "payer_msisdn": msisdn,
                                   "billed_amount": amount, "processing_fees": charge, "provider": provider,
                                   "narration": f"Service Payment for {service_name}",
                                   # "voucher_code": voucherid,
                                   "extra_details": {"service": service_name, "membership_number": membership_number}}
                        libhandler.writelog(logfile, f"Payload: {payload}")

                        response = requests.post(url, json=payload, verify=False)
                        libhandler.writelog(logfile, f"Submit Response: {response.text}")

                    elif pay_id == "2":

                        voucherid = extract_reply[10]

                        message = f"You have chosen to pay for {service_name} with GH{amount} from {momonum}^" \
                                  f"Thank you"
                        menu_response = core_processor.make_response.notitle_response(request, "end", message)
                        core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

                        payload = {"reference_number": trxid, "account_number": momonum, "payer_msisdn": msisdn,
                                   "billed_amount": amount, "processing_fees": charge, "provider": "VODAFONE",
                                   "narration": f"Service Payment for {service_name}",
                                   # "voucher_code": voucherid,
                                   "extra_details": {"service": service_name, "membership_number": membership_number}}
                        libhandler.writelog(logfile, f"Payload: {payload}")
                        #
                        response = requests.post(url, json=payload, verify=False)
                        libhandler.writelog(logfile, f"Submit Response: {response.text}")

                elif userdata == "2":
                    message = f"You have cancelled this payment."
                    menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                    libhandler.writelog(logfile, f"Message: {message}")

                else:
                    data = ""
                    menu_response = \
                        core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

            elif last_position == "CEMVDF":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")
                extract_reply = extract.split('|')

                service_id = extract_reply[0]
                service_name = extract_reply[1]
                membership_number = extract_reply[2]
                amount = extract_reply[3]
                narration = extract_reply[4]
                pay_name = extract_reply[6]
                pay_id = extract_reply[5]
                momonum = extract_reply[7]
                # total_amount = extract_reply[8]
                # charge = extract_reply[9]
                voucherid = userdata

                if not voucherid.isdigit():
                    message = "Voucher id entered is Invalid. Please enter again"
                    menu_response = core_processor.make_response.make_response(request, "more", message)
                    session_processor.store_menupoint.store_menupoint(request, "VOTVDF", extract)
                    libhandler.writelog(logfile, f"Message = {message}")

                elif voucherid.isdigit():
                    if len(userdata) < 6 or len(userdata) > 6:
                        message = f"Please check voucher id entered!^Enter voucher id again"
                        menu_response = core_processor.make_response.make_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "VOTVDF", extract)

                    elif len(userdata) == 6:
                        charge = 0

                        charge = float(amount) * float(vdftelco_charge)
                        charge = "{0:.4f}".format(charge)
                        libhandler.writelog(logfile, f"Charge: {charge}")

                        total_amount = float(amount) + float(charge)
                        stored_data = f"{extract}|{total_amount}|{charge}|{voucherid}"
                        libhandler.writelog(logfile, f"Total amount: {total_amount}")

                        message = f"Processing Charge: GHC{charge}^You are paying a total of " \
                                  f"GHC {total_amount} as " \
                                  f"{service_name} from {momonum}.^Is this ok?^1. Yes^2. No"
                        menu_response = core_processor.make_response.notitle_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "CEMCNF", stored_data)
                        libhandler.writelog(logfile, f"Message: {message}")



                    else:
                        menu_response = core_processor.unknown_option.throw_unknown_option(request, "",
                                                                                           goback_message)

            elif last_position == "GOBACK":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Status: {extract}")
                stored_data = extract

                message = ""
                count = 0
                response = {"service_list": [{"id": 1, "name": "First Fruit"},
                                         {"id": 2, "name": "Tithe"},
                                         {"id": 3, "name": "Pledge"},
                                         {"id": 4, "name": "Welfare"},
                                         {"id": 5, "name": "Christ To The Rural World"},
                                         {"id": 6, "name": "Day of Help"},
                                         {"id": 7, "name": "General Offering"}
                                         ]}

                for service in response['service_list']:
                    service_id = service['id']
                    service_name = service['name']
                    count += 1
                    message += str(count) + '. ' + str(service_name) + '^'

                str_conv = json.dumps(response['service_list'])  # converting list to json string
                stored_data = f"{str_conv}"

                message = f"Welcome to CHARISMATIC EVANGELISTIC MINISTRY Payment Service.^Select a service:^{message}"
                menu_response = core_processor.make_response.notitle_response(request, "more", message)
                session_processor.store_menupoint.store_menupoint(request, "SESSTR", stored_data)
                libhandler.writelog(logfile, f"Message: {message}")

            else:
                data = ""
                menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)




    except:
        data = ""
        menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)
        libhandler.log_error_detailed(logfile, "Error")

    libhandler.writelog(logfile, f"Sending message [ {menu_response} ]")

    return render_to_response('index.html', {'content': menu_response})
    # returns menuresponses to be placed in content-a template

