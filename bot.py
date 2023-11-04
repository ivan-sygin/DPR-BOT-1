import asyncio
import logging
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import traceback
import sys
import telegram_keyboards
from requests_server import BackendConnector
import texts
from telegram_keyboards import keyboard_main, GenerateInlineServer
from db_connector import DB_Handler
import os
import requests
import urllib3
from group_sender import GlobalSender
import buttons_handler
from texts import help_text

urllib3.disable_warnings()
import threading
from initialize import sendStartBot

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher()

db = DB_Handler(
    host="localhost", port="5432", db="tg_bot_base", user="postgres", passw="admin"
)

users = db.getUsers()

auth_info = {}
def updateUsersList():
    global users
    users = db.getUsers()
    return users


gs = GlobalSender(bot, users, updateUsersList)

bc = BackendConnector('https', '26.0.102.28', '7278')

COUNT_SERVERS = 3


def find_user(id_find):
    for user in users:
        if id_find == user.chat_id:
            return user
    return None


@dp.message(F.text == "ℹ️ Информация о серверах")
async def cmd_start(message: types.Message):
    await check_all_servers(message)


@dp.message(F.text == "🆘 Помощь")
async def help_start(message: types.Message):
    await message.reply(
        texts.help_text
    )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = find_user(message.chat.id)
    if find_user(message.chat.id) is not None:
        await message.answer(f"Добро пожаловать, {user.name}", reply_markup=keyboard_main)
    else:
        await message.answer(
            texts.TryUnautorizedToUser(message)
        )
        await gs.sendToAdmin(
            texts.TryUnautorizedToAdmin(message)
        )


@dp.message(Command("all_servers"))
async def check_all_servers(message: types.Message):
    args = message.text.split()[1:]
    if find_user(message.chat.id) is not None:
        try:
            result = bc.fetchGet('/api/Server/servers', auth=True)

            text = f"""Информация по серверам:\n"""
            for i in result["response"]:
                text += f"\nID сервера: {i['id']}"
                text += f"\nИмя сервера: {i['displayedName']}"
                text += f"\nIP сервера: {i['host']}"
                text += f"\nПорт: {i['port']}"
                text += f"\n"

            keyboard = telegram_keyboards.GenerateButtonsServers(COUNT_SERVERS)
            await message.reply(text, reply_markup=keyboard)

        except:
            await message.reply("Костя включи сервер пж")
            '''
            await bot.send_message(
                "719194958", "Костя, я устал! Включи сервер пж!!! Надо фигачить"
            )
            '''
    else:
        await message.answer(
            texts.TryUnautorizedToUser(message)
        )
        await gs.sendToAdmin(
            texts.TryUnautorizedToAdmin(message)
        )


@dp.callback_query(F.data[:13] == "setBackupMode")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)

    await callback_query.message.edit_reply_markup(
        reply_markup=telegram_keyboards.GenerateButtonsBackupMenu(args['id']))


@dp.callback_query(F.data[:13] == "closeCallback")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()


@dp.callback_query(F.data[:11] == "viewBackups")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)
    res = bc.fetchGet('/api/Server/getbackups', auth=True, data={'serverId': args['id']})
    await callback_query.message.edit_reply_markup(reply_markup=telegram_keyboards.GenerateInlineServer(args['id']))
    text = f'🔙 Бекапы сервера {args["id"]} 🔙\n\n'
    if res['response'] != "Нет доступных бекапов":
        for item in res['response']:
            text += f'ID: {item["id"]}\nНазвание: {item["filename"]}\n\n'
    else:
        text += f'🧹Бекапов не обнаружено🧹'
    await bot.send_message(callback_query.message.chat.id,text, reply_markup=telegram_keyboards.GenerateButtonClose())


@dp.callback_query(F.data[:17] == "restoreFromBackup")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)
    res = bc.fetchGet('/api/Server/getbackups', auth=True, data={'serverId': args['id']})

    buttons = [

    ]

    if res['response'] == "Нет доступных бекапов":
        await bot.send_message(callback_query.message.chat.id, '🧹Бекапов не обнаружено🧹', reply_markup=telegram_keyboards.GenerateButtonClose())
        return

    for item in res['response']:
        buttons.append([
            types.InlineKeyboardButton(
                text=f"{item['filename']}",
                callback_data=buttons_handler.encode("SelectRestoreFromBackup",
                                                     {"id": args['id'], "num_backup": item['id']}),
            )
        ])

    buttons.append([
        types.InlineKeyboardButton(
            text=f"Назад",
            callback_data=buttons_handler.encode("serverInfo", {"id": args['id']}),
        )
    ])
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_reply_markup(reply_markup=kb)


