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

import transaction_processor.airtime_processor.airtime as airtime_processor

import transaction_processor.mobile_money_processor.momo as momo_processor
import transaction_processor.mobile_money_processor.bank_wallet as momo_bankwallet
import transaction_processor.mobile_money_processor.wallet_bank as momo_walletbank

import transaction_processor.collections_processor.collections as collections_processor

import transaction_processor.payment_processor.payment_methods as payment_processor
import transaction_processor.payment_processor.momo_payment as pay_momo
import transaction_processor.payment_processor.bank_payment as pay_bank

import transaction_processor.forex_processor.forex as forex_processor

import pin_processor.pin_reset as pin_processor



# import Product_views.agency_services as agency_services
#
# import transaction_processor.deposit_processor.deposit as deposit_processor
# import transaction_processor.withdrawal_processor.initiate_withdrawal as withdraw_initiate
# import transaction_processor.withdrawal_processor.dispense_cash as withdrawal_processor

# import userstatus_processor.status_check
# import userstatus_processor.login


import os
import json
import string
import random
import requests
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

''' Initialising the logger '''

libhandler = Logger(app_or_directory_name="debug", host="local.mesika.org",
                    port=24777, version=1)
logfile = "new_design"

config_file_name = os.path.join(os.path.dirname(__file__), "/legacy_demo/2.0/mesika_ussdmenu/menu.json")
with open(config_file_name, 'r') as f:
    settings = json.load(f)

    bank_code = settings['bank_code']
    url = settings['url']
    bank_id = settings['bank_id']
    goback_message = settings['goback_message']
    api_version = settings['api_version']


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
            message = "Mesika Test"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_session.store_session(msisdn, sessionid, networkid, f"SESSTA")
            libhandler.writelog(logfile, f"Message: {message}")

        else:
            pos = session_processor.get_last_step.get_last_step(msisdn, sessionid, networkid)
            last_position = pos[0:6]
            menu_mod = pos[0:3]
            libhandler.writelog(logfile, f"POS: {pos}")
            libhandler.writelog(logfile, f"Last position: {pos}")

            if last_position == "SESSTA":
                menu_response = airtime_processor.airtime(request, url, "", "AIRSUB", goback_message, pos)

            elif menu_mod == "AIR":
                menu_response = airtime_processor.airtime(request, url, "", last_position, goback_message, pos)


            # elif menu_mod == "AIR":
            #     menu_response = trans_airtime.airtime(request, url, "", last_position, "Enter any digit", pos)
            #
            # elif menu_mod == "PIN":
            #     menu_response = pin_processor.pin_reset.pin_reset(request, url, "hello", last_position, pos, "", goback_message)
            #
            # else:
            #     menu_response = core_processor.unknown_option.throw_unknown_option(request, "", goback_message)
            #


    except:
        data = ""
        # menu_response = throw_unknown_option(data, goback_message)
        libhandler.log_error_detailed(logfile, "Error")

    libhandler.writelog(logfile, f"Sending message [ {menu_response} ]")

    return render_to_response('index.html', {'content': menu_response})
    # returns menuresponses to be placed in content-a template

