#!/usr/bin/env python
# coding: utf-8

import asyncio
import json
import os
import signal
import smtplib
import ssl
import sys
import zipfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from glob import glob
from pathlib import Path

import html2text
from dotenv import load_dotenv
from loguru import logger
from rclone.rclone import Rclone
from watchfiles import awatch


def keyboard_interrupt_handler(sig, _):
    logger.warning(f'\nKeyboardInterrupt (id: {sig}) has been caught...')
    logger.warning('Terminating the session gracefully...')
    sys.exit(1)


def parse_eml(eml_file):
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


def zip_email(file):
    dst = file.parent / 'sent' / file.with_suffix('.zip').name
    with zipfile.ZipFile(dst,
                         mode='w',
                         compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as zf:
        zf.write(file, file.name)
    return dst


def process_email(file):
    parsed_email = parse_eml(file)
    send_email(parsed_email)
    logger.info(f'Sent (from: {parsed_email["from"]}, '
                f'subject: {parsed_email["subject"]})')
    dst = zip_email(file)
    file.unlink()


def init_checks():
    env = ['FROM_EMAIL', 'FROM_EMAIL_PASSWORD', 'TO_EMAIL', 'REMOTE_NAME']
    if not all(os.getenv(x) for x in env):
        raise AssertionError('Missing a required environment variable!')

    Path('emails/sent').mkdir(exist_ok=True, parents=True)

    pending_emails = [Path(x) for x in glob('emails/*') if not Path(x).is_dir()]
    for file in pending_emails:
        process_email(file)


async def sync_emails():
    while True:
        remote = os.environ['REMOTE_NAME']
        rc = Rclone()
        rc.unit = 'B'
        rc.copy(f'{remote}:emails', f'{remote}:downloaded_emails')
        rc.move(f'{remote}:emails', 'emails')
        await asyncio.sleep(10)


async def watch_emails():
    async for changes in awatch('emails'):
        for change in changes:
            logger.debug(change)
            file = Path(change[1])
            if change[0].value != 1 or file.suffix == '.zip' or not file.exists(
            ):
                continue
            process_email(file)


async def main():
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    logger.add('logs.log')
    load_dotenv()
    init_checks()
    await asyncio.gather(sync_emails(), watch_emails())


if __name__ == '__main__':
    asyncio.run(main())
