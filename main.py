import asyncio
import logging
from pathlib import Path

import beanie
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
from aiohttp.web import _run_app
from aiohttp.web_app import Application
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

import constants
import db
import imports
from bot import router
from bot.middlewares import error_middleware, username_middleware
from bot.webapp.router import routes
from sheets import sheets
from utils import get_classes_in_folder

# Установка настроек логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(module)s %(funcName)s ~~~~ %(message)s')

# Создание объекта диспетчера
dp = Dispatcher()

# Создание объекта бота
bot = Bot(constants.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)


# Добавление промежуточного обработчика для обработки исключений
@dp.update.outer_middleware()
async def _(*args, **kwargs):
    if await username_middleware(*args, **kwargs):
        return await error_middleware(*args, **kwargs)


async def on_startup(bot: Bot, base_url: str, dispatcher: Dispatcher):
    """
    Обработчик события запуска бота.
    """
    await bot.delete_webhook()
    asyncio.create_task(dispatcher.start_polling(bot, base_url=base_url))


async def main() -> None:
    """
    Основная функция скрипта.
    """
    await db.engine.init()
    # Запись в кэш данных из управляющей таблицы glossarium
    await sheets.update()

    # Импортирование обработчиков команд и обратных вызовов
    imports.import_all('bot.handlers')
    imports.import_all('bot.handlers.commands')
    imports.import_all('bot.handlers.callback')

    dp["base_url"] = 'https://webapp.capremslash.ru'
    dp.startup.register(on_startup)
    dp.include_router(router)

    # Создание объекта веб-приложения
    app = Application()
    app["bot"] = bot
    app['base_url'] = dp["base_url"]

    # Добавление статических маршрутов и обработчиков в веб-приложение
    app.add_routes([
        web.static('/css', Path(__file__).parent.resolve() / 'bot/webapp/html/css'),
        web.static('/xfTXuw7jP6QXaEhM5WTn', Path(__file__).parent.resolve() / '.journals', show_index=True)
    ])

    app.add_routes(routes)
    setup_application(app, dp, bot=bot)

    # Запуск приложения
    # ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain('/etc/letsencrypt/live/webapp.capremslash.ru/fullchain.pem',
    #                             '/etc/letsencrypt/live/webapp.capremslash.ru/privkey.pem')
    await _run_app(app, host="0.0.0.0", port=80)


if __name__ == "__main__":
    asyncio.run(main())
