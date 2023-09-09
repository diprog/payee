from aiogram.filters import Command
from aiogram.types import Message

from bot import router


@router.message(Command('error'))
async def raise_error(message: Message) -> None:
    raise Exception
