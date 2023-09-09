from aiogram.filters import Command
from aiogram.types import Message

import backup_yearly
from bot import router
from bot.utils import is_main_admin


@router.message(Command('newbackperiod'))
async def command_newbackperiod_handler(message: Message) -> None:
    if is_main_admin(message.from_user.id):
        await message.reply('Сервер будет перезагружен...')
        await backup_yearly.main(force=True)

