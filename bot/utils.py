import asyncio

from aiogram.types import Message

import constants
import sheets.worksheets
from db.models.requests import Request


def is_main_admin(user_id: int):
    return user_id in (constants.DEVELOPER_ID, *constants.MAIN_ADMIN_ID)


async def delete_message_after_delay(message: Message, seconds: int):
    await asyncio.sleep(seconds)
    await message.delete()


def prep_md(string: str) -> str:
    """
    Подготовка строки к обработке с использованием Markdown.

    В Markdown некоторые символы имеют специальное значение, например, символы форматирования текста.
    Эта функция "экранирует" такие символы в переданной строке, добавляя перед ними символ обратного слэша.
    Это предотвращает интерпретацию этих символов как специальных символов Markdown.

    :param string: Исходная строка, которую следует подготовить.
    :return: Подготовленная строка.
    """

    # Определение символов, которые необходимо экранировать с помощью предшествующего '\'
    escape_chars = '_*[]()~`>#-|=+{}.!\\'

    # Определение символов, которые необходимо экранировать в определенных контекстах
    pre_code_escape_chars = '`\\'
    link_emoji_escape_chars = ')\\'

    # Определение символа, который следует использовать вместо неоднозначных сущностей курсива и подчеркивания
    ambiguity_char = '\r'

    # Экранирование всех необходимых символов с помощью предшествующего '\'
    escaped_string = ''
    i = 0
    while i < len(string):
        char = string[i]
        if char == '\\':
            # Экранирование символа с помощью предшествующего '\'
            next_char = string[i + 1] if i + 1 < len(string) else ''
            if next_char in (escape_chars + pre_code_escape_chars + link_emoji_escape_chars):
                escaped_string += next_char
                i += 1
            else:
                escaped_string += char
        elif char in escape_chars:
            # Экранирование символа с помощью предшествующего '\'
            escaped_string += '\\' + char
        elif char == '`':
            # Проверка нахождения внутри блока кода, и при необходимости экранирование
            if '`' in escaped_string[-3:] or '`' in string[i + 1:i + 4]:
                escaped_string += '\\' + char
            else:
                escaped_string += char
        elif char == '(':
            # Проверка нахождения внутри определения ссылки или emoji, и при необходимости экранирование ')' и '\'
            if '[' in escaped_string[-3:] and ']' not in escaped_string[-3:]:
                j = i + 1
                while j < len(string):
                    if string[j] == ']':
                        break
                    elif string[j] == ')':
                        escaped_string += '\\' + string[j]
                        i = j
                        break
                    elif string[j] == '\\':
                        escaped_string += '\\' + string[j]
                        j += 1
                    else:
                        escaped_string += string[j]
                        j += 1
                else:
                    escaped_string += char
            else:
                escaped_string += char
        elif char == '_':
            # Проверка на наличие неоднозначной сущности курсива или подчеркивания,
            # и добавление символа неоднозначности при необходимости
            if '_' in escaped_string[-3:] or '_' in string[i + 1:i + 4]:
                escaped_string += ambiguity_char
            else:
                escaped_string += char
        else:
            escaped_string += char
        i += 1

    return escaped_string


def parse_request(request: Request, include_sender=True, edited_request=None) -> str:
    """
    Форматирует информацию о запросе в текстовую строку.

    :param request: Объект запроса, который необходимо отформатировать.
    :param include_sender: Флаг, определяющий, следует ли включать информацию об отправителе в отформатированный текст.
    :param edited_request: Объект отредактированного запроса, если он есть.
    :return: Строка с отформатированной информацией о запросе.
    """
    # Получаем информацию о сотруднике из листа Google Sheets
    employee = sheets.worksheets.users.get(request.from_username)

    # Формируем текстовую строку с информацией о сотруднике
    employee_text = f'{prep_md(employee.name)} \\(@{prep_md(employee.username)}\\)'

    # Если запрос был отправлен, то формируем соответствующую строку
    sender = f'{employee_text} отправил запрос на согласование и оплату\\.'

    # Формируем строки с информацией о запросе
    object = f'🏠 *Объект:* {prep_md(request.object)}'
    counterparty = f'👤 *Контрагент:* {prep_md(request.counterparty)}'
    money = f'🧾 *Сумма:* {prep_md(request.money)}'
    comment = f'📝 *Примечание:* {prep_md(request.comment)}'

    # Если запрос был отредактирован, то формируем соответствующие строки с информацией о изменениях
    if edited_request:
        sender = f'{employee_text} отредактировал запрос\\.'
        if request.object != edited_request.object:
            object += f' *\\=\\>* {prep_md(edited_request.object)}'
        if request.counterparty != edited_request.counterparty:
            counterparty += f' *\\=\\>* {prep_md(edited_request.counterparty)}'
        if request.money != edited_request.money:
            money += f' *\\=\\>* {prep_md(edited_request.money)}'
        if request.comment != edited_request.comment:
            comment += f' *\\=\\>* {prep_md(edited_request.comment)}'

    # Если не нужно включать информацию об отправителе, то удаляем соответствующую строку
    if not include_sender:
        sender = ''

    # Возвращаем сформированный текст
    return f'{sender}\n\n{object}\n\n{counterparty}\n\n{money}\n\n{comment}'


SPLITTER = prep_md('\n─────────────')
