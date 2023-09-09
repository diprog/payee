from copy import copy

import aiofiles
import jsonpickle

cache = {}


class Pickler:
    """
    Класс Pickler используется для асинхронной сериализации и десериализации данных в JSON формат.

    :param filename: Имя файла для сохранения и чтения данных.
    """

    def __init__(self, filename: str):
        """
        Инициализация объекта класса Pickler.

        :param filename: Имя файла без расширения.
        """
        # Создание пути до файла с использованием переданного имени файла
        self.filepath = f'db/data/{filename}.json'

    async def write(self, obj):
        """
        Асинхронная запись сериализованного объекта в файл.

        :param obj: Объект для сериализации и записи.
        """
        # Открытие файла на запись в асинхронном режиме
        async with aiofiles.open(self.filepath, 'w', encoding='utf-8') as f:
            # Сериализация объекта в JSON и запись в файл
            await f.write(jsonpickle.encode(obj, keys=True))
            cache[self.filepath] = obj

    async def read(self):
        """
        Асинхронное чтение файла и десериализация данных.

        :return: Десериализованный объект или None, если файл не найден.
        """
        try:
            if cache.get(self.filepath):
                return copy(cache[self.filepath])
            # Открытие файла на чтение в асинхронном режиме
            async with aiofiles.open(self.filepath, 'r', encoding='utf-8') as f:
                # Чтение файла и десериализация данных из JSON
                obj = jsonpickle.decode(await f.read(), keys=True)
                cache[self.filepath] = obj
                return copy(obj)
        except FileNotFoundError:
            # В случае отсутствия файла возвращается None
            return None
