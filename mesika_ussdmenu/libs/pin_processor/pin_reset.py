import pin_processor
import core_processor
import session_processor
import api_processor

logfile = "pin_reset"


def pin_reset(request, url, msg, last_position, pos, modul, goback_message, otp_length=4):
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "PINCUR":
        message = "Enter current pin"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_session.store_session(msisdn, sessionid, networkid, "PINSTA")
        core_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "PINSTA":
        current_pin = userdata
        # payload = {"msisdn": msisdn, "pin": current_pin}
        # response = api_processor.call_api(url, "post", modul, "pinReset", payload)
        #
        # status = response['status']
        status = 200
        if status == 200:
            message = f"{msg}^Please enter your preferred {otp_length} digit pin to reset"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "PINRST", otp_length)
            pin_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = f"Pin entered is invalid.^Please enter pin again"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "PINSTA", otp_length)
            pin_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "PINRST":
        new_pin = userdata
        otp_length = session_processor.get_ussd_extra.get_ussd_extra(pos)
        pin_processor.libhandler.writelog(logfile, f"Length of pin: {len(str(new_pin))}")

        otp_length = int(otp_length)

        if len(new_pin) > otp_length or len(new_pin) < otp_length:
            """ Length of new pin entered should not be greater than or less than the set pin length"""
            message = "The length of the pin entered is Invalid."
            menu_response = core_processor.make_response.make_response(request, "end", message)
            pin_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = "Please re-enter your preferred pin"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "PINCNF", new_pin)
            pin_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "PINCNF":
        new_pin = session_processor.get_ussd_extra.get_ussd_extra(pos)
        re_pin = userdata

        if new_pin == re_pin:
            # payload = {"msisdn": msisdn, "pin": new_pin}
            # response = core_processor.call_api(url, payload, module, "pinReset")
            # status = response['status']

            status = 200
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
            message = "Pins do not match. Please try again"
            menu_response = core_processor.make_response.make_response(request, "end", message)
            pin_processor.libhandler.writelog(logfile, f"Message: {message}")

    else:
        data = ""
        menu_response = core_processor.unknown_option.throw_unknown_option(request, data, goback_message)

    return menu_response
