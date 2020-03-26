import transaction_processor.collections_processor as collections_processor
import core_processor
import session_processor
import api_processor

import requests
import json

logfile = "collections"


def collections(request, url, msg, last_position, pos, goback_message):
    menu_response = ""
    msisdn = request.GET["msisdn"]
    networkid = request.GET["networkid"]
    sessionid = request.GET["sessionid"]
    mode = request.GET["mode"]
    userdata = request.GET["userdata"]

    if last_position == "COLSTA":
        # check validity of customer
        # list all billers

        payload = {}
        # response = api_processor.api_get.api_get(url, payload, package, modul, actionurl, payload, "cowrypay", "getProductslist")
#        url = "https://10.85.85.80:47777/api/digital-payment-collections/v2/products/product-list/"
 #       result = requests.get(url, verify=False, timeout=10)
  #      results = result.text
   #     collections_processor.libhandler.writelog(logfile, f"Response: {results}")
#
 #       response = json.loads(results)
        response = {"status": 200, "product_list": [{"product_uuid": 1, "product_name": "DSTV"},
                                                            {"product_uuid": 2, "product_name": "GOTV"}]}
        status = 200

        if status == 200:
            count = 0
            message = ""
            for n in response['product_list']:
                prd_id = n['product_uuid']
                prod_name = n['product_name']

                count += 1
                message += '^' + str(count) + '. ' + str(prod_name)

            store_array = response['product_list']
            str_conv = json.dumps(store_array)
            stored_data = f"{str_conv}"
            # nun = ""
            message = f"{msg}^Select an option:^1. DSTV^2. GOTV"
            menu_response = core_processor.make_response.make_response(request, "more", message)
            session_processor.store_menupoint.store_menupoint(request, "COLOPT", stored_data)
            collections_processor.libhandler.writelog(logfile, f"Message: {message}")

    elif last_position == "COLOPT":
        extract = session_processor.get_ussd_extra.get_ussd_extra(pos)

        product_list = json.loads(extract)

        sel0 = userdata
        sel0 = int(sel0)
        sel = sel0 - 1
        collections_processor.libhandler.writelog(logfile, f"sel = {sel}")

        product_uuid = product_list[sel]['product_uuid']
        product_name = product_list[sel]['product_name']
        collections_processor.libhandler.writelog(logfile, f"Products: {product_uuid}. {product_name}")

        stored_data = f"{product_uuid}|{product_name}"

        # if self.userdata == "2":
        #     message = "Please enter the Smart Card Number Eg. 32987603837"  # ^0. Go Back"
        #     menu_response = self.core_processor.make_response("more", message)
        #     libhandler.writelog(logfile, f"message = {message}")
        #     # self.core_processor.storeSession(self.msisdn, self.sessionid, self.networkid, f"ENTAMT|{stored_data}")
        #     self.core_processor.storeSession(self.msisdn, self.sessionid, self.networkid, f"COLAMT|{stored_data}")

        # elif self.userdata == "1" or self.userdata == "3":
        message = "Please enter your SmartCard Number Eg: 12344398989"  # ^0. Go Back"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "COLAMT", stored_data)

        # else:
        #     data = ""
        #     menu_response = self.core_processor.thrown_unknown_option(data, goback_message)

    elif last_position == "COLAMT":
        extract =session_processor.get_ussd_extra.get_ussd_extra(pos)
        status = extract
        biller_num = userdata

        stored_data = f"{extract}|{biller_num}"

        message = "Enter amount Eg: 5"  # ^0. Go Back"
        menu_response = core_processor.make_response.make_response(request, "more", message)
        session_processor.store_menupoint.store_menupoint(request, "MDEPAY", stored_data)

    return menu_response

