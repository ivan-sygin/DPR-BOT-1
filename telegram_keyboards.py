from aiogram import Bot, Dispatcher, types
import buttons_handler

kb = [
    [
        types.KeyboardButton(
            text="ℹ️ Информация о серверах",
        ),
        types.KeyboardButton(text="🆘 Помощь"),
    ],
]
keyboard_main = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def GenerateInlineServer(id):

    args = [id]
    buttons = [
        [
            types.InlineKeyboardButton(
                text=f"Бекапы",
                callback_data=buttons_handler.encode("setBackupMode", {"id": args[0]}),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"Прислать график HDD",
                callback_data=buttons_handler.encode("sendgraphic", {"id": args[0]}),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"Прислать график CPU",
                callback_data=buttons_handler.encode(
                    "Processorsendgraphic", {"id": args[0]}
                ),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"Установить ограничения по процессору",
                callback_data=f"setprocogr{args[0]}",
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"Установить ограничения по памяти",
                callback_data=f"setmemogr{args[0]}",
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"Удалить лишние соединения",
                callback_data=f"deleteconnections{args[0]}",
            ),
        ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def GenerateButtonsServers(count_buttons, count_in_row=5):
    buttons = [
        [],
    ]
    for i in range(count_buttons):
        if i // count_in_row != (i - 1) // count_in_row:
            buttons.append([])
        buttons[i // count_in_row].append(
            types.InlineKeyboardButton(
                text=f"Сервер {i + 1}",
                callback_data=buttons_handler.encode("serverInfo", {"id": i + 1}),
            ),
        )

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


def GenerateButtonProcessor(i):
    return (
        types.InlineKeyboardButton(
            text=f"Исправить ошибку с процессором",
            callback_data=f"processorFix|{i + 1}",
        ),
    )


def GenerateButtonMemory(i):
    return (
        types.InlineKeyboardButton(
            text=f"Исправить ошибку с памятью", callback_data=f"memoryFix|{i + 1}"
        ),
    )


def GenerateButtonConnection(i):
    return (
        types.InlineKeyboardButton(
            text=f"Исправить ошибку с соединениями",
            callback_data=f"connectionFix|{i + 1}",
        ),
    )


def GenerateButtonsBackupMenu(id_server):
    buttons = [
        [
            types.InlineKeyboardButton(
                text=f"Просмотреть бекапы",
                callback_data=buttons_handler.encode("viewBackups", {"id": id_server}),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"Восстановиться с бекапа",
                callback_data=buttons_handler.encode("restoreFromBackup", {"id": id_server}),
            ),
        ],
        [
            types.InlineKeyboardButton(
                text=f"Создать бекап",
                callback_data=buttons_handler.encode("createBackup", {"id": id_server}),
            ),
        ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

