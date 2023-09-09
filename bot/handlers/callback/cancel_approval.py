from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

import db
from bot import router
from bot.callback_data import ApproveRequest, CancelApproval
from bot.inline_keyboards import request_menu
from bot.utils import parse_request
from db.models.requests import RequestStatuses


@router.callback_query(CancelApproval.filter())
async def cancel_approving_request(query: CallbackQuery, callback_data: ApproveRequest):
    """
    Обработчик callback запроса на отмену согласования заявки.

    :param query: Объект CallbackQuery, содержащий информацию о запросе
    :type query: CallbackQuery
    :param callback_data: Объект ApproveRequest, содержащий данные callback
    :type callback_data: ApproveRequest
    """
    # Получаем запрос из базы данных
    request = await db.requests.get(callback_data.request_id)
    request.status = RequestStatuses.ON_APPROVAL
    await request.save()
    data = await db.data.get()

    # Редактируем сообщение с запросом в группе, возвращая его в исходное состояние
    await Bot.get_current().edit_message_text(
        parse_request(request),
        data.group_id,
        request.message_id,
        reply_markup=request_menu(request.id),
        parse_mode=ParseMode.MARKDOWN_V2)

    # Отвечаем на callback запрос уведомлением
    await query.answer('✅ Запрос передан обратно в группу.', show_alert=True)

    # Удаляем текущее сообщение с запросом
    await query.message.delete()
