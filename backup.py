import asyncio
import os
import time
from datetime import datetime
from zipfile import ZipFile

from aiogram import Bot
from aiogram.types import FSInputFile

import constants
import db
from db.models.requests import RequestStatuses

BACKUP_FILEPATH = f'.temp/backup.zip'

bot = Bot(constants.TELEGRAM_BOT_TOKEN)


async def get_approved_requests_count():
    approved_requests_count = 0
    for request in await db.requests.get():
        if request.status == RequestStatuses.APPROVED:
            approved_requests_count += 1
    return approved_requests_count


def create_zip():
    with ZipFile(BACKUP_FILEPATH, 'w') as zip_object:
        # Adding files that need to be zipped
        zip_object.write('db/data/requests.json')
        for folder_name, sub_folders, file_names in os.walk('.journals'):
            for filename in file_names:
                # Create filepath of files in directory
                file_path = os.path.join(folder_name, filename)
                # Add files to zip file
                zip_object.write(file_path)


async def main(force=False):
    cache_file = '.cache'
    approved_requests_count = 0
    try:
        with open(cache_file, 'r') as f:
            approved_requests_count = int(f.read())
    except FileNotFoundError:
        pass
    except ValueError:
        pass

    if approved_requests_count == await get_approved_requests_count() and not force:
        return
    else:
        with open(cache_file, 'w') as f:
            f.write(str(await get_approved_requests_count()))

    create_zip()
    data = await db.data.get()
    file = FSInputFile(BACKUP_FILEPATH, filename=f'backup_{int(time.time())}.zip')
    caption = datetime.now().strftime('%d-%m-%Y')
    if force:
        caption += '\n\nЭто ручной бэкап'
    await bot.send_document(data.backup_chat_id, file, caption=caption)
    os.remove(BACKUP_FILEPATH)


if __name__ == '__main__':
    asyncio.run(main())
