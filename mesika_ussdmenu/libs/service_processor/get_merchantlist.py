import service_processor
import core_processor
import session_processor
import api_processor

import json

logfile = "get_merchantlist"


def get_merchantlist(url, request, stored_data, next_position, goback_message ):
    payload = {}
    # response = api_processor.call_api(url, "get", modul, "getMerchantlist", payload)
    # status = response['status']

    response = {"reason": "hello", "merchants": [{"id": 1, "name": "MTN"},
                                                        {"id": 2, "name": "AirtelTigo"},
                                                        {"id": 3, "name": "Vodafone"}]}


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
        menu_response = core_processor.make_response.make_response(request, "more", message)
        service_processor.libhandler.writelog(logfile, f"Message: {message}")
        session_processor.store_menupoint.store_menupoint(request, "AIRTME", stored_data)

    else:
        message = "Merchant list cannot be displayed right now. Please try again later"
        menu_response = core_processor.goto_start.goto_start(request, message, stored_data, goback_message)
        service_processor.libhandler.writelog(logfile, f"Message: {message}")

