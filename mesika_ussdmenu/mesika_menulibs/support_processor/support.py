import support_processor
import core_processor
import session_processor
import json

logfile = "support"


def customerCare(url, service_id, last_position, goback_message, pos):
    menu_response = ""
    if last_position == "CUSLST":
        message = "Please select an option:^1. Report Issue^2. " \
                  "Re-open Issue^3. Close Issue^4. Reversal of funds^5. Check Report Status"
        menu_response = core_processor.make_response.make_response("more", message)
        session_processor.store_session.store_session(support_processor.msisdn, support_processor.sessionid,
                                                      support_processor.networkid, "CUSCRE")
        support_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "CUSCRE":
        cust_type = support_processor.userdata

        if cust_type == "1" or cust_type == "2" or cust_type == "3" or cust_type == "5":  # report issue
            payload = {}

            # response = core_processor.call_api(url, payload, "cowrybank", "getServicelist")
            # libhandler.writelog(logfile, f"Api call: {response}")
            # status = response['status']
            status = 200

            response = {"reason": "hello", "services": [{"id": 1, "name": "VIVA Plus Capsules(Large)"},
                                                        {"id": 2, "name": "VIVA Plus Capsules(Small)"},
                                                        {"id": 3, "name": "VIVA Plus Powder(Large)"},
                                                        {"id": 4, "name": "VIVA Plus Powder(Small)"},
                                                        {"id": 5, "name": "OBIRI Mixture"}]}
            if status == 200:
                message = ""
                count = 0

                for n in response['services']:
                    service_id = n['id']
                    service = n['name']
                    service = service.title()
                    count += 1
                    message += str(count) + '. ' + str(service) + '^'

                str_conv = json.dumps(response['services'])  # converting list to json string
                stored_data = f"{cust_type}-{str_conv}"

                message = f"Please select an option:^{message}0. Settings"
                menu_response = core_processor.make_response.make_response("more", message)
                session_processor.store_menupoint.store_menupoint(f"CUSSEL|{stored_data}")
                support_processor.libhandler.writelog(logfile, f"Message:{message}")

            else:
                message = "No services are available right now. Please try again later"
                menu_response = core_processor.make_response.make_response("end", message)
                core_processor.libhandler.writelog(logfile, f"Message: {response}")

        elif cust_type == "4":  # reverse funds
            message = "Service disabled"
            msg = f"{message}^Enter 1 for the Main Menu or 2 for Customer Care."
            menu_response = core_processor.make_response.make_response("more", msg)
            session_processor.store_session.store_session(support_processor.msisdn, support_processor.sessionid,
                                                          support_processor.networkid, "GOBACK")
            support_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            data = ""
            menu_response = core_processor.unknown_option.throw_unknown_option(data, goback_message)

    elif last_position == "CUSSEL":
        sel0 = support_processor.userdata
        sel0 = int(sel0)
        sel = sel0 - 1

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extract_reply = extract.split('-')
        service_list = extract_reply[1]
        cust_type = extract_reply[0]

        service_list = json.loads(service_list)  # converting json string back to dict
        support_processor.libhandler.writelog(logfile, f"JSON loads {service_list}")

        service_id = service_list[sel]['id']
        service_name = service_list[sel]['name']
        support_processor.libhandler.writelog(logfile, f"extract1: {service_id} and extract2: {service_name}")

    else:
        data = ""
        menu_response = core_processor.unknown_option.throw_unknown_option(data, goback_message)

    return menu_response