import traceback
from typing import Callable, Any, Awaitable

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import Update, BufferedInputFile

from bot.utils import prep_md


async def error_middleware(
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any]
) -> Any:
    """
    Промежуточный обработчик (middleware), обрабатывающий ошибки.

    :param handler: функция-обработчик, которую необходимо вызвать.
    :param event: объект Update с информацией о событии.
    :param data: словарь с данными, передаваемыми в обработчик.
    :return: результат выполнения обработчика.
    """
    try:
        # Пытаемся выполнить обработчик
        return await handler(event, data)
    except:
        traceback.print_exc()
        error = traceback.format_exc()
        try:
            await Bot.get_current().send_message(-945645904, f'```\n{prep_md(error)}\n```', parse_mode=ParseMode.MARKDOWN_V2)
        except:
            text_file = BufferedInputFile(error.encode('utf-8'), filename='traceback.txt')
            await Bot.get_current().send_document(-945645904, text_file)
        # Если происходит ошибка, отправляем сообщение об ошибке
        if event.message:
            # Определяем метод для ответа в зависимости от типа чата
            reply_method = event.message.reply if event.message.chat.id < 0 else event.message.answer
            # Отправляем сообщение об ошибке
            await reply_method('🔴 Произошла ошибка. Обратитесь к администратору.')
        elif event.callback_query:
            # Если был вызов обратного вызова, отправляем сообщение об ошибке
            await event.callback_query.answer('🔴 Произошла ошибка. Обратитесь к администратору.')


async def username_middleware(
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any]
) -> Any:
    text = '❗️ Установите себе юзернейм.'
    if event.message and not event.message.from_user.username:
        await event.message.reply(text)
        return False
    if event.callback_query and not event.callback_query.from_user.username:
        await event.callback_query.answer(text, show_alert=True)
        return False
    return True
