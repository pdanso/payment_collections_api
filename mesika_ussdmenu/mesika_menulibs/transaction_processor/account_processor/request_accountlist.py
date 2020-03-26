import transaction_processor.account_processor as trans_account
import core_processor
import session_processor

logfile = "request_accountlist"


def request_account(bank_id, url, service_id, data, next_position, goback_message, modul):
    message = ""
    account_results = ""

    payload = {"msisdn": trans_account.msisdn}
    trans_account.libhandler.writelog(logfile, f"Payload:{payload}")
    response = self.core_processor.call_api(url, payload, module, "getAccountlist")

    status = response['status']
    account_result = {}

    try:
        status = 200
        if status == 200:

            acc_counts = len(response['accounts'])
            acc_count = int(acc_counts)
            account_list = response['accounts']
            trans_account.libhandler.writelog(logfile, f"Resp: {account_list}")

            account_results = {'status': 200, 'count': acc_count, 'account_list': account_list}

            account_c = self.get_account_list(self.BANK_ID, self.MSISDN)

            if account_c['total_accounts'] == 1:
                # SET ACCOUNT
                exist_data = self.ussdhelper.get_ussd_extra(pos)
                nxt_pos = "accts:%s|acct_selected:1|acctcount:%s|network_selected:%s|%s" % (
                    (account_c['accounts']).rstrip('\n'),
                    account_c['total_accounts'],
                    network,
                    exist_data)

                # self.ussdhelper.storeSession(self.MSISDN,self.SESSION_ID, self.NETWORK_ID,nxt_pos)
                LIBHANDLER.writelog(LOG_FILE_NAME,
                                    "{airtime} storing NXT_POS=> %s" % str(nxt_pos))

                self.store_ussd_menu_point("AIRDST", nxt_pos)
                msg = "Please enter the amount eg. 5"
                menu_response = self.make_response("MORE", msg)





            # if acc_count == 1:
            #     source_account =account_list[0]['account_number']
            #     stored_data = f"{acc_count}|{data}:{source_account}"
            #
            #     self.core_processor.storeSession(self.msisdn, self.sessionid, self.networkid,
            #                                  f"{next_position}|{data}")
            #     libhandler.writelog(logfile, f"Next:{next_position}")
            #     menu_response = ""
            #     return menu_response

            # if acc_count >= 1:
            #     count = 0
            #     for n in response['accounts']:
            #         acct_id = n['id']
            #         source_account = n['account_number']
            #         count += 1
            #         message += str(count) + '. ' + str(source_account)
            #
            #     str_conv = json.dumps(response['accounts'])
            #     stored_data = f"{acc_count}|{str_conv}-{data}"
            #     libhandler.writelog(logfile, f"stored_data: {stored_data} and Count: {count}")
            #
            #     message = f"Please select an account number for this transaction^{message}" #^0. Go back"
            #     menu_response = self.core_processor.make_response("more", message)
            #     self.core_processor.storeSession(self.msisdn, self.sessionid, self.networkid,
            #                                  f"{next_position}|{stored_data}")
            #     libhandler.writelog(logfile, f"Message: {message}")
            #
            # else:
            #     message = "Account numbers cannot be displayed right now. Please try again later"
            #     menu_response = self.core_processor.goto_start(message, data, goback_message)
            #     libhandler.writelog(logfile, f"Message: {message}")

        else:
            account_results = {"status": 400, "message": "Account Numbers cannot be displayed right now. Please "
                                                         "try again later"}


            # message = "Account numbers cannot be displayed right now. Please try again later"
            # menu_response = self.core_processor.goto_start(message, data, goback_message)
            # libhandler.writelog(logfile, f"Message: {message}")
            # return menu_response

    except:
        libhandler.log_error_detailed(logfile, "NOT WORKING")

    return account_results