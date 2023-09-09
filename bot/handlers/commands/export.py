import aiofiles.os
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.types import FSInputFile, Message

import db
import excel
import sheets.worksheets
import sheets.worksheets.owners
from bot import router
from bot.callback_data import GenerateJournalSelectUser, GenerateJournal
from bot.inline_keyboards import generate_journal_menu
from db.models.requests import RequestStatuses
from sheets.sheets import User

FIRST_MESSAGE = 'Выберите, по каким сотрудникам сформировать журнал, и затем нажмите на кнопку "🪄 *Сформировать*".\n\nНажмите на кнопку "🫂 *По всем*", чтобы сформировать журналы по всем сотрудникам.'
SPLITTER = '\n\nВыбранные сотрудники:\n'


async def generate_journal(message: Message, user: User):
    """
    Генерирует журнал по согласованным запросам сотрудника.

    :param message: объект Message, на которое будут отправляться ответы в виде документов
    :param user: объект User, содержащий информацию о пользователе
    :return: None
    """
    # Инициализация списка запросов
    requests: list[db.requests.Request] = []

    # Получение всех запросов и фильтрация по имени пользователя и статусу "Согласовано"
    for request in await db.requests.get():
        if request.from_username == user.username and request.status == RequestStatuses.APPROVED:
            requests.append(request)

    # Если нет запросов, выводится сообщение об отсутствии записей
    if not requests:
        await message.answer(f'Не найдено записей для сотрудника {user.name}.')
        return

    filepath = excel.generate_journal(requests)

    # Отправка файла Excel в качестве документа
    file = FSInputFile(filepath, filename=f"Журнал ({user.name}).xlsx")
    await message.answer_document(file, caption=f'*Записей:* {len(requests)}')

    # Удаляем таблицу с диска.
    await aiofiles.os.remove(filepath)


def get_names_from_message(message):
    """
    Извлекает имена пользователей из сообщения.

    :param message: объект Message, содержащий информацию о сообщении
    :return: список имен пользователей
    """
    # Инициализация списка имен
    names = []

    # Если строк больше одной, извлекаются имена пользователей
    if SPLITTER in message.text:
        names = message.text.split(SPLITTER)[-1].split('\n')

    return names


@router.message(Command('export'))
async def command_export_handler(message: Message) -> None:
    """
    Обрабатывает команду /export, запускающую процесс экспорта данных.

    :param message: объект Message, содержащий информацию о сообщении
    :return: None
    """
    # Если пользователь является согласующим, отправляется сообщение с меню формирования журнала
    if sheets.worksheets.owners.get(message.from_user.username):
        await message.reply(FIRST_MESSAGE, reply_markup=generate_journal_menu())
    # Если пользователь не является согласующим, но является сотрудником,
    # запускается формирование журнала этого сотрудника
    elif user := sheets.worksheets.users.get(message.from_user.username):
        await generate_journal(message, user)
    else:
        await message.reply('❌ Нет доступа.')


@router.callback_query(GenerateJournalSelectUser.filter())
async def generate_journal_select_user(query: CallbackQuery, callback_data: GenerateJournalSelectUser):
    """
    Обрабатывает callback-запросы, связанные с выбором пользователей для формирования журнала.

    :param query: объект CallbackQuery, содержащий информацию о callback-запросе
    :param callback_data: объект GenerateJournalSelectUser, содержащий данные callback-запроса
    :return: None
    """
    # Получение информации о текущем пользователе-согласующем
    owner = sheets.worksheets.owners.get(query.from_user.username)

    # Если пользователь не является согласующим, выводится сообщение об ошибке
    if not owner:
        await query.answer('❌ У вас нет роли Согласущего.', show_alert=True)
        return

    # Если выбрана опция "all", формируются журналы для всех пользователей
    if callback_data.username == 'all':
        await query.message.edit_text('⏳ Подождите, пока сформируются все журналы...')
        for user in sheets.worksheets.users.get():
            await generate_journal(query.message, user)
        await query.message.delete()
        return

    # Извлечение имен пользователей из сообщения
    names = get_names_from_message(query.message)

    # Получение информации о выбранном пользователе
    user = sheets.worksheets.users.get(callback_data.username)

    # Если имя выбранного пользователя уже есть в списке, оно удаляется
    # В противном случае, имя добавляется в список
    if user.name in names:
        names.remove(user.name)
    else:
        names.append(user.name)

    # Обновление текста сообщения в соответствии с текущим списком выбранных пользователей
    if names:
        await query.message.edit_text(
            f'Нажмите кнопку "Сформировать", как будете готовы.{SPLITTER}' + '\n'.join(names),
            reply_markup=generate_journal_menu(names))
    else:
        await query.message.edit_text(
            FIRST_MESSAGE,
            reply_markup=generate_journal_menu())


@router.callback_query(GenerateJournal.filter())
async def generate_journal_callback(query: CallbackQuery):
    """
    Обрабатывает callback-запросы на формирование журнала.

    :param query: объект CallbackQuery, содержащий информацию о callback-запросе
    :return: None
    """
    # Получение информации о текущем пользователе-согласующем
    owner = sheets.worksheets.owners.get(query.from_user.username)

    # Если пользователь не является согласующим, выводится сообщение об ошибке
    if not owner:
        await query.answer('У вас нет роли Согласущего.', show_alert=True)
        return

    # Извлечение имен пользователей из сообщения
    names = get_names_from_message(query.message)
    print(names)
    if not names:
        await query.answer('❕ Сначала выберите сотрудников, по которым требуется сформировать журналы.',
                           show_alert=True)
        return

    # Показ сообщения о начале формирования журналов
    await query.message.edit_text('⏳ Подождите, пока сформируются все журналы...')

    # Перебор всех пользователей
    for user in sheets.worksheets.users.get():
        # Если имя пользователя есть в списке выбранных, формируется журнал
        if user.name in names:
            await generate_journal(query.message, user)

    # После завершения формирования всех журналов сообщение удаляется
    await query.message.delete()
