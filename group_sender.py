import telebot
from users import User


class GlobalSender:
    users: list[User]
    bot: telebot.TeleBot
    usersUpdate: None

    def __init__(self, bot, users, usersUpdate):
        self.bot = bot
        self.users = users
        self.usersUpdate = usersUpdate

    async def sendToAll(self, text: str, keyboard=None):
        self.usersUpdate()
        for user in self.users:
            await self.bot.send_message(
                user.chat_id, text, reply_markup=keyboard
            )

    async def sendToNotified(self, text: str, keyboard=None):
        self.usersUpdate()
        for user in self.users:
            if user.notificationsEnabled:
                await self.bot.send_message(
                    user.chat_id, text, reply_markup=keyboard
                )

    async def sendToAdmin(self, text: str, keyboard=None):
        self.usersUpdate()
        for user in self.users:
            if user.notificationsEnabled and user.isAdmin:
                await self.bot.send_message(
                    user.chat_id, text, reply_markup=keyboard
                )
