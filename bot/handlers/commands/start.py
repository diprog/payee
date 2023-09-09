from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message

import sheets.worksheets
from bot import router
from bot.inline_keyboards import user_request


@router.message(Command('start'))
async def command_start_handler(message: Message, base_url: str) -> None:
    user = sheets.worksheets.users.get(message.from_user.username)
    if user:
        await message.reply(f'Здравствуйте, {user.name}.\n\nЧтобы отправить запрос на согласование и оплату, заполните форму и нажмите кнопку «Отправить».'.replace('..', '.'),
                            reply_markup=user_request(base_url))
    else:
        await message.reply('❌ Нет доступа.')