@dp.callback_query(F.data[:23] == "SelectRestoreFromBackup")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)
    buttons = [
        [
            types.InlineKeyboardButton(
                text=f"Восстановить только данные",
                callback_data=buttons_handler.encode("SetRestoreFromBackup",
                                                     {"id": args['id'], 'num_backup': args['num_backup'],
                                                      'type': '-a'}),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"Удалить объекты базы данных перед их воссозданием",
                callback_data=buttons_handler.encode("SetRestoreFromBackup",
                                                     {"id": args['id'], 'num_backup': args['num_backup'],
                                                      'type': '-c'}),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"создает базу данных перед восстановлением в нее",
                callback_data=buttons_handler.encode(
                    "SetRestoreFromBackup", {"id": args['id'], 'num_backup': args['num_backup'], 'type': '-C'}
                ),
            ),
        ],
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.edit_reply_markup(reply_markup=kb)


@dp.callback_query(F.data[:20] == "SetRestoreFromBackup")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)
    res = bc.fetchPostNoResponse('/api/Server/usebackup', auth=True,
                 data={'serverId': args['id'], 'backupId': args['num_backup'], 'backuptype': args['type']})
    await callback_query.message.edit_reply_markup(reply_markup=telegram_keyboards.GenerateInlineServer(args['id']))
    await bot.send_message(callback_query.message.chat.id,'Бекап успешно восстановлен', reply_markup=telegram_keyboards.GenerateButtonClose())


@dp.callback_query(F.data[:12] == "createBackup")
async def process_button1(callback_query: types.CallbackQuery):
    import datetime
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)
    namefile = str(datetime.datetime.now())[:-7].replace(' ','-')
    res = bc.fetchPostNoResponse('/api/Server/createbackup', auth = True, data = {'serverId':args['id'],'filename':namefile})
    await callback_query.message.edit_reply_markup(reply_markup=telegram_keyboards.GenerateInlineServer(args['id']))
    await bot.send_message(callback_query.message.chat.id, f'Бекап {namefile} создан', reply_markup=telegram_keyboards.GenerateButtonClose())


@dp.callback_query(F.data[:10] == "serverInfo")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)
    mes = await bot.send_message(
        callback_query.from_user.id,
        f"Собираем информацию о сервере {args['id']}...",
    )

    try:
        result = bc.fetchGet('/api/Server/stats', auth=True, data={'id': args['id']})
        text = ""

        text += f"Информация о сервере {args['id']}\n"
        text += f"Загрузка процессора: {'+' if result['response']['processorPercentLoading'] == -1 else result['response']['processorPercentLoading']}\n"
        text += f"Размер базы данных: {result['response']['databaseSize']}\n"
        text += f"Количество подключений: {result['response']['connectionInfo']['totalConnections']}\n"
        text += f"Активных подключений: {result['response']['connectionInfo']['nonIdleConnections']}\n"

        await bot.send_message(
            callback_query.message.chat.id, text, reply_markup=GenerateInlineServer(args['id'])
        )
        await mes.delete()
    except:
        await bot.send_message(
            callback_query.message.chat.id, f"💀 СЕРВЕР {args['id']} НЕДОСТУПЕН 💀", reply_markup=telegram_keyboards.GenerateButtonClose()
        )
        await mes.delete()


