import os, sys, math
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from database import init_db, add_user, list_users, remove_user, is_registered
from reply_keyboard import menu_eng, menu, menu_germ, menu_kyrg, keyboard_3
from reply_keyboard import response_menu, response_menu_eng, response_menu_germ, response_menu_kyrg
from reply_keyboard import menu_2, menu_2_eng, menu_2_kyrg, menu_2_germ
from dotenv import load_dotenv
load_dotenv()


router = Router()

init_db()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  
if not BOT_TOKEN or not ADMIN_ID:
    sys.exit("Error: BOT_TOKEN or ADMIN_ID environment variable not set.")

DB_PATH = "bot_db.sqlite3"


from datetime import datetime, timedelta

def format_date(db_date, lang):
    dt = datetime.strptime(db_date, "%Y-%m-%d %H:%M:%S")
    dt += timedelta(hours=6)  
    
    date_formats = {
        "ru": dt.strftime("%d.%m.%Y %H:%M"),
        "kg": dt.strftime("%d.%m.%Y %H:%M"),
        "en": dt.strftime("%m/%d/%Y %H:%M"),
        "de": dt.strftime("%d.%m.%Y %H:%M")
    }
    return date_formats.get(lang, dt.strftime("%Y-%m-%d %H:%M"))



PHONE_PROMPTS = {
    "ru": "Введите номер телефона:",
    "kg": "Телефон номериңизди жазыңыз:",
    "en": "Enter your phone number:",
    "de": "Geben Sie Ihre Telefonnummer ein:"
}  


LOCATION_PROMPTS = {
    "ru": "Отправьте вашу геолокацию, включите локацию на устройстве для определения вашей геопозиции на данный момент ",
    "kg": "Геолокацияңызды жөнөтүңүз, учурдагы геолокацияңызды аныктоо үчүн локация жаңдырыңыз",
    "en": "Send your geolocation, enable location on your device to determine your current geolocation",
    "de": "Senden Sie Ihre Geolokalisierung, aktivieren Sie die Ortung auf Ihrem Gerät, um Ihre aktuelle Geolokalisierung zu bestimmen"
    }

KIDS_BUTTONS = {
    "ru": {"yes": "Да", "no": "Нет"},
    "kg": {"yes": "Ооба", "no": "Жок"},
    "en": {"yes": "Yes", "no": "No"},
    "de": {"yes": "Ja", "no": "Nein"}
}


KIDS_PROMPTS = {
    "ru": "У вас есть дети?",  
    "kg": "Сизде балдар барбы?",  
    "en": "Do you have children?",  
    "de": "Haben Sie Kinder?"  
}


PROBLEM_PROMPTS = {
    "ru": "Расскажите о вашей проблеме",  
    "kg": "Өз көйгөйүңүз жөнүндө айтыңыз",  
    "en": "Tell us about your problem",  
    "de": "Erzählen Sie uns von Ihrem Problem"  
}


import requests

def get_address_from_coords(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 18, 
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "OSH_SU_PROFESSIONS_CHOOSER"  
        }
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        address = data.get("address", {})

        road = address.get("road", "")
        house_number = address.get("house_number", "")
        neighbourhood = address.get("neighbourhood", "")
        suburb = address.get("suburb", "")
        city = address.get("city") or address.get("town") or address.get("village", "")
        state = address.get("state", "")
        country = address.get("country", "")

        components = [road, house_number, neighbourhood, suburb, city, state, country]
        return ", ".join([part for part in components if part])
    except Exception as e:
        return "Не удалось определить точный адрес"




def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lat2 - lon2)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class FSMAdminAdd(StatesGroup):
    name = State()
    age = State()
    gender = State()
    lang = State()
    ph_num = State()
    with_kids = State()
    problem = State()
    latitude = State()
    longitude = State()
    

