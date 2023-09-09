from datetime import datetime

from beanie import Document, Link
from pydantic import BaseModel

from db.models.user import User


class Job(BaseModel):
    # Название работ
    name: str
    # Прораб
    foreman: Link[User]
    # Бюджет
    budget: float


class Object(Document):
    # Код контракта
    contract_code: str
    # Бюджет контракта
    contract_budget: float
    # Объект/адрес объекта
    address: str
    # Дата начала работ
    jobs_start_date: datetime
    # Дата завершения работ
    jobs_finish_date: datetime
    # Список работ
    jobs: list[Link[Job]]

class Contract(Document):
