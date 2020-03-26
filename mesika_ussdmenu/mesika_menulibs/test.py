'''
Created: August 5, 2018 3:26pm
author: d33v4sn1p3r1
'''

from django.shortcuts import render_to_response

import json
import string
import random
import requests
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from mesika_libs.logging import Logger
from mesika_libs.Caching import Cacher

import core_processor.make_response
import core_processor.goto_start
import core_processor.unknown_option
import core_processor.disable_service
#
import session_processor.store_session
import session_processor.store_menupoint
import session_processor.get_last_step
import session_processor.get_ussd_extra
import pin_processor.pin_reset

import transaction_processor.airtime_processor.airtime as trans_airtime


# import mesika_menulibs.core_processor
# import mesika_menulibs.reset_pin
# import core_processor.make_response as core
#import core_processor.goto_start
# from core_processor.make_response import make_response
# from mesika_menulibs.core_processor.goto_start import goto_start
# from mesika_menulibs.core_processor.throw_unknown_option import throw_unknown_option
#
# from mesika_menulibs.coreprocessor import CoreProcessor
# from mesika_menulibs.ussdProcessor import UssdProcessor
# from mesika_menulibs.transactionProcessor import TransactionProcessor

''' Initialising the logger '''

libhandler = Logger(app_or_directory_name="debug", host="local.mesika.org",
                    port=24777, version=1)
logfile = "new_design"

goback_message = "Enter any digit to continue!"
url = "https://magnet.mesika.org:1000"

small_size = 12


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
            # menu_response = trans_airtime.airtime(url, "", "AIRSUB", "Enter any digit", "")
            # menu_response = pin_processor.pin_reset.pin_reset(url, "hello", "PINCUR", "PINCUR", "", goback_message)
            message = "Welcome to Herbal Technology.^Please select an option:^1. View Products^2. Buy Product" \
                      "^3. Subscribe"
            menu_response = core_processor.make_response.make_response("more", message)
            session_processor.store_session.store_session(msisdn, sessionid, networkid, f"AIRWHO")
            libhandler.writelog(logfile, f"Message: {message}")

        else:
            pos = session_processor.get_last_step.get_last_step(msisdn, sessionid, networkid)
            last_position = pos[0:6]
            menu_mod = pos[0:3]
            libhandler.writelog(logfile, f"POS: {pos}")
            libhandler.writelog(logfile, f"Last position: {pos}")

            if last_position == "AIRSUB":
                data = ""
                response = [{"id": 1, "name": "Topup for myself"}, {"id": 2, "name": "Topup Another Number"}]
                str_conv = json.dumps(response)
                data = f"{str_conv}|{data}"

                message = "Select type of transfer:^1. Topup for myself^2. Topup Another Number"
                session_processor.store_session.store_session(msisdn, sessionid, networkid, f"AIRWHO|{data}")
                menu_response = core_processor.make_response.make_response("more", message)
                # session_processor.store_sessionpoint.store_sessionpoint(f"AIRWHO|{data}")

                libhandler.writelog(logfile, f"Message: {message}")

            elif last_position == "AIRWHO":
                sel0 = userdata
                sel0 = int(sel0)
                sel = sel0 - 1
                libhandler.writelog(logfile, f"sel = {sel}")

                extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
                libhandler.writelog(logfile, f"Extract: {extract}")

                extract_reply = extract.split('|')
                airtime_list = extract_reply[0]
                service_id = extract_reply[1]

                airtime_type = json.loads(airtime_list)
                airtime_id = airtime_type[sel]['id']
                airtime_name = airtime_type[sel]['name']
                libhandler.writelog(logfile, f"Airtime: {airtime_id}. {airtime_name}")

                stored_data = f"{service_id}:{airtime_id}"
                libhandler.writelog(logfile, f"Stored data: {stored_data}")

                response = {"reason": "hello", "merchants": [{"id": 1, "name": "MTN"},
                                                             {"id": 2, "name": "AirtelTigo"},
                                                             {"id": 3, "name": "Vodafone"}]}

                # payload = {}
                # response = api_processor.api_json.api_js(url, payload, "cowrybank", "getMerchantlist")
                # status = response['status']
                status = 200

                if status == 200:
                    message = ""
                    count = 0
                    for n in response['merchants']:
                        merchant_id = n['id']
                        merchant_name = n['name']
                        count += 1
                        message += str(count) + '. ' + str(merchant_name) + '^'

                    str_conv = json.dumps(response['merchants'])

                    stored_data = f"{stored_data}?{str_conv}"
                    message = f"Please select a network:^{message}"
                    menu_response = core_processor.make_response.make_response("more", message)
                    libhandler.writelog(logfile, f"Message: {message}")
                    session_processor.store_menupoint.store_menupoint(f"AIRTME|{stored_data}")

                else:
                    message = "Merchant list cannot be displayed right now. Please try again later"
                    msg = f"{message}^Enter 1 for the Main Menu or 2 for Customer Care."
                    menu_response = core_processor.make_response.make_response("more", msg)
                    session_processor.store_session.store_session(trans_airtime.msisdn, trans_airtime.sessionid,
                                                                  trans_airtime.networkid, "GOBACK")
                    trans_airtime.libhandler.writelog(logfile, f"Message: {message}")

            elif menu_mod == "AIR":
                menu_response = trans_airtime.airtime(url, "", last_position, "Enter any digit", pos)

            elif menu_mod == "PIN":
                menu_response = pin_processor.pin_reset.pin_reset(url, "hello", last_position, pos, "", goback_message)

            else:
                menu_response = core_processor.unknown_option.throw_unknown_option("", goback_message)



    except:
        data = ""
        # menu_response = throw_unknown_option(data, goback_message)
        libhandler.log_error_detailed(logfile, "Error")

    libhandler.writelog(logfile, f"Sending message [ {menu_response} ]")

    return render_to_response('index.html', {'content': menu_response})
    # returns menuresponses to be placed in content-a template

