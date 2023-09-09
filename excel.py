from datetime import datetime
from random import random
from typing import Optional

import xlsxwriter

import sheets.worksheets
from db.models.requests import Request


def generate_journal(requests: list[Request], filepath: Optional[str] = None):
    """
    Функция для создания журнала в формате Excel по списку запросов.

    :param requests: список запросов
    :type requests: list[Request]
    :param filepath: путь, куда следует сохранить файл Excel
    :type filepath: Optional[str]
    :return: путь к созданному файлу Excel
    :rtype: str
    """
    # Если путь к файлу не предоставлен, создаем случайное имя файла в директории .temp
    filepath = filepath or f'.temp/{str(random())[2:]}.xlsx'

    # Формирование строк для записи в соответствии с техническим заданием
    rows = []
    for request in requests:
        # Извлекаем информацию об одобрившем запрос
        owner = sheets.worksheets.owners.get(request.approving_by_username)
        name = owner.name if owner else 'Не найден'
        try:
            payer_name = request.payer_name
        except:
            payer_name = 'ОШИБКА'
        date = datetime.fromtimestamp(request.last_edit_ts)
        row = [date, request.object, request.counterparty, float(request.money), request.check, request.comment,
               name, payer_name]
        rows.append(row)

    # Создание книги Excel и листа в ней
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet()

    # Создание форматов ячеек для заголовков
    green = workbook.add_format()
    green.set_bold()
    green.set_font_color('green')

    red = workbook.add_format()
    red.set_bold()
    red.set_font_color('red')

    # Запись заголовков в лист Excel
    for i, col in enumerate(
            ['Дата', 'Объект', 'Контрагент', 'Сумма', 'От кого (юр. лицо, счет)', 'Примечание', 'Кем согласовано', 'Кем оплачено']):
        worksheet.write(0, i, col, green if i in (4, 6, 7) else red)

    # Запись данных в лист Excel
    date_format = workbook.add_format({'num_format': 'dd.mm.yyyy'})
    for i, row in enumerate(rows):
        for j, col in enumerate(row):
            if j == 0:  # Дата
                worksheet.write_datetime(i + 1, j, col, date_format)
            elif j == 3:  # Сумма (числовое значение)
                worksheet.write_number(i + 1, j, col)
            else:  # Все остальные данные
                worksheet.write(i + 1, j, col)
    worksheet.autofilter(0, 0, len(rows) - 1, len(rows[0]) - 1)

    # Автоматический подбор размера столбцов
    worksheet.autofit()

    # Закрытие книги Excel
    workbook.close()

    return workbook.filename
