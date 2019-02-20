# coding: utf-8

import os
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64

import logging
from config import SENDER_EMAIL, SENDER_PWD

logger = logging.getLogger(__name__)


def send_notification(new_offers_list, query):

    # Compose attachment
    # part = MIMEBase('application', "octet-stream")
    # part.set_payload(open(excel_file, "rb").read())
    # encode_base64(part)
    # part.add_header('Content-Disposition', "attachment; filename= %s" % os.path.basename(excel_file))

    # Compose message
    msg = MIMEMultipart()
    msg["Subject"] = "Degewo : {} new offers".format(len(new_offers_list))
    msg["From"] = SENDER_EMAIL
    msg["To"] = ",".join(query.receiver)
    msg.attach(MIMEText("\n".join(new_offers_list), "plain"))
    # msg.attach(part)

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(SENDER_EMAIL, SENDER_PWD)
        server.sendmail(SENDER_EMAIL, query.receiver, msg.as_string())
        server.close()
        logging.debug("Email sent!")
    except Exception as e:

        logging.error("Something went wrong...")
        logging.error(e)
