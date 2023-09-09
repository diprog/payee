from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

import db
import sheets.worksheets.owners
from bot import router
from bot.callback_data import ApproveRequest
from bot.inline_keyboards import approve_menu
from bot.utils import parse_request, prep_md


@router.callback_query(ApproveRequest.filter())
async def approve_request(query: CallbackQuery, callback_data: ApproveRequest, base_url: str):
    """
    Обработчик callback запроса на согласование заявки.

    :param query: Объект CallbackQuery, содержащий информацию о запросе
    :type query: CallbackQuery
    :param callback_data: Объект ApproveRequest, содержащий данные callback
    :type callback_data: ApproveRequest
    :param base_url: Базовый URL для формирования меню
    :type base_url: str
    """
    # Получаем информацию о пользователе, согласующем запрос
    owner = sheets.worksheets.owners.get(query.from_user.username)

    # Если у пользователя нет роли Согласующего, отвечаем сообщением об ошибке и прерываем функцию
    if not owner:
        await query.answer('У вас нет роли Согласущего.', show_alert=True)
        return

    # Получаем запрос из базы данных
    request = await db.requests.get(callback_data.request_id)

    # Формируем текст сообщения и редактируем текущее сообщение
    try:
        text = parse_request(request)
        await query.message.edit_text(
            text + f'\n\n❗️ *На согласовании* у {prep_md(owner.name)} \\(@{prep_md(owner.username)}\\)\\.\nПодождите, пока он завершит процесс или отменит согласование\\.',
            reply_markup=None,
            parse_mode=ParseMode.MARKDOWN_V2)

        # Отправляем сообщение пользователю с запросом на согласование и меню для выбора действий
        message = await Bot.get_current().send_message(query.from_user.id,
                                                       '*Вы приняли запрос на согласование:*\n\n' + text + '\n\n❔ _Выберите нужный вариант, чтобы  завершить процесс согласования, либо вернуть запрос в стадию выбора согласующего\\._',
                                                       parse_mode=ParseMode.MARKDOWN_V2,
                                                       reply_markup=approve_menu(base_url, request.id))
    # Ошибка в parse_request
    except AttributeError:
        await query.answer('❌ Запрос не найден. Возможно, отсутствует запись в базе данных.', show_alert=True)
        return

    # Обновляем данные запроса в базе данных
    request.approving_by_user_id = query.from_user.id
    request.approving_by_message_id = message.message_id
    request.approving_by_username = owner.username
    await request.save()

    # Отправляем пользователю уведомление о необходимости перейти в
    # личные сообщения с ботом для продолжения согласования
    await query.answer(
        '❕ Вы приняли запрос на согласование и выбора плательщика. Перейдите в личные сообщения с ботом @capremslash_bot, чтобы продолжить',
        show_alert=True)