import asyncio

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

import constants

bot = Bot(constants.TELEGRAM_BOT_TOKEN)

from jsonpickle import Pickler, Unpickler


async def main():
    try:
        await bot.send_message(45345345, 'message')
    except TelegramBadRequest as e:
        a = Pickler().flatten(e)
        print(a)
        print(Unpickler().restore(a))



asyncio.run(main())
