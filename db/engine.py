from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient

from utils import get_classes_in_folder


async def init():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    models = get_classes_in_folder('db/models', Document)
    await init_beanie(database=client.payeebot, document_models=models)
