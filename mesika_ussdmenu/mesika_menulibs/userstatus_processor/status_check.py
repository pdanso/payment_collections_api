import userstatus_processor
import core_processor
import session_processor

logfile = "status_check"


def status_check(support_num, msg, goback_message, bank_code):
    menu_response = ""
    # payload = {"msisdn": self.msisdn}
    # response = self.core_processor.call_api(url, payload, module, "check")
    # person_status = response['status']

    """ to be taken out"""
    person_status = 200
    if person_status == 200:
        # fname = response["first_name"]
        # note_enabled = response['note_enabled']
        # welcome_note = response['welcome']
        # otp_length = response['otp_length']
        # otp_status = response['is_otp']

        fname = "Miriam"
        note_enabled = True
        welcome_note = False
        otp_length = 4
        # otp_status = True

        """ to be taken out"""
        otp_status = False

        if not otp_status:
            """ activated - display main menu """
            payload = {}

            """outage_response = self.core_processor.call_api(url, payload, module, "checkServices")
            outage_status = outage_response['status'] """

            message = f"Support: {support_num}^Hello {fname},^{msg}^"
            message = f"{message}Please enter your secret pin"
            menu_response = core_processor.make_response.make_response("more", message)
            session_processor.store_sessionpoint.store_sessionpoint(f"OTPCHK|{otp_length}")
            userstatus_processor.libhandler.writelog(logfile, f"Message: {message}")

        elif otp_status:  # approved - reset pin
            message = f"Support: {support_num}^Hello {fname},^{msg}^Enter one-time pin to reset:"
            menu_response = core_processor.make_response.make_response("more", message)
            session_processor.store_sessionpoint.store_sessionpoint(f"PIN|{otp_length}")
            userstatus_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            data = ""
            menu_response = core_processor.unknown_option.throw_unknown_option(data, goback_message)

    elif person_status == 201:  # account blocked
        message = f"Sorry your account has been blocked due to irregular activities." \
                  "^Please visit your local {bank_code} branch."
        menu_response = core_processor.make_response.make_response("end", message)
        userstatus_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif person_status == 203:  # unapproved
        message = f"You are yet to be approved for {bank_code} services. You will " \
                  "receive your one-time pin soon or contact your local branch for assistance."
        menu_response = core_processor.make_response.make_response("end", message)
        userstatus_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif person_status == 400:  # not registered for mbanking
        signup_enabled = 0
        # signup_enabled = response["self_signup_enabled"]

        if signup_enabled == 1:  # enabled
            message = f"Sorry you are not registered for {bank_code} services.^" \
                      "Would you like to sign up now?^1. Yes^2. No"
            menu_response = core_processor.make_response.make_response("more", message)
            session_processor.store_session.store_session(userstatus_processor.msisdn, userstatus_processor.sessionid,
                                                          userstatus_processor.networkid, "REGSTR")
            userstatus_processor.libhandler.writelog(logfile, f"Message: {message}")

        else:
            message = f"Sorry you are not registered for {bank_code} Services.^Visit a nearby branch to " \
                      "sign up NOW!"
            menu_response = core_processor.make_response.make_response("end", message)
            userstatus_processor.libhandler.writelog(logfile, f"Message: {message}")

    else:  # not registered
        message = f"Sorry you are not registered as a customer of {bank_code}.^Visit a nearby branch to open" \
                  f" an account now! :)"
        menu_response =core_processor.make_response.make_response("end", message)
        userstatus_processor.libhandler.writelog(logfile, f"Message: {message}")

    return menu_response
