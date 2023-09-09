import logging
from typing import Optional

import gspread_asyncio
from google.oauth2.service_account import Credentials


def get_creds():
    creds = Credentials.from_service_account_file("google.json")
    scoped = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


class User:
    def __init__(self, username: str, name: str, id: Optional[int | str] = None):
        self.username = username
        self.name = name
        self.id = int(id) if id else None

class Object:
    def __init__(self, name: str, username: str):
        self.name = name
        self.username = username
cache = {}


async def get_worksheet(title: str) -> gspread_asyncio.AsyncioGspreadWorksheet:
    """
    Асинхронная функция, которая возвращает лист (worksheet) из Google таблицы по указанному названию.

    :param title: Название листа, который нужно получить.
    :type title: str
    :return: Лист из Google таблицы.
    :rtype: gspread_asyncio.AsyncioGspreadWorksheet
    """
    # Авторизуемся в Google Sheets
    agc = await agcm.authorize()

    # Открываем таблицу с названием 'glossarium'
    ss = await agc.open("glossarium")

    # Получаем список всех листов в этой таблице
    worksheets = await ss.worksheets()

    # Проходимся по всем листам в поисках нужного
    for worksheet in worksheets:
        # Если название текущего листа совпадает с запрошенным, возвращаем этот лист
        if worksheet.title == title:
            return worksheet


async def update():
    """
    Эта асинхронная функция обновляет данные в локальном кэше из указанных листов Google таблицы.

    Ключи для кэша: 'users', 'owners', 'objects', 'check'.

    :return: None
    """
    # Выводим информационное сообщение о начале загрузки данных из таблицы
    logging.info('Загрузка таблицы...')

    # Получаем лист 'users' из Google таблицы и загружаем данные в кэш
    worksheet = await get_worksheet('users')
    usernames = await worksheet.col_values(1)
    names = await worksheet.col_values(2)
    users = []
    for i in range(0, len(usernames)):
        users.append(User(usernames[i], names[i]))
    cache['users'] = users

    # Получаем лист 'owners' из Google таблицы и загружаем данные в кэш
    worksheet = await get_worksheet('owner')
    usernames = await worksheet.col_values(1)
    names = await worksheet.col_values(2)
    ids = await worksheet.col_values(3)
    users = []
    for i in range(0, len(usernames)):
        users.append(User(usernames[i], names[i], ids[i]))
    cache['owners'] = users

    # Получаем лист 'objects' из Google таблицы и загружаем данные в кэш
    worksheet = await get_worksheet('object')
    names = await worksheet.col_values(1)
    usernames = await worksheet.col_values(2)
    try:
        cache['objects'] = [Object(names[i], usernames[i]) for i in range(0, len(names))]
    except IndexError:
        cache['objects'] = names

    # Получаем лист 'check' из Google таблицы и загружаем данные в кэш
    worksheet = await get_worksheet('check')
    cache['check'] = await worksheet.col_values(1)

    # Выводим информационное сообщение о завершении загрузки данных из таблицы
    logging.info('Таблица загружена.')


def get_from_cache(key):
    return cache[key]
