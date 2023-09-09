import asyncio
import glob
import os
import shutil
import time
from datetime import datetime

from aiogram import Bot

import constants
import db

bot = Bot(constants.TELEGRAM_BOT_TOKEN)


def move_xlsx_files(force=False):
    path = '.journals'
    # Создаем новую директорию, если она еще не существуетX
    filename = f'.journals_end_{datetime.now().strftime("%d-%m-%Y")}_{int(time.time())}' if force else f'.journals_end_{datetime.now().year - 1}'
    new_dir = os.path.join(path, filename)
    os.makedirs(new_dir, exist_ok=True)

    # Перебираем все файлы .xlsx в указанной директории
    for filename in glob.glob(os.path.join(path, '*.xlsx')):
        # Перемещаем каждый файл .xlsx в новую директорию
        shutil.move(filename, new_dir)


async def main(force=False):
    move_xlsx_files(force)
    data = await db.data.get()
    await bot.send_message(data.backup_chat_id, f'📄 Архив журналов до {datetime.now().strftime("%d-%m-%Y")}')
    os.remove('db/data/requests.json')
    os.system('reboot')


if __name__ == '__main__':
    asyncio.run(main())
