from aiogram.filters import Command
from aiogram.types import Message

from bot import router


@router.message(Command('id'))
async def command_id(message: Message) -> None:
    text = f'Ваш ID: {message.from_user.id}\nID этого чата: {message.chat.id}'
    await message.answer(text)
