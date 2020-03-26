import core_processor

logfile = "disable_service"


def service_disabled(request, data, goback_message):
    message = "This service is currently under maintenance and will be back shortly."
    menu_response = core_processor.goto_start.goto_start(request, message, data, goback_message)
    core_processor.libhandler.writelog(logfile, f"Message: {menu_response}")

    return menu_response