@dp.callback_query(F.data[:10] == "setprocogr")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    number_server = callback_query.data[10:]
    buttons = [
        [
            types.InlineKeyboardButton(
                text=f"50%", callback_data=f"setogrproc{number_server}|50"
            ),
            types.InlineKeyboardButton(
                text=f"60%", callback_data=f"setogrproc{number_server}|60"
            ),
            types.InlineKeyboardButton(
                text=f"70%", callback_data=f"setogrproc{number_server}|70"
            ),
            types.InlineKeyboardButton(
                text=f"80%", callback_data=f"setogrproc{number_server}|80"
            ),
            types.InlineKeyboardButton(
                text=f"90%", callback_data=f"setogrproc{number_server}|90"
            ),
            types.InlineKeyboardButton(
                text=f"100%", callback_data=f"setogrmem{number_server}|100"
            ),
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback_query.message.edit_reply_markup(
        str(callback_query.message.message_id), reply_markup=keyboard
    )


@dp.callback_query(F.data[:17] == "deleteconnections")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    number_server = callback_query.data[17:]
    result = bc.fetchGetNoData('/api/Server/clearprocess', auth=True, data={'serverId': number_server})
    result = bc.fetchGet('/api/Server/stats', auth=True, data={'id': number_server})

    text = ""

    text += f"Информация о сервере {number_server}\n"
    text += f"Загрузка процессора: {result['response']['processorPercentLoading']}\n"
    text += f"Размер базы данных: {result['response']['databaseSize']}\n"
    text += f"Количество подключений: {result['response']['connectionInfo']['totalConnections']}\n"
    text += f"Активных подключений: {result['response']['connectionInfo']['nonIdleConnections']}\n"

    await callback_query.message.edit_text(text)
    await callback_query.message.edit_reply_markup(
        reply_markup=GenerateInlineServer(number_server)
    )
    await bot.send_message(callback_query.message.chat.id, "Удалили лишние соединения", reply_markup=telegram_keyboards.GenerateButtonClose())


@dp.callback_query(F.data[:9] == "setmemogr")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    number_server = callback_query.data[9:]
    buttons = [
        [
            types.InlineKeyboardButton(
                text=f"50%", callback_data=f"setogrmem{number_server}|50"
            ),
            types.InlineKeyboardButton(
                text=f"60%", callback_data=f"setogrmem{number_server}|60"
            ),
            types.InlineKeyboardButton(
                text=f"70%", callback_data=f"setogrmem{number_server}|70"
            ),
            types.InlineKeyboardButton(
                text=f"80%", callback_data=f"setogrmem{number_server}|80"
            ),
            types.InlineKeyboardButton(
                text=f"90%", callback_data=f"setogrmem{number_server}|90"
            ),
            types.InlineKeyboardButton(
                text=f"100%", callback_data=f"setogrmem{number_server}|100"
            ),
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback_query.message.edit_reply_markup(
        str(callback_query.message.message_id), reply_markup=keyboard
    )


@dp.callback_query(F.data[:20] == "Processorsendgraphic")
async def send_graphic(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)

    server_api = bc.fetchGet('/api/Server/lastrecords', auth=True, data={"serverId": args['id'], 'records': 5})
    # server_stats = bc.fetchGet('/api/Server/stats', auth=True, data={'id': args['id']})
    data_json = {
        "data": [

        ]
    }
    for item in server_api['response']:
        data_json['data'].append(
            {
                'unix_time': item['writedAt'],
                'workload': item['processorPercentLoading'],
            }
        )

    r = requests.post(f"http://26.65.125.199:8000/generateTimeChart", json=data_json)
    photo = types.BufferedInputFile(r.content, "image.png")
    await bot.send_photo(chat_id=callback_query.message.chat.id, photo=photo, reply_markup=telegram_keyboards.GenerateButtonClose())


@dp.callback_query(F.data[:11] == "sendgraphic")
async def send_graphic(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = buttons_handler.decode(callback_query.data)

    server_api = bc.fetchGet('/api/Server/server', auth=True, data={"id": args['id']})
    server_stats = bc.fetchGet('/api/Server/stats', auth=True, data={'id': args['id']})

    allocatedSpace = server_api['response']['allocatedSpace']
    databaseSize = server_stats['response']['databaseSize']

    total = int(allocatedSpace) * 1024
    used = int(databaseSize[:-2])

    r = requests.get(f"http://26.65.125.199:8000/generate_chart/{total}/{used}")
    photo = types.BufferedInputFile(r.content, "image.png")
    await bot.send_photo(chat_id=callback_query.message.chat.id, photo=photo, reply_markup=telegram_keyboards.GenerateButtonClose())


@dp.callback_query(F.data[:10] == "setogrproc")
async def process_button1(callback_query: types.CallbackQuery):
    args = [callback_query.data.split("|")[0][10:], callback_query.data.split("|")[1]]

    await callback_query.message.edit_reply_markup(
        str(callback_query.message.message_id),
        reply_markup=GenerateInlineServer(args[0]),
    )
    await bot.send_message(
        str(callback_query.message.chat.id),
        f"Установили ограничения по процессору на {args[1]}% для сервера {args[0]}", reply_markup=telegram_keyboards.GenerateButtonClose()
    )


@dp.callback_query(F.data[:12] == "processorFix")
async def process_button1(callback_query: types.CallbackQuery):
    global auth_info
    await bot.answer_callback_query(callback_query.id)

    if callback_query.message.chat.id not in auth_info.keys():
        auth_info[callback_query.message.chat.id] = False
        await bot.send_message(callback_query.message.chat.id, f'Пройдите авторизацию /auth <ключ>', reply_markup=telegram_keyboards.GenerateButtonClose())
        return
    if auth_info[callback_query.message.chat.id]:
        args = callback_query.data.split('|')[1:]
        await bot.send_message(callback_query.message.chat.id, f'Выполнено', reply_markup=telegram_keyboards.GenerateButtonClose())
        auth_info[callback_query.message.chat.id] = False
    else:
        await bot.send_message(callback_query.message.chat.id, f'Пройдите авторизацию /auth <ключ>', reply_markup=telegram_keyboards.GenerateButtonClose())


@dp.callback_query(F.data[:9] == "memoryFix")
async def process_button1(callback_query: types.CallbackQuery):
    global auth_info
    await bot.answer_callback_query(callback_query.id)

    if callback_query.message.chat.id not in auth_info.keys():
        auth_info[callback_query.message.chat.id] = False
        await bot.send_message(callback_query.message.chat.id, f'Пройдите авторизацию /auth <ключ>', reply_markup=telegram_keyboards.GenerateButtonClose())
        return
    if auth_info[callback_query.message.chat.id]:
        args = callback_query.data.split('|')[1:]
        await bot.send_message(callback_query.message.chat.id, f'Выполнено', reply_markup=telegram_keyboards.GenerateButtonClose())
        auth_info[callback_query.message.chat.id] = False
    else:
        await bot.send_message(callback_query.message.chat.id, f'Пройдите авторизацию /auth <ключ>', reply_markup=telegram_keyboards.GenerateButtonClose())

@dp.message(Command("auth"))
async def check_start(message: types.Message):
    args = message.text.split()[1:]
    if os.environ["USER_TOKEN"] == args[0]:
        auth_info[message.chat.id] = True
        await message.delete()
    else:
        await message.delete()
        await bot.send_message(message.chat.id,"Ошибка авторизации!", reply_markup=telegram_keyboards.GenerateButtonClose())



@dp.callback_query(F.data[:13] == "connectionFix")
async def process_button1(callback_query: types.CallbackQuery):
    global auth_info
    await bot.answer_callback_query(callback_query.id)

    if callback_query.message.chat.id not in auth_info.keys():
        auth_info[callback_query.message.chat.id] = False
        await bot.send_message(callback_query.message.chat.id, f'Пройдите авторизацию /auth <ключ>', reply_markup=telegram_keyboards.GenerateButtonClose())
        return
    if auth_info[callback_query.message.chat.id]:
        args = callback_query.data.split('|')[1:]
        await bot.send_message(callback_query.message.chat.id, f'Выполнено', reply_markup=telegram_keyboards.GenerateButtonClose())
        auth_info[callback_query.message.chat.id] = False
    else:
        await bot.send_message(callback_query.message.chat.id, f'Пройдите авторизацию /auth <ключ>', reply_markup=telegram_keyboards.GenerateButtonClose())


@dp.callback_query(F.data[:9] == "setogrmem")
async def process_button1(callback_query: types.CallbackQuery):
    args = [callback_query.data.split("|")[0][9:], callback_query.data.split("|")[1]]

    await callback_query.message.edit_reply_markup(
        str(callback_query.message.message_id),
        reply_markup=GenerateInlineServer(args[0]),
    )
    await bot.send_message(
        str(callback_query.message.chat.id),
        f"Установили ограничения по памяти на {args[1]}% для сервера {args[0]}", reply_markup=telegram_keyboards.GenerateButtonClose()
    )


@dp.message(Command("check"))
async def check_start(message: types.Message):
    args = message.text.split()[1:]
    if find_user(message.chat.id) is not None:

        if args:
            result = bc.fetchGet('/api/Server/stats', auth=True, data={'id': args[0]})
            text = ""

            text += f"Информация о сервере {args[0]}\n"
            text += f"Загрузка процессора: {'+' if result['response']['processorPercentLoading'] == -1 else result['response']['processorPercentLoading']}\n"
            text += f"Размер базы данных: {result['response']['databaseSize']}\n"
            text += f"Количество подключений: {result['response']['connectionInfo']['totalConnections']}\n"
            text += f"Активных подключений: {result['response']['connectionInfo']['nonIdleConnections']}\n"

            await message.reply(f"{text}", reply_markup=GenerateInlineServer(args[0]))
        else:
            await message.reply("Вы использовали команду /check без аргументов")
    else:
        await message.answer(
            f"Вас нет в списке администраторов баз данных. Обратитесь к системному администратору."
        )
        await gs.sendToAdmin(
            f"Попытка взять данные у бота:\nchat_id: {message.chat.id}\nИмя в Telegrame: {message.chat.full_name}\nДанные про базу: {args}"
        )


async def main():
    tasks = [longpooling(), dp.start_polling(bot)]
   #tasks = [dp.start_polling(bot)]
    global COUNT_SERVERS
    try:
        COUNT_SERVERS = len(bc.fetchGet("/api/Server/servers", auth=True)['response'])
        await gs.sendToNotified('Сервис работает! Status: 200', keyboard=keyboard_main)
        await asyncio.gather(*tasks)
    except Exception as e:
        trace = traceback.extract_tb(sys.exc_info()[2])

        for frame in trace:
            print(f"Строка: {frame.lineno}, Функция: {frame.name}, Код: {frame.line}, Ошибка: {e}")

        await gs.sendToNotified(
            f"Бот не работает!\nСтрока: {frame.lineno}, Функция: {frame.name}, Код: {frame.line}, Ошибка: {e}")


def call_admin():
    r = requests.post(
        f"http://26.65.125.199:8000/callAdmin?phone_number=79493324599", verify=False,
    )


async def longpooling():
    import time
    server = {}
    while True:
        for i in range(COUNT_SERVERS):
            try:
                result = bc.fetchGet('/api/Server/stats', auth=True, data={'id': i + 1})

                if 'errorText' not in result.keys():

                    jsik = bc.fetchGet('/api/Server/findproblems', auth=True, data={'serverId': i + 1})
                    if jsik['response']:
                        if (i + 1) not in server.keys():
                            server[i + 1] = 1
                        else:
                            server[i + 1] += 1
                        """"""
                        if server[i + 1] == 10:
                            server[i + 1] = 1
                        if server[i + 1] == 1:
                            text_all_errors = ''
                            type_smiles = {'Error': '🆘', 'Warning': '⚠️'}

                            for item in jsik['response']:
                                text_all_errors += type_smiles[item['alert']] + ' ' + item['text'] + '\n'
                            result_from_GPT = ''
                            try:
                                r = requests.post(
                                    f"http://26.65.125.1991:8000/sendMessage?temperature=0.87",
                                    json=[
                                        {
                                            "role": "user",
                                            "content": "Опиши двумя словами. У меня возникла проблема с базой данных на PostgreSQL. Вот описание: "
                                                       + text_all_errors
                                        }
                                    ],
                                    headers={
                                        "accept": "application/json",
                                        "Content-type": "application/json",
                                    },
                                    verify=False,
                                )
                                res = r.json()
                                result_from_GPT = res['choices'][0]['message']['content']
                            except Exception as e:
                                result_from_GPT = 'GPT не знает что ответить'
                            buttons = [[]]
                            for item in jsik['response']:
                                if item['type'] == "processor_loaded":
                                    buttons.append(telegram_keyboards.GenerateButtonProcessor(i))
                                elif item['type'] == "free_space_running_out":
                                    buttons.append(telegram_keyboards.GenerateButtonMemory(i))

                            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

                            for item in jsik['response']:
                                if item['alert'] == 'Error':
                                    # call_admin()
                                    break

                            await gs.sendToAdmin(
                                f"❗️ТРЕВОГА! СЕРВЕР {i + 1}❗️\n\n{text_all_errors}\n\n🤖Искусственный интеллект🤖: {result_from_GPT}",
                                keyboard=keyboard,
                            )
            except Exception as e:
                print(e)
        await asyncio.sleep(15)


if __name__ == "__main__":
    asyncio.run(main())
