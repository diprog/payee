from aiogram.filters import Command
from aiogram.types import Message

import backup
from bot import router
from bot.utils import is_main_admin


@router.message(Command('backup'))
async def command_backup_handler(message: Message) -> None:
    if is_main_admin(message.from_user.id):
        await backup.main(force=True)
        await message.reply('✅ Бэкап успешно создан и отправлен в установленную для бэкапов группу.')
