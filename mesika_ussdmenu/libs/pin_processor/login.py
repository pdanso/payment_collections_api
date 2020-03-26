import pin_processor
import core_processor
import session_processor
import api_processor

logfile = "login"


def login(request, url, msg, last_position, pos, modul, goback_message, otp_length=4):
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    status = 0

    if last_position == "LOGINN":
        pin = userdata
        # payload = {"msisdn": msisdn, "pin": current_pin}
        # response = api_processor.call_api(url, "post", modul, "pinReset", payload)
        #
        # status = response['status']
        status = 200

    return status
