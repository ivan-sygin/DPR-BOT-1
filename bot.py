import asyncio
import logging
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

import telegram_keyboards
from requests_server import BackendConnector
import texts
from telegram_keyboards import keyboard_main, GenerateInlineServer
from db_connector import DB_Handler
import os
import requests
import urllib3
from group_sender import GlobalSender
from texts import help_text

urllib3.disable_warnings()
import threading
from initialize import sendStartBot

COUNT_SERVERS = 2

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.environ["TOKEN"])
dp = Dispatcher()

db = DB_Handler(
    host="localhost", port="5432", db="tg_bot_base", user="postgres", passw="admin"
)

users = db.getUsers()


def updateUsersList():
    global users
    users = db.getUsers()
    return users


gs = GlobalSender(bot, users, updateUsersList)

bc = BackendConnector('https', '26.0.102.28', '7278')


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

            keyboard = telegram_keyboards.GenerateButtonsServers(2)
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


@dp.callback_query(F.data[:6] == "Server")
async def process_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    mes = await bot.send_message(
        callback_query.from_user.id,
        f"Собираем информацию о сервере {callback_query.data[6:]}...",
    )
    args = [callback_query.data[6:]]

    result = bc.fetchGet('/api/Server/stats', auth=True, data={'id': args[0]})
    text = ""

    text += f"Информация о сервере {args[0]}\n"
    text += f"Загрузка процессора: {result['response']['processorPercentLoading']}\n"
    text += f"Размер базы данных: {result['response']['databaseSize']}\n"
    text += f"Количество подключений: {result['response']['connectionInfo']['totalConnections']}\n"
    text += f"Активных подключений: {result['response']['connectionInfo']['nonIdleConnections']}\n"

    await bot.send_message(
        callback_query.message.chat.id, text, reply_markup=GenerateInlineServer(args[0])
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

    result = bc.fetchGet('/api/Server/stats', auth=True, data={'id': number_server})

    text = ""

    text += f"Информация о сервере {number_server}\n"
    text += f"Загрузка процессора: {result['response']['processorPercentLoading']}\n"
    text += f"Размер базы данных: {result['response']['databaseSize']}\n"
    text += f"Количество подключений: {result['response']['connectionInfo']['nonIdleConnections']}\n"
    text += f"Активных подключений: {result['response']['connectionInfo']['nonIdleConnections']}\n"

    await callback_query.message.edit_text(text)
    await callback_query.message.edit_reply_markup(
        reply_markup=GenerateInlineServer(number_server)
    )
    await bot.send_message(callback_query.message.chat.id, "Удалили лишние соединения")


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


@dp.callback_query(F.data[:11] == "sendgraphic")
async def send_graphic(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    args = callback_query.data.split()[1:]
    total = 100
    used = 20
    r = requests.get(f"http://26.65.125.199:8000/generate_chart/{total}/{used}")
    photo = types.BufferedInputFile(r.content, "image.png")
    await bot.send_photo(chat_id=callback_query.message.chat.id, photo=photo)


@dp.callback_query(F.data[:10] == "setogrproc")
async def process_button1(callback_query: types.CallbackQuery):
    args = [callback_query.data.split("|")[0][10:], callback_query.data.split("|")[1]]

    await callback_query.message.edit_reply_markup(
        str(callback_query.message.message_id),
        reply_markup=GenerateInlineServer(args[0]),
    )
    await bot.send_message(
        str(callback_query.message.chat.id),
        f"Установили ограничения по процессору на {args[1]}% для сервера {args[0]}",
    )


@dp.callback_query(F.data[:9] == "setogrmem")
async def process_button1(callback_query: types.CallbackQuery):
    args = [callback_query.data.split("|")[0][9:], callback_query.data.split("|")[1]]

    await callback_query.message.edit_reply_markup(
        str(callback_query.message.message_id),
        reply_markup=GenerateInlineServer(args[0]),
    )
    await bot.send_message(
        str(callback_query.message.chat.id),
        f"Установили ограничения по памяти на {args[1]}% для сервера {args[0]}",
    )


@dp.message(Command("check"))
async def check_start(message: types.Message):
    args = message.text.split()[1:]
    if find_user(message.chat.id) is not None:

        if args:
            result = bc.fetchGet('/api/Server/stats', auth=True, data={'id': args[0]})
            text = ""

            text += f"Информация о сервере {args[0]}\n"
            text += f"Загрузка процессора: {result['response']['processorPercentLoading']}\n"
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
            f"Попытка взять данные у бота:\nchat_id: {message.chat.id}\nИмя в Telegram: {message.chat.full_name}\nДанные про базу: {args}"
        )


async def main():
    await gs.sendToNotified('Сервис работает! Status: 200', keyboard=keyboard_main)

    #tasks = [longpooling(), dp.start_polling(bot)]

    tasks = [dp.start_polling(bot)]

    await asyncio.gather(*tasks)


def func():
    asyncio.run(main())


def func2():
    asyncio.run(longpooling())


async def longpooling():
    import time

    while True:
        for i in range(COUNT_SERVERS):
            result = bc.fetchGet('/api/Server/stats', auth=True, data={'id': i + 1})
            jsik = bc.fetchGet('/api/Server/findproblems', auth=True, data={'serverId': i + 1})

            """"""
            r = requests.post(
                f"http://26.65.125.199:8000/sendMessage?temperature=0.87",
                json=[
                    {
                        "role": "user",
                        "content": "У меня возникла проблема с базой данных на PostgreSQL. Вот детальное описание: "
                                   + jsik["response"][0]["text"],
                    }
                ],
                headers={
                    "accept": "application/json",
                    "Content-type": "application/json",
                },
                verify=False,
            )
            res = r.json()
            buttons = [
                [
                    types.InlineKeyboardButton(
                        text=f"Исправить ошибку с БД", callback_data=f"deleteDB|{i + 1}"
                    ),
                ],
            ]
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
            if jsik["response"][0]["alert"] == "Error":
                await gs.sendToAdmin(
                    f"❗️ТРЕВОГА! СЕРВЕР {i + 1}❗️\n{jsik['response'][0]['text']}\n\n🤖Искусственный интеллект🤖:{res['choices'][0]['message']['content']}",
                    keyboard=keyboard,
                )
        time.sleep(15)


if __name__ == "__main__":
    # Создание списка задач
    asyncio.run(main())
