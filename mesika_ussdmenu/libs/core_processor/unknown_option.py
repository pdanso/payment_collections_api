import core_processor

logfile = "unknown_option"


def throw_unknown_option(request, data, goback_message):
    message = "Sorry, the option selected is invalid. Please try again"
    menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
    core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

    return menu_response
