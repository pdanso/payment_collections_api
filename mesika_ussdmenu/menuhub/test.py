'''
Created: August 5, 2018 3:26pm
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

import userstatus_processor.status_check
import userstatus_processor.login



import json
import string
import random
import requests
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


''' Initialising the logger '''

libhandler = Logger(app_or_directory_name="Xplore", host="local.mesika.org",
                    port=24777, version=1)
logfile = "test"

goback_message = "Enter any digit to continue!"
url = "https://magnet.mesika.org:1000"

bank_code = "Mesika"


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
            message = "Welcome to MeSIKA Xplore Development. Select an option:^1. Mobile banking^2. Mobile Loans^3. " \
                      "Agency Services^4. Mobile Collections"
            menu_response = core_processor.make_response.notitle_response(request, "more", message)
            session_processor.store_session.store_session(msisdn, sessionid, networkid, "SESSTA")
            libhandler.writelog(logfile, f"Message: {message}")

        else:
            pos = session_processor.get_last_step.get_last_step(msisdn, sessionid, networkid)
            last_position = pos[0:6]
            menu_mod = pos[0:3]
            libhandler.writelog(logfile, f"POS: {pos}")

            if last_position == "SESSTA":

                if userdata == "1":
                    # call api to give mbanking submenu
                    payload = {}

                    # response = self.core_processor.call_api(url, payload, module, action)
                    # libhandler.writelog(logfile, f"Api call: {response}")
                    # status = response['status']

                    status = 200
                    if status == 200:
                        message = ""
                        count = 0

                        response = {"reason": "hello", "services": [{"id": 1, "name": "Check Balance"},
                                                                    {"id": 2, "name": "Funds Transfer"},
                                                                    {"id": 3, "name": "Airtime"},
                                                                    {"id": 4, "name": "Mobile Money"},
                                                                    {"id": 5, "name": "Collections"},
                                                                    {"id": 6, "name": "Forex"},
                                                                    {"id": 7, "name": "Settings"}, ]}

                        for n in response['services']:
                            service_id = n['id']
                            service = n['name']
                            service = service.title()
                            count += 1
                            message += str(count) + '. ' + str(service) + '^'

                        str_conv = json.dumps(response['services'])  # converting list to json string

                        message = f"Please select an option:^{message}"
                        menu_response = core_processor.make_response.make_response(request, "more", message)
                        session_processor.store_menupoint.store_menupoint(request, "MBASTA", str_conv)
                        libhandler.writelog(logfile, f"Message:{message}")

                    else:
                        message = "No services are available right now. Please try again later"
                        menu_response = core_processor.make_response.make_response(request, "end", message)
                        libhandler.writelog(logfile, f"Message: {menu_response}")

                elif userdata == "2":
                    menu_response = loans_processor.loans(request, "", bank_code, "LONSTA", pos, goback_message)

 #               elif userdata == "3":
  #                  message = ""

                elif userdata == "4":
                    menu_response = collections_processor.collections(request, "", "", "COLSTA", pos, goback_message)

                else:
                    message = "Services are temporarily unavailable be enabled shortly."
                    menu_response = core_processor.make_response.make_response(request, "end", message)
                    libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "MBASTA":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")

                if userdata == "1":  # airtimemessage = f"Please select an option:^{message}"
                    message = "Your balance is GHS 150, 000."
                    menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                    libhandler.writelog(logfile, f"Message: {message}")

                elif userdata == "2":
                    menu_response = ft_processor.funds_transfer(request, url, bank_code, 3,
                                                                "FNDSUB", goback_message, pos)

                elif userdata == "3":
                    menu_response = trans_airtime.airtime(request, url, "", "AIRSUB", goback_message, pos)

                elif userdata == "4":
                    menu_response = momo_processor.momo(request, url, bank_code, 3, "MOMSUB", goback_message, pos)

                elif userdata == "5":
                    menu_response = collections_processor.collections(request, "", "",
                                                                                  "COLSTA",
                                                                                  pos, goback_message)

                elif userdata == "6":
                    menu_response = forex_processor.get_forex(request, url, "FRXLST", goback_message, pos)

                elif userdata == "7":
                    message = "Select an option:^1. View Profile^2. Pin Reset^3. View Recent Transactions"
                    menu_response = core_processor.make_response.notitle_response(request, "more", message)
                    session_processor.store_session.store_session(msisdn, sessionid, networkid, "SETSUB")
                    libhandler.writelog(logfile, f"Message: {message}")

                else:
                    data = ""
                    menu_response = core_processor.disable_service.service_disabled(request, data, goback_message)
                    # libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "GOBACK":
                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Status: {extract}")
                stored_data = extract

                message = "Welcome to MeSIKA Explore. Select an option:^1. Mobile banking^2. Mobile Loans^3. " \
                          "Agency Services^4. Mobile Collections"
                menu_response = core_processor.make_response.make_response(request, "more", message)
                session_processor.store_session.store_session(msisdn, sessionid, networkid, "SESSTA")
                libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "SETSUB":
                if userdata == "1":
                    # cll api
                    message = "Profile:^Name: Miriam Mineko^Number: 050 xxxxxxx"
                    menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                    libhandler.writelog(logfile, f"Message: {message}")

                elif userdata == "2":
                    menu_response = pin_processor.pin_reset(request, url, "", "PINCUR", pos,
                                                            "", goback_message, otp_length=4)

                elif userdata == "3":
                    message = "Your recent transactions will be sent to you via text shortly!"
                    menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                    libhandler.writelog(logfile, f"Message: {message}")

                else:
                    menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)

            elif menu_mod == "FND":
                menu_response = ft_processor.funds_transfer(request, url, bank_code, 3,
                                                            last_position, goback_message, pos)
            elif menu_mod == "GIP":
                menu_response = gip_processor.gip(request, url, bank_code, 3, last_position, goback_message,
                                                     pos)

            elif menu_mod == "AIR":
                menu_response = trans_airtime.airtime(request, url, "", last_position, goback_message, pos)

            elif menu_mod == "MOM":
                menu_response = momo_processor.momo(request, url, bank_code, 3, last_position, goback_message, pos)

            elif menu_mod == "MCR":
                menu_response = momo_bankwallet.momo_credit(request, url, bank_code, 3,
                                                       last_position, goback_message, pos)

            elif menu_mod == "MDB":
                menu_response = momo_walletbank.momo_debit(request, url, bank_code, 3,
                                                      last_position, goback_message, pos)

            elif menu_mod == "COL":
                menu_response = collections_processor.collections(request, url, "",
                                                                              last_position,
                                                                              pos, goback_message)
            elif menu_mod == "MDE":
                menu_response = payment_processor.pay_methods(request, url, "", last_position, goback_message, pos)

            elif menu_mod == "MPM":
                menu_response = pay_momo.momo_pay(request, url, "", last_position, goback_message, pos)

            elif menu_mod == "MPB":
                menu_response = pay_bank.bank_pay(request, url, "", last_position, goback_message, pos)

            elif menu_mod == "FRX":
                menu_response = forex_processor.get_forex(request, url, last_position, goback_message, pos)

            elif menu_mod == "PIN":
                menu_response = pin_processor.pin_reset(request, url, "", last_position, pos,
                                                        "", goback_message, otp_length=4)

            elif menu_mod == "LON":
                menu_response = loans_processor.loans(request, "", bank_code, last_position, pos, goback_message)



    except:
        data = ""
        menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)
        libhandler.log_error_detailed(logfile, "Error")

    libhandler.writelog(logfile, f"Sending message [ {menu_response} ]")

    return render_to_response('index.html', {'content': menu_response})
    # returns menuresponses to be placed in content-a template

