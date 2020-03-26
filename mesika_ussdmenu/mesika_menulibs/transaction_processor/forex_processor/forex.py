import transaction_processor.forex_processor as forex_processor
import core_processor
import session_processor
import api_processor

import json

logfile = "forex"


def get_forex(request, url, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "FRXLST":
        message = ""
        count = 0

        # payload = {}
        # response = core_processor.call_api(url, payload, "cowrybank", "getForexlist")
        # status = response['status']

        response = {"status": 200, "forex_list": [{"id": 1, "name": "US Dollars"},
                                                  {"id": 2, "name": "GB Pounds"},
                                                  {"id": 3, "name": "Euros"}]}
        status = 200

        if status == 200:
            for n in response['forex_list']:
                forex_id = n['id']
                currency = n['name']
                count += 1
                message += str(count) + '. ' + str(currency) + '^'

            str_conv = json.dumps(response['forex_list'])
            stored_data = f"{str_conv}"
            message = f"Select a currency:^{message}"
            menu_response = core_processor.make_response.notitle_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "FRXRTE", stored_data)
            forex_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = "Currencies cannot be displayed right now."
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            forex_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "FRXRTE":
        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        forex_processor.libhandler.writelog(logfile, f"Sel: {sel} and type: {type(sel)}")

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        forex_list = json.loads(extract)

        forex_id = forex_list[sel]['id']
        currency = forex_list[sel]['name']


        payload = {"forex_id": forex_id}
        # response = core_processor.call_api(url, payload, "cowrybank", "getForexrate")
        # status = response['status']

        status = 200
        if status == 200:
            message = f"You will receive a response shortly for the {currency} rate for today.Thank you"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            forex_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = f"The {currency} rate cannot be displayed right now"
            menu_response = core_processor.goto_start.goto_start(request, message, "", goback_message)
            forex_processor.libhandler.writelog(logfile, f"Message: {message}")

    else:
        menu_response = core_processor.unknown_option.thrown_unknown_option(request, "", goback_message)

    return menu_response

