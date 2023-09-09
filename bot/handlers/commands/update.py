from aiogram.filters import Command
from aiogram.types import Message

from bot import router
from bot.utils import is_main_admin
from sheets import sheets


@router.message(Command('update'))
async def command_update_handler(message: Message) -> None:
    """
    Обработчик команды /update для обновления кэша таблиц.

    :param message: Объект Message, содержащий информацию о сообщении
    :type message: Message
    """
    # Проверяем, является ли отправитель команды главным администратором
    if is_main_admin(message.from_user.id):
        # Отправляем сообщение о начале обновления кэша
        reply_message = await message.reply('⌛️ Идет чтение таблиц и обновление кэша. Пожалуйста, подождите...')

        # Выполняем обновление кэша
        await sheets.update()

        # Редактируем сообщение с подтверждением обновления кэша
        await reply_message.edit_text('✅ Кэш был успешно обновлен.')
