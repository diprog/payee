from aiogram.filters.callback_data import CallbackData


class ApproveRequest(CallbackData, prefix='approve_request'):
    """
    Объект CallbackData для обработки запроса на утверждение.
    Префикс: 'approve_request'
    Поля: request_id (идентификатор запроса)
    """
    request_id: str


class CancelApproval(CallbackData, prefix='cancel_approval'):
    """
    Объект CallbackData для обработки отмены утверждения.
    Префикс: 'cancel_approval'
    Поля: request_id (идентификатор запроса)
    """
    request_id: str


class RequestCompletePayment(CallbackData, prefix='complete_payment'):
    request_id: str

class GenerateJournalSelectUser(CallbackData, prefix='generate_journal_select_user'):
    """
    Объект CallbackData для обработки выбора пользователя при генерации журнала.
    Префикс: 'generate_journal_select_user'
    Поля: username (имя пользователя)
    """
    username: str


class GenerateJournal(CallbackData, prefix='generate_journal'):
    """
    Объект CallbackData для обработки генерации журнала.
    Префикс: 'generate_journal'
    """
    ...