class FSMAdminDel(StatesGroup):
    choose_user = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить пользователя")],
            [KeyboardButton(text="📋 Список пользователей")],
            [KeyboardButton(text="❌ Удалить пользователя")],
            [KeyboardButton(text="🍽️ бесплатное питание")],
            [KeyboardButton(text="🏠 Бесплатное жилье и хостелы")],
            [KeyboardButton(text="🌸 Помощь женщинам")],
        ],
        resize_keyboard=True
    )
keyboard_2 = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Админ-панель")],
            [KeyboardButton(text="➕ Зарегистрироваться")]
        ],
        resize_keyboard=True
    )




@router.message(Command("start_rus"))
async def cmd_start_rus(message: types.Message):
    await message.answer(
            f"""👋 Привет, {message.from_user.first_name}! Вас приветствует наша команда для оказания помощи. Перед тем как воспользоваться функциями бота, пройдите регистрацию. А если уже прошли регистрацию, нажмите на /info.

Если хотите поменять язык, нажмите /start          

По всем дополнительным вопросам обращайтесь к создателю бота: @vulpes_07.

Выберите действие:""",
            reply_markup=keyboard_2
        )

@router.message(Command("admin"))
async def admin_greeting(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Приветствую, администратор {message.from_user.first_name}!\n"
            "🛠 Вам доступны все административные функции:",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "⛔ У вас нет доступа к этой команде",
            reply_markup=keyboard_2
        )
@router.message(F.text == "🛠 Админ-панель")
async def admin_panel_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к этой функции")
        return
    else:
        await message.answer(
            f"👋 Приветствую, администратор {message.from_user.first_name}!\n"
            "🛠 Вам доступны все административные функции:",
            reply_markup=keyboard)  


@router.message(F.text == "➕ Добавить пользователя")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await start_add_user(message, state)

@router.message(F.text == "➕ Зарегистрироваться")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await start_add_user(message, state)

@router.message(F.text == "📋 Список пользователей")
async def handle_list_users_button(message: types.Message):
    await list_users_command(message)

@router.message(F.text == "❌ Удалить пользователя")
async def handle_remove_user_button(message: types.Message, state: FSMContext):
    await start_remove_user(message, state)

@router.message(Command("add_user"))
async def start_add_user(message: types.Message, state: FSMContext):
    await message.answer("Введите ваше имя:")
    await state.set_state(FSMAdminAdd.name)


@router.message(FSMAdminAdd.name)
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите свой возраст:")
    await state.set_state(FSMAdminAdd.age)

@router.message(FSMAdminAdd.age)
async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите возраст.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(FSMAdminAdd.gender) 
    await message.answer("Выберите пол:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Мужчина", callback_data="gender_male")],
        [InlineKeyboardButton(text="Женщина", callback_data="gender_female")]
    ]))
    await state.set_state(FSMAdminAdd.gender)

@router.callback_query(lambda call: call.data.startswith("gender_"))
async def load_gender(callback_query: types.CallbackQuery, state: FSMContext):
    
    data = await state.get_data()
    lang = data.get("lang", "ru")  
    
    gender = "Мужчина" if callback_query.data == "gender_male" else "Женщина"
    await state.update_data(gender=gender, lang=lang)
    await callback_query.message.answer(PHONE_PROMPTS.get(lang, "Введите номер телефона:"))
    await state.set_state(FSMAdminAdd.ph_num)
    
@router.message(FSMAdminAdd.ph_num)
async def load_ph_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите номер телефона.")
        return
    await state.update_data(ph_num=int(message.text))
    
    lang = (await state.get_data()).get("lang", "ru")
    buttons = KIDS_BUTTONS.get(lang, KIDS_BUTTONS["ru"])
    
    await message.answer(KIDS_PROMPTS[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buttons["yes"], callback_data="kids_yes")],
        [InlineKeyboardButton(text=buttons["no"], callback_data="kids_no")]
    ]))
    await state.set_state(FSMAdminAdd.with_kids)


