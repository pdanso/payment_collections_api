import service_processor
import core_processor
import session_processor
import json

logfile = "get_servicelist"


def get_servicelist(url, modul, msg, action, last_position):
    payload = {}

    # response = core_processor.call_api(url, payload, module, action)
    # libhandler.writelog(logfile, f"Api call: {response}")
    # status = response['status']

    status = 200
    if status == 200:
        message = ""
        count = 0

        # response = {"reason": "hello", "services": [{"id": 1, "name": "Check Commission Balance"},
        #                                            {"id": 2, "name": "Deposit"}, {"id": 3, "name": "Withdrawal"}]}
        response = {"reason": "hello", "services": [{"id": 1, "name": "VIVA Plus Capsules(Large)"},
                                                     {"id": 2, "name": "VIVA Plus Capsules(Small)"},
                                                     {"id": 3, "name": "VIVA Plus Powder(Large)"},
                                                     {"id": 4, "name": "VIVA Plus Powder(Small)"},
                                                     {"id": 5, "name": "OBIRI Mixture"}]}

        for n in response['services']:
            service_id = n['id']
            service = n['name']
            service = service.title()
            count += 1
            message += str(count) + '. ' + str(service) + '^'

        str_conv = json.dumps(response['services'])  # converting list to json string

        message = f"{msg}:^{message}"
        menu_response = core_processor.make_response.make_response("more", message)
        session_processor.store_menupoint.store_menupoint(f"{last_position}|{str_conv}")
        service_processor.libhandler.writelog(logfile, f"Message:{message}")

    else:
        message = "No services are available right now. Please try again later"
        menu_response = core_processor.make_response.make_response("end", message)
        service_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

    return menu_response
