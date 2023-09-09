from copy import copy

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

import db
import sheets.worksheets
from bot.inline_keyboards import request_menu, user_request, pay_keyboard
from bot.utils import SPLITTER
from bot.utils import parse_request, prep_md
from bot.webapp.templates import load_from_base_template
from sheets.sheets import update as sheets_update

user_state = {}

routes = web.RouteTableDef()

from functools import wraps


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError:
            request: Request = args[0]
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    return wrapper


@routes.get('/approve_request')
async def bot_setup_handler(request: Request):
    return web.Response(text=load_from_base_template('approve_request.html'), content_type='text/html')


@routes.get('/decline_request')
async def bot_setup_handler(request: Request):
    return web.Response(text=load_from_base_template('decline_request.html'), content_type='text/html')


@routes.get('/request')
async def bot_setup_handler(request: Request):
    return web.Response(text=load_from_base_template('request.html'), content_type='text/html')


@routes.post('/checkData')
async def check_data_handler(request: Request):
    bot: Bot = request.app["bot"]

    data = await request.post()
    if check_webapp_signature(bot.token, data["_auth"]):
        return json_response({"ok": True})
    return json_response({"ok": False, "err": "Unauthorized"}, status=401)


@routes.post('/initApp')
async def init_app(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    user_id = data['_unsafe_data[user][id]']
    if check_webapp_signature(bot.token, data["_auth"]):
        return json_response({'response': {"ok": True}})

    return json_response({"ok": False, "err": "Unauthorized"}, status=401)


@routes.post('/getObjects')
@handle_errors
async def get_objects_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    response = dict(objects=sheets.worksheets.objects.get(web_app_init_data.user.username))
    return json_response(response, status=200)


@routes.post('/sendRequest')
@handle_errors
async def send_request_handler(r: Request):
    bot: Bot = r.app["bot"]
    data = await r.post()
    web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    request = db.requests.Request(
        web_app_init_data.user.username,
        web_app_init_data.user.id,
        data['request[object]'],
        data['request[counterparty]'],
        data['request[money]'],
        data['request[comment]']
    )
    group_id = (await db.data.get()).group_id

    text = parse_request(request)
    message = await bot.send_message(group_id, text, reply_markup=request_menu(request.id),
                                     parse_mode=ParseMode.MARKDOWN_V2)
    request.message_id = message.message_id

    notify_message = await bot.send_message(web_app_init_data.user.id,
                                            f'Вы отправили запрос на согласование и оплату\\.\n{parse_request(request, False)}\n\n❗️ Ожидайте ответа по вашему запросу\\!',
                                            parse_mode=ParseMode.MARKDOWN_V2)
    request.private_message_id = notify_message.message_id
    await request.save()
    return json_response(dict(ok=True), status=200)


@routes.post('/editRequest')
@handle_errors
async def edit_request_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    request = await db.requests.get(data['request_id'])
    edited_request = copy(request)
    edited_request.object = data['request[object]']
    edited_request.counterparty = data['request[counterparty]']
    edited_request.money = data['request[money]']
    edited_request.comment = data['request[comment]']
    group_id = (await db.data.get()).group_id
    text = parse_request(request, edited_request=edited_request)
    request = edited_request

    await bot.edit_message_text(text, group_id, request.message_id, text, reply_markup=request_menu(request.id),
                                parse_mode=ParseMode.MARKDOWN_V2)

    # await bot.send_message(group_id, f'↩️ Требуется повторное согласование.',
    #                        reply_to_message_id=request.message_id)

    await request.save()
    try:
        await bot.delete_message(request.from_id, request.edit_message_id)
    except TelegramBadRequest as e:
        if "message can't be deleted for everyone" in e.message:
            await bot.edit_message_text('✅ Вы успешно отредактировали заявку. Сообщение можно удалить.',
                                        request.from_id, request.edit_message_id)
    return json_response(dict(ok=True), status=200)


@routes.post('/getApprovalSelectors')
@handle_errors
async def get_approval_selectors_handlers(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    owner = sheets.worksheets.owners.get(web_app_init_data.user.username)
    response = dict(
        check=sheets.worksheets.check.get(),
        owners=['Оплачу сам' if u.name == owner.name else u.name for u in sheets.worksheets.owners.get()],
        owner=sheets.worksheets.owners.get(web_app_init_data.user.username).name
    )
    return json_response(response, status=200)


@routes.post('/approveRequest')
@handle_errors
async def send_message_handler(r: Request):
    bot: Bot = r.app["bot"]
    data = await r.post()

    web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])

    request = await db.requests.get(data['request_id'])

    await bot.delete_message(request.approving_by_user_id, request.approving_by_message_id)

    check = data['check']
    owner = sheets.worksheets.owners.get(request.approving_by_username)
    payer_name = data['payer_name']
    if payer_name == 'Оплачу сам':
        payer_name = owner.name

    if payer_name == owner.name:
        request.status = db.requests.RequestStatuses.APPROVED
    else:
        request.status = db.requests.RequestStatuses.ON_PAYER_CONFIRMATION
    request.check = check
    request.payer_name = payer_name
    await request.save()

    owner_text = f'{prep_md(owner.name)} \\(@{prep_md(owner.username)}\\)'
    group_id = (await db.data.get()).group_id
    text = parse_request(request)

    payer = sheets.worksheets.owners.get(name=payer_name)
    if payer_name == owner.name:
        approved_text = f'✅ *Согласовал* и 💵 *оплатил* {owner_text}\\.'
        text += f'\n{SPLITTER}\n💼 *От кого \\(юр\\. лицо/счёт\\):* {check}\n\n{approved_text}'
        await bot.send_message(request.from_id,
                               f'*Вы отправили запрос на согласование и оплату:*\n{parse_request(request, False)}\n{SPLITTER}\n💼 *От кого \\(юр\\. лицо/счёт\\):* {check}\n\n{approved_text}',
                               parse_mode=ParseMode.MARKDOWN_V2)
        await bot.delete_message(request.from_id, request.private_message_id)
    else:
        payer_text = f'{prep_md(payer.name)} \\(@{prep_md(payer.username)}\\)'
        text += f'\n{SPLITTER}\n💼 *От кого \\(юр\\. лицо/счёт\\):* {check}\n\n✅ *Согласовал* {owner_text}\n\n💵{payer_text} в *процессе оплаты*\\. _Подождите, пока он завершит оплату или отменит запрос\\._'

        user = sheets.worksheets.users.get(request.from_username)
        user_text = f'{prep_md(user.name)} \\(@{prep_md(user.username)}\\)'
        await bot.send_message(payer.id,
                               f'{owner_text} отправил *запрос на оплату* по заявке от {user_text}\\.\n{parse_request(request, False)}\n\n💼 *От кого \\(юр\\. лицо/счёт\\):* {check}\n\n❔ _Произведите оплату по заявке, либо верните запрос в стадию согласования\\._',
                               parse_mode=ParseMode.MARKDOWN_V2,
                               reply_markup=pay_keyboard(request.id))

    await bot.edit_message_text(text, group_id, request.message_id, parse_mode=ParseMode.MARKDOWN_V2)

    return json_response({"ok": True}, status=200)


