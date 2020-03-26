import trxid_processor
import string
import random

logfile = "num_trxid"


def get_num_trxid(size=10, chars=string.digits, code=trxid_processor.bank_code.lower()):
    # digits
    return f'{code}' + ''.join(random.choice(chars) for _ in range(size))
