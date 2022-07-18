#!/usr/bin/env python
# coding: utf-8

import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import html2text


def parse_eml(eml_file: str) -> str:
    with open(eml_file) as j:
        eml = json.load(j)

    msg = MIMEMultipart('alternative')
    msg.add_header('from', f'{eml["from"]} <{eml["from"]}>')
    msg.add_header('to', os.environ['TO_EMAIL'])
    msg.add_header('reply-to', eml['from'])
    msg.add_header('subject', eml['subject'])

    html = eml['body']
    text = html2text.html2text(eml['body'])
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))
    return msg


def send_email(email_object):
    email_string = email_object.as_string()
    ctx = ssl.create_default_context()
    s = smtplib.SMTP_SSL('smtp.gmail.com', port=465, context=ctx)
    s.login(os.environ['FROM_EMAIL'], os.environ['FROM_EMAIL_PASSWORD'])
    s.sendmail(email_object['from'], os.environ['TO_EMAIL'], email_string)
    s.quit()
