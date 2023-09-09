from beanie import Document

from db.models.person import Person


class User(Document):
    # ID Пользователя Telegram
    tg_id: int
    # Юзернейм пользователя Telegram
    tg_username: str
    # Персональные данные пользователя
    person: Person
    # Является ли сотрудником
    is_employee: bool = False
    # Является ли администратором
    is_admin: bool = False
    # Является ли прорабом
    is_foreman: bool = False
