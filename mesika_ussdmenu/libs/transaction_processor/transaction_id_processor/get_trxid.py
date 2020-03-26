import transaction_processor.transaction_id_processor as transaction_id

import string
import random
import secrets

logfile = "num_trxid"
size = 10


def get_trxid(request, type):

    if type == "num":
        # digits
        return f'{transaction_id.bank_code.lower()}' + ''.join(random.choice(chars=string.digits) for _ in range(size))

    elif type == "secret":
        trxid = secrets.token_urlsafe(size)
        trxid = trxid.replace('_', '')
        trxid = trxid.replace('-', '')
        trxid = f"{transaction_id.bank_code.lower()}{trxid}"

        return trxid

    elif type == "alph":
        return f'{transaction_id.bank_code.lower()}'.join(random.choice(string.ascii_letters) for _ in range(size))
