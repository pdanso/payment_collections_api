import transaction_processor.mobile_money_processor as momo_processor
import core_processor.make_response
import session_processor.store_menupoint
import session_processor.store_session
import core_processor.disable_service
import core_processor
import json

logfile = "momo"


def momo(request, url, bank_code, data, last_position, goback_message, pos):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "MOMSUB":
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

        response = {"subservices": [{"id": 1, "name": f"{bank_code} account to Momo"},
                                    {"id": 2, "name": f"Momo to {bank_code} Account"}]}
        str_conv = json.dumps(response['subservices'])

        message = f"Select type of transfer:^1. {bank_code} account to Momo^2. Momo to {bank_code} Account"

        str_conv = json.dumps(response['subservices'])
        # message = f"Please select an option:^{message}"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MOMSEL", str_conv)
        momo_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "MOMSEL":
        sel0 = userdata
        momo_processor.libhandler.writelog(logfile, f"Userdata: {sel0} and {type(sel0)}")
        sela = int(sel0)
        sel = sela - 1
        momo_processor.libhandler.writelog(logfile, f"Subservice_list: {sel} and {type(sel)}")

        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)
        subservice_list = json.loads(extract)

        subservice_id = subservice_list[sel]['id']
        subservice_name = subservice_list[sel]['name']
        momo_processor.libhandler.writelog(logfile, f"id: {subservice_id} and name: {subservice_name} ")


        # if ft_processor.userdata == -1:
        #     menu_response = self.ussd_processor.get_servicelist(bank_id, "cowrybank", "getServicelist")
        #     libhandler.writelog(logfile, f"Message: {menu_response}")

        if subservice_id == 1:  # bank to wallet
            menu_response = momo_processor.bank_wallet.momo_credit(request, url, bank_code, 3,
                                                                   "MCRCHG", goback_message, pos)

        elif subservice_id == 2: # momo to wallet
            menu_response = momo_processor.wallet_bank.momo_debit(request, url, bank_code, 3, "MDBCHG",
                                                                  goback_message, pos)

    elif pos[0:3] == "MCR":
        menu_response = momo_processor.bank_wallet.momo_credit(request, url, bank_code, 3,
                                                               last_position, goback_message, pos)

    elif pos[0:3] == "MDB":
        menu_response = momo_processor.wallet_bank.momo_debit(request, url, bank_code, 3,
                                                              last_position, goback_message, pos)


    else:
        menu_response = core_processor.unknown_option.thrown_unknown_option(request, data, goback_message)

    return menu_response
