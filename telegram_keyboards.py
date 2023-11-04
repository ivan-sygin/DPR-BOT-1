from aiogram import Bot, Dispatcher, types

kb = [
            [
                types.KeyboardButton(text="ℹ️ Информация о серверах",),
                types.KeyboardButton(text="🆘 Помощь")
            ],
        ]
keyboard_main = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def GenerateInlineServer(id):
    args = [id]
    buttons = [
            [types.InlineKeyboardButton(text=f"Прислать график",
                                    callback_data=f"sendgraphic|{args[0]}"), ],
            [
                types.InlineKeyboardButton(text=f"Установить ограничения по процессору",
                                           callback_data=f"setprocogr{args[0]}"),

            ],
            [types.InlineKeyboardButton(text=f"Установить ограничения по памяти",
                                        callback_data=f"setmemogr{args[0]}"), ],
            [types.InlineKeyboardButton(text=f"Удалить лишние соединения",
                                        callback_data=f"deleteconnections{args[0]}"), ]
        ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def GenerateButtonsServers(count_buttons,count_in_row = 5):
    buttons = [
        [],
    ]
    for i in range(count_buttons):
        if i // count_in_row != (i - 1) // count_in_row:
            buttons.append([])
        buttons[i // count_in_row].append(
            types.InlineKeyboardButton(
                text=f"Сервер {i + 1}", callback_data=f"Server{i + 1}"
            ),
        )

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)