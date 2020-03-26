#!/bin/env/python
import psycopg2
import sys
import pprint
import os,json,smtplib
from datetime import date, timedelta

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart


def main(providers_reference_number):
    config_file_name = os.path.join(os.path.dirname(__file__), "settings.json")
    with open("/client_configs/non_rfi/stool_lands/uat/payment_collections/settings.json", "r") as f:
        efs = json.load(f)
        db = efs['vodafone_db']['db_name']
        host = efs['vodafone_db']['db_host']
        port = efs['vodafone_db']['db_port']
        user = efs['vodafone_db']['db_user']
        passwd = efs['vodafone_db']['db_password']
    print("Connecting to database\n ")

    # get a connection, if a connect cannot be made an exception will be raised here
    conn = psycopg2.connect(host=host, database=db, user=user, password=passwd, port=port)

    cursor = conn.cursor()
    print("Connected\n")


    query = f"select transaction_status, transaction_description from momo_transactions where providers_reference_number = '{providers_reference_number}'"

    cursor.execute(query)
    record = cursor.fetchone()
    print(record)
    cursor.close()
    conn.close()
    print("Closing connection")

    return record

