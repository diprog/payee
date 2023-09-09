from aiogram.filters import Command
from aiogram.types import Message

import db
from bot import router
from bot.utils import is_main_admin


@router.message(Command('setapprove'))
async def command_setapprove_handler(message: Message) -> None:
    if is_main_admin(message.from_user.id):
        data = await db.data.get()
        data.group_id = message.chat.id
        await data.save()
        await message.reply('✅ Теперь в эту группу будут направляться запросы для согласующих.')
