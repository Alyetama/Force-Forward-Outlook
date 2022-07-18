#!/usr/bin/env python
# coding: utf-8

import asyncio
import zipfile
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from rclone.rclone import Rclone
from watchfiles import awatch

from send import parse_eml, send_email


def zip_sent(file):
    dst = file.parent / 'sent' / file.with_suffix('.zip').name
    with zipfile.ZipFile(dst,
                         mode='w',
                         compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as zf:
        zf.write(file, file.name)
    return dst


async def rclone_sync():
    remote = os.environ['REMOTE_NAME']
    rc = Rclone()
    rc.unit = 'B'
    rc.copy(f'{remote}:emails', f'{remote}:downloaded_emails')
    rc.move(f'{remote}:emails', 'emails')
    await asyncio.sleep(10)


async def main():
    async for changes in awatch('emails'):
        for change in changes:
            logger.debug(change)
            file = Path(change[1])
            if change[0].value != 1 or file.suffix == '.zip' or not file.exists(
            ):
                continue
            parsed_email = parse_eml(file)
            send_email(parsed_email)
            logger.info(f'Sent (from: {parsed_email["from"]}, '
                        f'subject: {parsed_email["subject"]})')
            dst = zip_sent(file)
            file.unlink()


if __name__ == '__main__':
    load_dotenv()
    asyncio.run(rclone_sync())
    asyncio.run(main())
