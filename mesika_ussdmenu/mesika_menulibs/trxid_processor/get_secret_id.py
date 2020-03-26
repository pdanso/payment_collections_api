import trxid_processor
import secrets

logfile = "secret_id"


def get_secret_trxid(code=trxid_processor.bank_code.lower(), size=9):
    trxid = secrets.token_urlsafe(size)
    trxid = trxid.replace('_', '')
    trxid = trxid.replace('-', '')
    trxid = f"{code}" % trxid

    return trxid
