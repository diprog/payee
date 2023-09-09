from typing import Optional

from beanie import Document


class Person(Document):
    # Имя
    first_name: str
    # Фамилия
    last_name: str
    # Отчество
    middle_name: str
    # Серия и номер паспорта человека
    passport: str
    # Комментарий
    comment: Optional[str] = None
