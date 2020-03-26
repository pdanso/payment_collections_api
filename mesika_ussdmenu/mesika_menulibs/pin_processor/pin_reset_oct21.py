import pin_processor
import core_processor
import session_processor
import api_processor

logfile = "pin_reset"


def pin_reset(request, endpoint, msg, last_position, pos, goback_message):
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]
    phone_number = msisdn

    if last_position == "PINCUR":
        message = "Enter current pin"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_session.store_session(msisdn, sessionid, networkid, "PINSTA")
        core_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "PINSTA":
        current_pin = userdata

        url = f"{endpoint}customers/authenticate/{phone_number}/"
        payload = {"pin": current_pin}
        response = api_processor.api_json.call_api(url, "post", payload, "")

        status = response['status']
        # status = 200
        if status == 200:
            token = response['customer_auth_token']
            stored_data = f"{token}|{current_pin}"

            message = f"{msg}^Please enter your preferred pin to reset"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "PINRST", stored_data)
            pin_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = "Pin reset failed as pin entered is wrong. Please try again later"
            menu_response = core_processor.make_response.make_response(request, "end", message)
            pin_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "PINRST":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        new_pin = userdata

        stored_data = f"{extract}|{new_pin}"

        message = "Please re-enter your preferred pin"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "PINCNF", stored_data)
        pin_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "PINCNF":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extractreply = extract.split('|')
        token = extractreply[0]
        current_pin = extractreply[1]
        new_pin = extractreply[2]

        re_pin = userdata

        if new_pin == re_pin:
            endpoint = f"{endpoint}customers/set-new-pin/{phone_number}/"
            headers = {"HTTP_X_CUSTOMER_AUTH_TOKEN": token}
            payload = {"current_pin": current_pin, "new_pin": new_pin}
            response = api_processor.api_json.call_api(endpoint, "post", payload, headers)
            status = response['status']

            if status == 200:
                message = "You have successfully reset your pin. Please " \
                          "log in again to enjoy this service" \
                          "^Thank you"
                menu_response = core_processor.make_response.make_response(request, "end", message)
                pin_processor.libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Pin reset failed. Please try again later"
                menu_response = core_processor.make_response.make_response(request, "end", message)
                pin_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = "Pins do not match. Please enter new pin:"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "PINRST", current_pin)
            pin_processor.libhandler.writelog(logfile, f"Message: {message}")
    else:
        data = ""
        menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

    return menu_response

