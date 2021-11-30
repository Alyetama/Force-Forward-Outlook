import json
import os
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import cache

from bs4 import BeautifulSoup as bs
from dateparser import parse
from dotenv import load_dotenv
from loguru import logger

from google_drive import Drive


@cache
def send_email(m):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = m['subject']
    msg['From'] = m['from']
    msg['To'] = m['toRecipients']
    msg['Reply-To'] = m['from']
    msg['Body'] = m['body']
    m["Date"] = parse(m['receivedDateTime'],
                      settings={
                          'TIMEZONE': 'UTC',
                          'TO_TIMEZONE': 'EST'
                      })
    soup = bs(msg['Body'], 'html.parser')

    bodytag = soup.find('div')
    bodytag.insert(0, bs(f'<p>Original time: {m["Date"]}</p>', 'html.parser'))
    msg.attach(MIMEText(soup, 'html'))

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(os.environ['FROM_EMAIL'], os.environ['EMAIL_PASSWD'])
    s.sendmail(m['from'], os.environ['TO_EMAIL'], msg.as_string())
    s.quit()


def get_eml_file(drive, folder_id):
    files_list = drive.ListFile({
        'q':
        f"'{folder_id}' in parents and trashed=false"
    }).GetList()
    if files_list:
        for file in files_list:
            try:
                send_email(json.loads(file.GetContentString()))
                file.Delete()
            except Exception as e:
                logger.error(f'{datetime.now()} – {e}')
            logger.info(f'{datetime.now()} – Found a new email!')
    else:
        logger.debug(f'{datetime.now()} – No new emails.')


if __name__ == '__main__':
    load_dotenv()
    logger.add('logs.log')
    drive = Drive().drive()
    while True:
        try:
            get_eml_file(drive, os.environ['FOLDER_ID'])
            time.sleep(5)
            if Path('logs.log').stat().st_size < 1e+7:
                with open('logs.log', 'a+') as f:
                    f.seek(0)
                    f.truncate()
                    f.flush()
        except KeyboardInterrupt:
            logger.debug(f'{datetime.now()} – Interrupted by user.')
            break
