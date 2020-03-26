import transaction_processor.funds_transfer_processor as ft_processor
import transaction_processor.funds_transfer_processor.internal as internal
import transaction_processor.funds_transfer_processor.gip as gip
import core_processor.make_response
import session_processor.store_menupoint
import session_processor.store_session
import core_processor.disable_service
import core_processor
import json

logfile = "funds_transfer"


def funds_transfer(request, url, bank_code, data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]
    token = data
    ft_processor.libhandler.writelog(logfile, f"Message: {token}")

    if last_position == "FNDSUB":
        # payload = {"service_id": service_id}
        #
        # response = self.core_processor.call_api(url, payload, "cowrybank", "getSubService")
        # status = response['status']
        #
        # message = ""
        # count = 0
        #
        # for n in response['subservices']:
        #     subservice_id = n['id']
        #     subservice_name = n['name']
        #     count += 1
        #
        #     message += str(count) + '. ' + str(subservice_name) + '^'

        response = {"subservices": [{"id": 1, "name": f"{bank_code} account"}, {"id": 2, "name": "Another bank"} ]}
        str_conv = json.dumps(response['subservices'])

        message = f"Select type of transfer:^1. {bank_code} account"

        str_conv = json.dumps(response['subservices'])
        stored_data = f"{str_conv}|{token}"
        # message = f"Please select an option:^{message}"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "FNDSEL", stored_data)
        # session_processor.store_menupoint.store_menupoint(request, "FNDSEL", str_conv)
        ft_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "FNDSEL":
        sel0 = userdata
        ft_processor.libhandler.writelog(logfile, f"Userdata: {sel0} and {type(sel0)}")
        sela = int(sel0)
        sel = sela - 1
        ft_processor.libhandler.writelog(logfile, f"Subservice_list: {sel} and {type(sel)}")

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        extractreply = extract.split('|')

        service_list = extractreply[0]
        token_new = extractreply[1]

        subservice_list = json.loads(service_list)

        subservice_id = subservice_list[sel]['id']
        subservice_name = subservice_list[sel]['name']
        ft_processor.libhandler.writelog(logfile, f"id: {subservice_id} and name: {subservice_name} ")


        # if ft_processor.userdata == -1:
        #     menu_response = self.ussd_processor.get_servicelist(bank_id, "cowrybank", "getServicelist")
        #     libhandler.writelog(logfile, f"Message: {menu_response}")

        if subservice_id == 1:  # internal bank transfer
            menu_response = ft_processor.internal.internal(request, url, bank_code, token_new,
                                                           "FTRACL", goback_message, pos)

   #     elif subservice_id == 2: # gip
   #         data = ""
    #        menu_response = ft_processor.gip.gip(request, url, bank_code, service_id, "GIPSUB", goback_message,
     #                                            pos)

    elif pos[0:3] == "FTR":
        menu_response = ft_processor.internal.internal(request, url, bank_code, token,
                                                       last_position, goback_message, pos)

    elif pos[0:3] == "GIP":
        menu_response = ft_processor.gip.gip(request, url, bank_code, service_id, last_position, goback_message,
                                             pos)

    else:
        menu_response = core_processor.unknown_option.thrown_unknown_option(request, token, goback_message)

    return menu_response


