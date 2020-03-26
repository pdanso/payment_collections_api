'''
Created: November 24, 2018 3:02pm
author: d33v4sn1p3r1
'''

from django.shortcuts import render_to_response

from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

# import product_views.mobile_banking.libhandler as mobile_banking
import core_processor.make_response
import core_processor.goto_start
import core_processor.unknown_option
import core_processor.disable_service

import session_processor.store_session
import session_processor.store_menupoint
import session_processor.get_last_step
import session_processor.get_ussd_extra

import service_processor.get_servicelist

import transaction_processor.funds_transfer_processor.funds_transfer as ft_processor
import transaction_processor.funds_transfer_processor.gip as gip_processor

import transaction_processor.airtime_processor.airtime as trans_airtime

import transaction_processor.mobile_money_processor.momo as momo_processor
import transaction_processor.mobile_money_processor.bank_wallet as momo_bankwallet
import transaction_processor.mobile_money_processor.wallet_bank as momo_walletbank

import transaction_processor.collections_processor.collections as collections_processor

import transaction_processor.payment_processor.payment_methods as payment_processor
import transaction_processor.payment_processor.momo_payment as pay_momo
import transaction_processor.payment_processor.bank_payment as pay_bank

import transaction_processor.forex_processor.forex as forex_processor

import transaction_processor.account_processor.balance_enquiry as balance_enquiry

import pin_processor.pin_reset as pin_processor

import transaction_processor.deposit_processor.deposit as deposit_processor
import transaction_processor.withdrawal_processor.initiate_withdrawal as withdraw_initiate
import transaction_processor.withdrawal_processor.dispense_cash as withdrawal_processor


import json
import os
import string
import random
import requests
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

libhandler = Logger(app_or_directory_name="Xplore", host="local.mesika.org",
                    port=24777, version=1)

config_file_name = os.path.join(os.path.dirname(__file__), "/legacy_demo/2.0/mesika_ussdmenu/menu.json")
with open(config_file_name, 'r') as f:
    settings = json.load(f)

    bank_code = settings['bank_code']
    url = settings['url']
    bank_id = settings['bank_id']
    goback_message = settings['goback_message']
    api_version = settings['api_version']
    logfile = settings['logfile']


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
            # check_profile

            message = f"Welcome to {bank_code} Mobile Banking Services.^Please enter your secret pin:"
            menu_response = core_processor.make_response.notitle_response(request, "more", message)
            session_processor.store_session.store_session(msisdn, sessionid, networkid, "SESSTA")
            libhandler.writelog(logfile, f"Message: {message}")

        else:
            pos = session_processor.get_last_step.get_last_step(msisdn, sessionid, networkid)
            last_position = pos[0:6]
            menu_mod = pos[0:3]
            libhandler.writelog(logfile, f"POS: {pos}")

            if last_position == "SESSTA":

                # check on the pin

                menu_response = service_processor.get_servicelist.get_servicelist(request, url,
                                                                                  "", "Select an option",
                                                                                  "getServicelist", "MBASTA")

            elif last_position == "MBASTA":
                sel0 = userdata
                sel0 = int(sel0)
                sel = sel0 - 1

                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

                service_list = json.loads(extract)
                service_id = service_list[sel]['id']
                service_name = service_list[sel]['name']
                libhandler.writelog(logfile, f"Service_list: {service_id}. {service_name}")

                if service_id == 1:
                    # balance check
                    # response = balance_enquiry.balance_check(url, account_number)

                    message = "Your balance is GHS 150, 000."
                    menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
                    libhandler.writelog(logfile, f"Message: {message}")

                elif service_id == 2:
                    menu_response = ft_processor.funds_transfer(request, url, bank_code, 3,
                                                                "FNDSUB", goback_message, pos)

                elif service_id == 3:
                    menu_response = trans_airtime.airtime(request, url, "", "AIRSUB", goback_message, pos)

                elif service_id == 4:
                    menu_response = momo_processor.momo(request, url, bank_code, 3, "MOMSUB", goback_message, pos)

                elif service_id == 5:
                    menu_response = collections_processor.collections(request, "", "",
                                                                      "COLSTA",
                                                                      pos, goback_message)

                elif service_id == 6:
                    menu_response = forex_processor.get_forex(request, url, "FRXLST", goback_message, pos)

                elif service_id == 7:
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

                menu_response = service_processor.get_servicelist.get_servicelist(request, url,
                                                                                  "", "Select an option",
                                                                                  "getServicelist", "MBASTA")

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

    except:
        data = ""
        menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)
        libhandler.log_error_detailed(logfile, "Error")

    libhandler.writelog(logfile, f"Sending message [ {menu_response} ]")

    return render_to_response('index.html', {'content': menu_response})
    # returns menuresponses to be placed in content-a template

