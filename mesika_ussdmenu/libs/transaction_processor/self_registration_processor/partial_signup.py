import transaction_processor.self_registration_processor
import core_processor
import session_processor
import api_processor


def self_signup(self, bank_id, url, answer, last_position, pos, goback_message, module):
    iterate = 0  # for self sign-up

    extract = self.core_processor.get_ussd_extra(pos)
    libhandler.writelog(logfile, f"Extract: {extract}")

    signup_responses = {}

    if last_position == "REGSTR":  # registering for mobile banking

        if answer == "1":
            payload = {}
            response = self.core_processor.call_api(url, payload, module, "getQuestions")
            libhandler.writelog(logfile, f"Api call: {response}")
            status = response['status']

            """to be removed"""
            status = 200
            if status == 200:  """ signup questions available """
            message = ""
            message = "Please answer the question below to sign up:^^"
            question_list = response['questions']
            libhandler.writelog(logfile, f"List: {question_list}")

            str_conv = json.dumps(question_list)
            """ get length of questions to iterate through """
            answers = []

            length = len(question_list)
            fin_length = length - 1
            libhandler.writelog(logfile, f"Length: {fin_length}")

            """ if number of questions is greater than count, display the question with its id """

            if fin_length >= iterate:
                message += str(question_list[iterate]['id']) + '. ' + str(
                    question_list[iterate]['question'])
                menu_response = self.core_processor.make_response("more", message)
                iterate += 1
                stored_data = f"{iterate}*{str_conv}*{answers}"
                self.core_processor.storeSession(self.msisdn, self.sessionid, self.networkid,
                                                 f"REGSTR|{stored_data}")
                libhandler.writelog(logfile, f"Message: {message}")

            else:
                data = ""
                menu_response = self.core_processor.throw_unknown_option(data, goback_message)

        else:
            message = "Sign up questions cannot be displayed right now. Please try again later"
            menu_response = self.core_processor.make_response("end", message)
            libhandler.writelog(logfile, f"Message: {message}")

    elif answer == "2":
        message = "Sign up cancelled"
        menu_response = self.core_processor.make_response("end", message)
        libhandler.writelog(logfile, f"Message: {message}")

    else:
        extract_reply = extract.split('*')
        libhandler.writelog(logfile, f"Reply: {extract_reply}")
        iterate = extract_reply[0]
        questions = extract_reply[1]
        answer_extract = extract_reply[2]

        iterate = int(iterate)
        question_list = json.loads(questions)
        answers = json.loads(answer_extract)

        signup_responses['id'] = question_list[iterate - 1]['id']
        signup_responses['answer'] = answer
        answers.append(signup_responses)
        libhandler.writelog(logfile, f"Answers: {answers}")

        str_conv = json.dumps(question_list)
        str_conv2 = json.dumps(answers)

        length = len(question_list)
        fin_length = length - 1
        libhandler.writelog(logfile, f"Length: {fin_length}")
        message = ""
        message = "Please answer the question below to sign up:^^"

        if fin_length >= iterate:
            message += str(question_list[iterate]['id']) + '. ' + str(
                question_list[iterate]['question'])
            menu_response = self.core_processor.make_response("more", message)
            iterate += 1
            stored_data = f"{iterate}*{str_conv}*{str_conv2}"
            self.core_processor.storeSession(self.msisdn, self.sessionid, self.networkid,
                                             f"REGSTR|{stored_data}")
            libhandler.writelog(logfile, f"Message: {message}")

        else:
            answers.append(signup_responses)
            libhandler.writelog(logfile, f"Answers: {answers}")
            payload = answers
            libhandler.writelog(logfile, f"Signup payload: {payload}")

            response = self.core_processor.call_api(url, payload, "cowrybank", "signup_answers")

            status = response['status']

            if status == 200:
                message = "Your signup request has been received.^You will receive your one-time " \
                          "pin after approval.^Thank you"
                menu_response = self.core_processor.make_response("end", message)
                libhandler.writelog(logfile, f"Message: {message}")

            else:
                message = "Your mobile banking signup request failed. Please try again later"
                menu_response = self.core_processor.make_response("end", message)
                libhandler.writelog("custuat_menu", f"Message: {message}")
    return menu_response