@routes.post('/declineRequest')
@handle_errors
async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    base_url: str = request.app["base_url"]
    data = await request.post()
    web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    reason = data['reason']
    group_id = (await db.data.get()).group_id
    request = await db.requests.get(data['request_id'])
    owner = sheets.worksheets.owners.get(request.approving_by_username)
    owner_text = f'{prep_md(owner.name)} \\(@{prep_md(owner.username)}\\)'

    # Редактируем сообщение в группе с причиной отмены.
    text = parse_request(request)
    text += f'\n\n{SPLITTER}\n*❔ Причина:* {prep_md(reason)}\n\n↩️ {owner_text} *отклонил запрос*\\.'
    await bot.edit_message_text(text, group_id, request.message_id, parse_mode=ParseMode.MARKDOWN_V2)

    # Удаляем сообщение в ЛС у согласующего, который отменил запрос,
    # чтобы у него не было возможности согласовывать уже согласованный запрос.
    await bot.delete_message(request.approving_by_user_id, request.approving_by_message_id)

    # Отправляем запрос обратно сотруднику на редактирование и повторное согласование.
    edit_message = await bot.send_message(request.from_id,
                                          f'Ваш запрос отклонил {owner_text}\\.\n*Причина:* {prep_md(reason)}\n{parse_request(request, False)}',
                                          reply_markup=user_request(base_url, request.id),
                                          parse_mode=ParseMode.MARKDOWN_V2)

    request.edit_message_id = edit_message.message_id
    await request.save()
    return json_response({'ok': True}, status=200)


@routes.post('/getRequestById')
@handle_errors
async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    request = await db.requests.get(data['request_id'])
    response = request.__dict__
    return json_response(response, status=200)


@routes.get('/updateSheets')
async def send_message_handler(request: Request):
    await sheets_update()