@router.callback_query(lambda call: call.data in ["kids_yes", "kids_no"])
async def load_with_kids(callback_query: types.CallbackQuery, state: FSMContext):
    with_kids = "Да" if callback_query.data == "kids_yes" else "Нет"
    await state.update_data(with_kids=with_kids)
    
    lang = (await state.get_data()).get("lang", "ru")
    await callback_query.message.answer(PROBLEM_PROMPTS[lang])
    await state.set_state(FSMAdminAdd.problem)



@router.message(FSMAdminAdd.problem)
async def load_problem(message: types.Message, state: FSMContext):
    await state.update_data(problem=message.text)

    lang = (await state.get_data()).get("lang", "ru")
    await message.answer(f"{message.from_user.full_name}, {LOCATION_PROMPTS[lang]}",  
        reply_markup=menu if lang == "ru" 
        else menu_eng if lang == "en" 
        else menu_germ if lang == "de" 
        else menu_kyrg)

    await state.set_state(FSMAdminAdd.latitude)


@router.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    lang = user_data.get("lang", "ru")  
    
    
    SUCCESS_MSGS = {
    "ru": "Ваши данные успешно добавлены! Спасибо за регистрацию, можете воспользоваться функциями бота",
    "en": "The data has been saved successfully! Thank you for the registration, now you can use bot functions",
    "de": "Die Daten wurden erfolgreich gespeichert! Vielen Dank für die Registrierung, jetzt können Sie die Bot-Funktionen nutzen",
    "kg": "Дайындарыңыз ийгиликтүү кошулду! Каттоодон өткөнүңүз үчүн рахмат, боттун мүмкүнчүлүктөрүн колдоно аласыз"
    }

    add_user(
    name=user_data["name"],
    age=user_data["age"],
    gender=user_data["gender"],
    ph_num=user_data["ph_num"],
    with_kids=user_data["with_kids"],
    problem=user_data["problem"],
    latitude=message.location.latitude,
    longitude=message.location.longitude,
    user_id=message.from_user.id,
    first_name=message.from_user.first_name,
    last_name=message.from_user.last_name,
    username=message.from_user.username
    )

    await message.answer(
    SUCCESS_MSGS[lang], 
    reply_markup=menu_2 if lang == "ru" 
    else menu_2_eng if lang == "en" 
    else menu_2_germ if lang == "de" 
    else menu_2_kyrg
    )
    await state.clear()



@router.message(Command("info"))
async def info_command(message: types.Message, state: FSMContext):
    
    lang = (await state.get_data()).get("lang", "ru")
    COMM_LIST_PROMPTS = {
    "ru": "📋Список доступных команд: ",
    "kg": "📋Жеткиликтүү буйруктардын тизмеси: ",
    "en": "📋List of the available cammands: ",
    "de": "📋Liste der verfügbaren Befehle: "
    }

    await message.answer(f"{message.from_user.full_name}, {COMM_LIST_PROMPTS[lang]}",  
    reply_markup=response_menu if lang == "ru" 
    else response_menu_eng if lang == "en" 
    else response_menu_germ if lang == "de" 
    else response_menu_kyrg )





@router.message(Command("list_users"))
async def list_users_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет доступа к этой команде.")
        return
    users = list_users()
    if not users:
        await message.answer("В базе данных нет пользователей.")
        return

    response_lines = []
    for id, name, age, gender, ph_num, with_kids, problem, latitude, longitude, user_id, first_name, last_name, username, registration_date in users:
        location_str = get_address_from_coords(latitude, longitude)
        formatted_date = format_date(registration_date, "ru")
        response_lines.append(f"""                              
№ {id}. {name}
Дата регистрации: {formatted_date} 
1. Возраст: {age}
2. Пол: {gender}
3. Номер телефона: {ph_num}
4. Дети: {with_kids}
5. Проблема: {problem}
6. username: @{username if username else '-'}
7. Имя и фамилия указанная пользователем в тг: {first_name} {last_name}
8. ID пользователя: {user_id}
9. Локация: {location_str}
10. Локация: широта: {latitude}, долгота: {longitude}

""") 
    await message.answer(f"📋Список пользователей:\n{''.join(response_lines)}")




