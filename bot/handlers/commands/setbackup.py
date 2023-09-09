from aiogram.filters import Command
from aiogram.types import Message

import db
from bot import router
from bot.utils import is_main_admin


@router.message(Command('setbackup'))
async def command_setbackup_handler(message: Message) -> None:
    if is_main_admin(message.from_user.id):
        data = await db.data.get()
        data.backup_chat_id = message.chat.id
        await data.save()
        await message.reply('✅ Теперь в эту группу каждый день будут загружатся бэкапы.')
