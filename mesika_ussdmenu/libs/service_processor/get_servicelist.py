import service_processor
import core_processor
import session_processor
import api_processor

import json

logfile = "get_servicelist"


def get_servicelist(request, url, modul, msg, action, next_position):
    payload = {}

    # response = api_processor.call_api(url, method, modul, action, payload)
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

        message = f"{msg}:^{message}"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, next_position, str_conv)
        service_processor.libhandler.writelog(logfile, f"Message:{message}")

    else:
        message = "No services are available right now. Please try again later"
        menu_response = core_processor.make_response.make_response(request, "end", message)
        service_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

    return menu_response
