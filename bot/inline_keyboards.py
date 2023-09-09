from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

import sheets.worksheets.users
from bot import callback_data


def InlineKeyboard(*rows):
    return InlineKeyboardMarkup(inline_keyboard=rows)


def InlineButton(text, callback=None, web_app_url=None):
    if callback:
        return InlineKeyboardButton(text=text, callback_data=callback.pack())
    elif web_app_url:
        return InlineKeyboardButton(text=text, web_app=WebAppInfo(url=web_app_url))
    else:
        return InlineKeyboardButton(text=text, callback_data='none')


def request_menu(request_id):
    return InlineKeyboard(
        [
            InlineButton('📋 Начать согласование', callback_data.ApproveRequest(request_id=request_id))
        ]
    )


def approve_menu(base_url, request_id):
    return InlineKeyboard(
        [
            InlineButton('✅ Согласовать', web_app_url=f'{base_url}/approve_request?request_id={request_id}')
        ],
        [
            InlineButton('🚫 Отклонить', web_app_url=f'{base_url}/decline_request?request_id={request_id}')
        ],
        [
            InlineButton('❌ Отменить согласование', callback_data.CancelApproval(request_id=request_id)),
        ]
    )


def user_request(base_url, request_id: str = None):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineButton(
                    "📝 Открыть форму", web_app_url=f"{base_url}/request"
                ) if not request_id else InlineButton(
                    "📝 Редактировать", web_app_url=f"{base_url}/request?request_id={request_id}"
                )
            ]
        ]
    )


def generate_journal_menu(names: Optional[list[str]] = None):
    buttons = []
    users = sheets.worksheets.users.get()
    for user in users:
        text = user.name
        if names and user.name in names:
            text = '✅ ' + text
        buttons.append([InlineButton(text, callback_data.GenerateJournalSelectUser(username=user.username))])
    buttons.insert(0, [InlineButton('🫂 По всем', callback_data.GenerateJournalSelectUser(username='all'))])
    buttons.append([InlineButton('🪄 Сформировать', callback_data.GenerateJournal())])
    return InlineKeyboard(*buttons)


def pay_keyboard(request_id: str):
    return InlineKeyboard(
        [
            InlineButton('✅ Оплачено', callback_data.RequestCompletePayment(request_id=request_id)),
            InlineButton('❌ Отклонить', callback_data.CancelApproval(request_id=request_id)),
        ]
    )
