import trxid_processor
import string
import random

logfile = "alph_id"
bank_code = ""


def get_alph_trxid(size=10, chars=string.ascii_letters, code=bank_code.lower()):
    return f'{code}'.join(random.choice(chars) for _ in range(size))

