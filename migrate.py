import asyncio

import db
from db.models.request import Request
from pprint import pprint

async def migrate_db():
    await db.engine.init()
    requests = await db.requests.get()
    for request in requests:
        pprint(request.__dict__)
        r = Request(**request.__dict__)
        await r.insert()

if __name__ == '__main__':
    asyncio.run(migrate_db())