@router.message(Command("remove_user"))
async def start_remove_user(message: types.Message, state: FSMContext):
    users = list_users()

    if not users:
        await message.answer("В базе данных нет пользователей для удаления.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{user[0]}. {user[1]}", callback_data=f"remove_{user[0]}")]
            for user in users
        ]
    )

    await message.answer("Выберите пользователя для удаления:", reply_markup=kb)


@router.callback_query(lambda query: query.data and query.data.startswith("remove_"))
async def process_remove_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])
    remove_user(user_id)

    data = await state.get_data()
    lang = data.get("lang", "ru")  


    del_resp = (f"✅ Пользователь {user_id} удалён." if lang == "ru" 
                else f"✅ The user: {user_id} was removed." if lang == "en" 
                else f"✅ Der Benutzer: {user_id} wurde entfernt." if lang == "de"  
                else f"✅ Колдонуучу {user_id} жок кылынды.")

    await callback_query.message.edit_text(del_resp)
    await state.clear()   






@router.message(F.text == "🍽️ бесплатное питание")
async def cmd_food_rus(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Пройдите регистрацию, чтобы воспользоваться функциями бота.", reply_markup=keyboard_3)
        return
    await message.answer(
        f"""
1. __Социальный магазин «Хадия»__  
Описание: Магазин, где малоимущие семьи могут бесплатно получить продукты питания и одежду.  
Адрес: Микрорайон «Амир-Тимур», территориальное управление № 9, г. Ош.  
Примечание: Для получения помощи может потребоваться справка от квартального комитета.  
Подробнее на Вести.kg: https://vesti.kg/obshchestvo/item/102644-v-oshe-otkroyut-sotsialnye-magaziny-dlya-maloobespechennykh-sloev-naseleniya.html  
Подробнее на Новости Азии: https://www.news-asia.ru/view/5/10322  

2. __Общественный фонд «Кыргызстан Жаштар Ынтымагы»__  
Описание: Оказывает благотворительную помощь нуждающимся семьям, включая предоставление продуктов питания первой необходимости.  
Адрес: г. Ош (точный адрес не указан).  
Примечание: Фонд активно работает в микрорайонах Кулатов, Анар и Толойкон.  
Подробнее на Медиа Центр: https://media-center.kg/ru/news/Kirgizstan-ZHashtar-Intimagi-okazal-pomoshch-nuzhdayushchimsya-semyam-v-Oshe-foto-920431711  

3. __Общественный фонд «Благодать»__  
Описание: Общественный фонд, предоставляющий помощь нуждающимся.  
Адрес: ул. Ленина, 205, кабинеты 211, 213, 214; 2 этаж, м-н Фрунзе, г. Ош.  
Социальные сети: Instagram: https://www.instagram.com/  

4. __Общественный благотворительный фонд «Сантерра-Юг»__  
Описание: Фонд родителей детей с синдромом Дауна, предоставляющий поддержку и помощь.  
Адрес: ул. Аскар Шакиров, 10/1, г. Ош.  
Веб-сайт: sunterra.kg: https://sunterra.kg/  

5. __Социальные магазины при муниципальных территориальных управлениях__  
Описание: Магазины, где малообеспеченные жители могут приобрести мясную и молочную продукцию по ценам на 10% ниже рыночных.  
Адрес: Во всех семи муниципальных территориальных управлениях города Ош.  
Примечание: Проект реализуется при поддержке мэрии города.  
Подробнее на Вести.kg: https://vesti.kg/obshchestvo/item/102644-v-oshe-otkroyut-sotsialnye-magaziny-dlya-maloobespechennykh-sloev-naseleniya.html  

6. __Ошское городское управление социального фонда__  
Описание: Государственное учреждение, предоставляющее социальную помощь нуждающимся.  
Адрес: ул. Курманжан-Датка, 130, г. Ош.  
Контакты: +996 (3222) 2-28-70.  
"""
    )


@router.message(F.text == "🏠 Бесплатное жилье и хостелы")
async def cmd_house_rus(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Пройдите регистрацию, чтобы воспользоваться функциями бота.", reply_markup=keyboard_3)
        return
    await message.answer(
        f"""
1. __Шелтер при Общественной организации «Мусаада»__  
Описание: Единственное известное убежище для бездомных в Оше, рассчитанное на 15 человек. Создано совместно с мэрией города.  
Адрес: г. Ош (точный адрес не указан).  
Примечание: Предоставляет временное проживание для бездомных.  
Подробнее на interbilimosh.kg: https://www.interbilimosh.kg/a-vy-znali-chto-v-oshe-chislo-bezdomnyh-variruetsya-ot-56-do-70/  

2. __Хостелы с доступными ценами__  
Хотя это не бесплатные приюты, некоторые хостелы в Оше предлагают недорогое проживание, что может быть вариантом для временного ночлега:  
- Wood Hostel: от 297 сом за ночь.  
- Hostel Visit: от 459 сом за ночь.  
- ABS Guest House: от 350 сом за ночь.  
- Sunny Hostel: от 297 сом за ночь.  
- Ocean Hostel: от 297 сом за ночь.  
Смотреть хостелы на hostelz.com: https://www.hostelz.com/hostels/Kyrgyzstan/Osh  

3. __Общественные организации и инициативы__  
Некоторые общественные организации в Оше могут предоставлять помощь нуждающимся, включая временное проживание:  
- Общественный фонд «Благодать»  
  - Адрес: ул. Ленина, 205, кабинеты 211, 213, 214; 2 этаж, м-н Фрунзе, г. Ош.  
  - Социальные сети: Instagram: https://www.instagram.com/  
  - Подробнее на 2ГИС: https://2gis.kg/osh/firm/70000001030680206  

- Общественный фонд «Сантерра-Юг»  
  - Адрес: ул. Аскар Шакиров, 10/1, г. Ош.  
  - Веб-сайт: sunterra.kg: https://sunterra.kg/  
  - Подробнее на 2ГИС: https://2gis.kg/osh/firm/70000001069418449  
"""
    )


@router.message(F.text == "🌸 Помощь женщинам")
async def cmd_help_rus(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Пройдите регистрацию, чтобы воспользоваться функциями бота.", reply_markup=keyboard_3)
        return
    await message.answer(
        f"""
1. __Кризисный центр «Ак-Журок»__  
Описание: Общественное объединение, работающее с 2002 года, предоставляет бесплатную психологическую, юридическую и социальную помощь женщинам и детям, пострадавшим от насилия. В 2009 году открыт шелтер для временного проживания.  
Адрес: г. Ош, ул. Ленина, 205  
Телефон: +996 (3222) 4-59-76  
Электронная почта: kjurok01@gmail.com  
Веб-сайт: crisis-center-osh.org: https://crisis-center-osh.org/  
Социальные сети: Facebook: https://www.facebook.com/akjurokcrisiscenter/?locale=ru_RU, Instagram: https://www.instagram.com/p/CiQTqYhLdih/  

2. __Кризисный центр «Аруулан» при ОО «Аялзат»__  
Описание: Центр оказывает психологическую, юридическую и медицинскую помощь женщинам и девочкам, пострадавшим от семейного насилия.  
Адрес: г. Ош, ул. Ленина, 205  
Телефон: +996 (3222) 5-56-08  
Электронная почта: ayalzat@netmail.kg  
Социальные сети: Instagram: https://www.instagram.com/ayalzat.osh/p/Csv3Fr5Mqdc/  

3. __Общественное объединение «Мээрбан»__  
Описание: Организация предоставляет психологическую и информационную поддержку женщинам, пострадавшим от насилия, а также проводит адвокационные кампании.  
Адрес: г. Ош, ул. Ленина, 312/23  
Телефоны: +996 (3222) 7-40-06, +996 (3222) 7-40-17  
Электронная почта: meerban.osh@mail.ru  
"""
    )
