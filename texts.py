import aiogram.types

help_text = """Вот небольшой список команд, которые доступны в нашем боте:

/start - Запускает бота.
/all_servers - Выводит информацию о всех доступных базах данных.
/check <id> - Выводит текущее состояние указанной базы данных. Вместо <id> введите id необходимой БД.
"""

def TryUnautorizedToUser(message:aiogram.types.Message):
    return f"Вас нет в списке администраторов баз данных. Обратитесь к системному администратору."

def TryUnautorizedToAdmin(message:aiogram.types.Message):
    return f"Попытка подключится к боту:\nchat_id: {message.chat.id}\nИмя в Telegram: {message.chat.full_name}"