from beanie import Document


class Request(Document):
    from_username: str
    from_id: int
    private_message_id: int
    object: str
    counterparty: str
    money: float
    comment: str
    check: str
    id: str
    message_id: int
    status: int
    approving_by_user_id: int
    approving_by_message_id: int
    approving_by_username: int
    edit_message_id: int
    last_edit_ts: float
    payer_name: str
