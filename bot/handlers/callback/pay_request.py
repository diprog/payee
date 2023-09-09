import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

import db
import sheets.worksheets
from bot import router
from bot.callback_data import RequestCompletePayment
from bot.utils import parse_request, SPLITTER, prep_md, delete_message_after_delay
from db.models.requests import RequestStatuses


@router.callback_query(RequestCompletePayment.filter())
async def complete_request_payment(query: CallbackQuery, callback_data: RequestCompletePayment):
    """
    Обрабатывает запрос на завершение оплаты. Обновляет статус запроса,
    форматирует и отправляет сообщение об успешной оплате.

    :param query: объект CallbackQuery, содержащий данные запроса от пользователя
    :type query: aiogram.types.CallbackQuery
    :param callback_data: данные, присланные с запросом
    :type callback_data: RequestCompletePayment
    :return: None
    """
    bot: Bot = Bot.get_current()
    # Получаем запрос на оплату
    request = await db.requests.get(callback_data.request_id)
    # Одобряем запрос (изменяем статус запроса на "одобрен")
    request.status = RequestStatuses.APPROVED
    await request.save()
    # Получаем данные из базы
    data = await db.data.get()
    # Получаем информацию о владельце
    owner = sheets.worksheets.owners.get(request.approving_by_username)
    owner_text = f'{prep_md(owner.name)} \\(@{prep_md(owner.username)}\\)'
    # Получаем информацию о плательщике
    payer = sheets.worksheets.owners.get(name=request.payer_name)
    payer_text = f'{prep_md(payer.name)} \\(@{prep_md(payer.username)}\\)'

    # Редактируем сообщение в чате у согласующих.
    approved_text = f'✅ *Согласовал:* {owner_text}\\.\n\n💵 *Оплатил:* {payer_text}\\.'

    try:
        await bot.edit_message_text(
            f'{parse_request(request)}\n{SPLITTER}\n*💼 От кого \\(юр\\. лицо/счёт\\):* {request.check}\n\n{approved_text}',
            data.group_id,
            request.message_id,
            parse_mode=ParseMode.MARKDOWN_V2)
    except:
        pass

    # Отправляем оповещение тому, кто создал заявку изначально.
    # Если прошло 48 часов с момента создания сообщения, то его нельзя удалить.
    text = f'*Вы отправили запрос на согласование и оплату:*\n{parse_request(request, False)}\n{SPLITTER}\n💼 *От кого \\(юр\\. лицо/счёт\\):* {request.check}\n\n{approved_text}'
    try:
        await bot.delete_message(request.from_id, request.private_message_id)
        await bot.send_message(request.from_id,
                               text,
                               parse_mode=ParseMode.MARKDOWN_V2)
    except TelegramBadRequest as e:
        if "message can't be deleted for everyone" in e.message:
            await bot.edit_message_text(text, request.from_id, request.private_message_id)
            message = await bot.send_message(request.from_id, 'Обновился статус заявки.',
                                             reply_to_message_id=request.private_message_id)
            asyncio.create_task(delete_message_after_delay(message, 86400))

    # Показываем alert об успешной оплате.
    await query.answer('✅ Оплачено.', show_alert=True)

    # Удаляем или редактируем сообщение с кнопкой "Оплачено", чтобы нельзя было сделать это ещё раз.
    try:
        await query.message.delete()
    except TelegramBadRequest as e:
        if "message can't be deleted for everyone" in e.message:
            await query.message.edit_text('✅ Оплачено. Данное сообщение можно удалить.', reply_markup=None)
