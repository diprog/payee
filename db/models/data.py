from db.pickler import Pickler

pickler = Pickler('data')


class Data:
    def __init__(self, group_id: int = None, backup_chat_id: int = None):
        self.group_id = group_id
        self.backup_chat_id = backup_chat_id

    async def save(self):
        await pickler.write(self)


async def get():
    return await pickler.read() or Data()
