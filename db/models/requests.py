import asyncio
import time
import uuid

import sheets.worksheets.users
from db.pickler import Pickler


pickler = Pickler('requests')


class RequestStatuses:
    ON_APPROVAL = 0
    NEEDS_CORRECTION = 1
    APPROVED = 2
    DECLINED = 3
    ON_PAYER_CONFIRMATION = 4


class Request:
    def __init__(self, from_username, from_id, object, counterparty, money, comment, id=None):
        self.from_username = from_username
        self.from_id = from_id
        self.private_message_id = None
        self.object = object
        self.counterparty = counterparty
        self.money = money
        self.comment = comment
        self.check = None
        self.id = id or str(uuid.uuid4())
        self.message_id = None
        self.status = RequestStatuses.ON_APPROVAL
        self.approving_by_user_id = None
        self.approving_by_message_id = None
        self.approving_by_username = None
        self.edit_message_id = None
        self.last_edit_ts = time.time()
        self.payer_name = None

    async def save_excel(self):
        from excel import generate_journal
        if self.status == RequestStatuses.APPROVED:
            requests = []
            for request in await get():
                if request.from_username == self.from_username and request.status == RequestStatuses.APPROVED:
                    requests.append(request)
            user = sheets.worksheets.users.get(self.from_username)
            generate_journal(requests, f'.journals/{user.name}.xlsx')

    async def save(self):
        requests = await get()

        self.last_edit_ts = time.time()

        edited = False
        for i, request in enumerate(requests):
            if request.id == self.id:
                requests[i] = self
                edited = True
                break

        if not edited:
            requests.append(self)

        await pickler.write(requests)

        asyncio.create_task(self.save_excel())


async def get(request_id=None) -> list[Request] | Request | None:
    requests = await pickler.read()
    if request_id:
        for request in requests:
            if request.id == request_id:
                return request
        return None
    return requests or []
