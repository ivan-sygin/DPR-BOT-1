import telebot
from telegram_keyboards import keyboard_main

async def sendStartBot(bot:telebot.TeleBot, users):
    print(users)
    for user in users:
        if user[3]:
            await bot.send_message(
                user[0], "Сервер запущен, базы проверяются", reply_markup=keyboard_main
            )