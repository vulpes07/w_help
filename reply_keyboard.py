from aiogram.types import ReplyKeyboardMarkup, KeyboardButton




# реплай клавиатура после регистрации 

menu_2 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽️ бесплатное питание")],
        [KeyboardButton(text="🏠 Бесплатное жилье и хостелы")],
        [KeyboardButton(text="🌸 Помощь женщинам")],
        ],
    resize_keyboard=True
)

menu_2_kyrg = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽️ акысыз тамак-аш")],
        [KeyboardButton(text="🏠 Акысыз жашай турган жайлар жана хостелдер")],
        [KeyboardButton(text="🌸 Аялдарга жардам")],
    ],

    resize_keyboard=True
)


menu_2_germ = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽️ Kostenlose Verpflegung")],
        [KeyboardButton(text="🏠 Kostenlose Unterkünfte und Hostels")],
        [KeyboardButton(text="🌸 Hilfe für Frauen")],
    ],
    resize_keyboard=True
)


menu_2_eng = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽️ Free meals and food")],
        [KeyboardButton(text="🏠 Free housing and hostels")],
        [KeyboardButton(text="🌸 Support for women")],
    ],
    resize_keyboard=True
)



# клавиатура после вопроса про номер, на вопросе про локацию

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить локацию", request_location=True)],
    ],
    resize_keyboard=True
)



menu_kyrg = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Локация жөнөтүү", request_location=True)],
    ],
    resize_keyboard=True
)


menu_germ = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Senden Sie den Standort", request_location=True)],
    ],
    resize_keyboard=True
)


menu_eng = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📍 Send the location", request_location=True)],
    ],
    resize_keyboard=True
)



# Клавиатура для команды /info
response_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Админ-панель")],
            [KeyboardButton(text="➕ Зарегистрироваться")],
            [KeyboardButton(text="🍽️ бесплатное питание")],
            [KeyboardButton(text="🏠 Бесплатное жилье и хостелы")],
            [KeyboardButton(text="🌸 Помощь женщинам")],
        ],
        resize_keyboard=True
    )



response_menu_germ = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin panel")],
            [KeyboardButton(text="➕ Registrieren")],
            [KeyboardButton(text="🍽️ Kostenlose Verpflegung")],
            [KeyboardButton(text="🏠 Kostenlose Unterkünfte und Hostels")],
            [KeyboardButton(text="🌸 Hilfe für Frauen")],
        ],
        resize_keyboard=True
    )


response_menu_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin Panel")],
            [KeyboardButton(text="➕ Register")],
            [KeyboardButton(text="🍽️ Free meals and food")],
            [KeyboardButton(text="🏠 Free housing and hostels")],
            [KeyboardButton(text="🌸 Support for women")],
        ],
        resize_keyboard=True
    )


response_menu_kyrg = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Админ панель")],
            [KeyboardButton(text="➕ Катталуу")],
            [KeyboardButton(text="🍽️ акысыз тамак-аш")],
            [KeyboardButton(text="🏠 Акысыз жашай турган жайлар жана хостелдер")],
            [KeyboardButton(text="🌸 Аялдарга жардам")],
        ],
        resize_keyboard=True
    )


# Клавиатура до регистрации  
keyboard_3 = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Зарегистрироваться")]
        ],
        resize_keyboard=True)


keyboard_3_kyrg = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Катталуу")]
        ],
        resize_keyboard=True)


keyboard_3_germ = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Registrieren")]
        ],
        resize_keyboard=True)


keyboard_3_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Register")]
        ],
        resize_keyboard=True)