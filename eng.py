import os, sys, math,logging
from contextlib import closing
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from database import init_db, is_registered, add_user, list_users, remove_user
from reply_keyboard import menu_eng, menu, menu_germ, menu_kyrg, keyboard_3_eng
from reply_keyboard import response_menu, response_menu_eng, response_menu_germ, response_menu_kyrg
from reply_keyboard import menu_2, menu_2_eng, menu_2_kyrg, menu_2_germ
from russ import get_address_from_coords
from dotenv import load_dotenv
load_dotenv()




router_eng = Router()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  
if not BOT_TOKEN or not ADMIN_ID:
    sys.exit("Error: BOT_TOKEN or ADMIN_ID environment variable not set.")

DB_PATH = "bot_db.sqlite3"

init_db()

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




def haversine(lat1, lon1, lat2, lon2):
    R = 6371  
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lat2 - lon2)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class FSMAdminAddEng(StatesGroup):
    name = State()
    age = State()
    gender = State()
    ph_num = State()
    with_kids = State()
    problem = State()
    latitude = State()
    longitude = State()

class FSMAdminDelEng(StatesGroup):
    choose_user = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID



keyboard_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Add users")],
            [KeyboardButton(text="📋 List of the users")],
            [KeyboardButton(text="❌ Remove the user")],
            [KeyboardButton(text="🍽️ Free meals and food")],
            [KeyboardButton(text="🏠 Free housing and hostels")],
            [KeyboardButton(text="🌸 Support for women")],
        ],
        resize_keyboard=True
    )
keyboard_2_eng = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin Panel")],
            [KeyboardButton(text="➕ Register")]
        ],
        resize_keyboard=True
    )
    


@router_eng.message(Command("start_eng"))
async def cmd_start_eng(message: types.Message):

    await message.answer(
            f"""👋 Hello, {message.from_user.first_name}! Our support team is here to help you. You have to register before you use this bot. Provided by you have already registered, press /info.

In case you have some questions, write to the bot creator: @vulpes_07.

If you want to change the language, press /start

Choose the function:""",
            reply_markup=keyboard_2_eng
        )

@router_eng.message(Command("admin"))
async def admin_greeting(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Welcome, Administrator {message.from_user.first_name}!\n"
            "🛠 All administrative functions are available:",
            reply_markup=keyboard_eng
        )
    else:
        await message.answer(
            "⛔ You don't have access to this command",
            reply_markup=keyboard_2_eng
        )

@router_eng.message(F.text == "🛠 Admin Panel")
async def admin_panel_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ You don't have permission to access this feature")
        return
    else:
        await message.answer(
            f"👋 Welcome back, Administrator {message.from_user.first_name}!\n"
            "🛠 All administrative functions are ready:",
            reply_markup=keyboard_eng)



@router_eng.message(F.text == "➕ Add users")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="en") 
    await start_add_user(message, state)


@router_eng.message(F.text == "➕ Register")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="en") 
    await start_add_user(message, state)

@router_eng.message(F.text == "📋 List of the users")
async def handle_list_users_button(message: types.Message):
    await list_users_command(message)

@router_eng.message(F.text == "❌ Remove the user")
async def handle_remove_user_button(message: types.Message, state: FSMContext):
    await start_remove_user(message, state)

@router_eng.message(Command("add_user"))
async def start_add_user(message: types.Message, state: FSMContext):
    await message.answer("Enter your name: ")
    await state.set_state(FSMAdminAddEng.name)


@router_eng.message(FSMAdminAddEng.name)
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Enter your current age:")
    await state.set_state(FSMAdminAddEng.age)

@router_eng.message(FSMAdminAddEng.age)
async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Enter your current age.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(FSMAdminAddEng.gender) 
    await message.answer("What's your gender:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Male", callback_data="gender_male")],
        [InlineKeyboardButton(text="Female", callback_data="gender_female")]
    ]))
    await state.set_state(FSMAdminAddEng.gender)

@router_eng.callback_query(lambda call: call.data.startswith("gender_"))
async def load_gender(callback_query: types.CallbackQuery, state: FSMContext):
    gender = "Male" if callback_query.data == "gender_male" else "Female"
    await state.update_data(gender=gender)
    await callback_query.message.answer("Enter your phone number:")
    await state.set_state(FSMAdminAddEng.ph_num)


@router_eng.message(FSMAdminAddEng.ph_num)
async def load_ph_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Enter your phone number.")
        return
    await state.update_data(ph_num=int(message.text))
    
    lang = (await state.get_data()).get("lang", "en")
    buttons = KIDS_BUTTONS.get(lang, KIDS_BUTTONS["en"])
    
    await message.answer(KIDS_PROMPTS[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buttons["yes"], callback_data="kids_yes")],
        [InlineKeyboardButton(text=buttons["no"], callback_data="kids_no")]
    ]))
    await state.set_state(FSMAdminAddEng.with_kids)


@router_eng.callback_query(lambda call: call.data in ["kids_yes", "kids_no"])
async def load_with_kids(callback_query: types.CallbackQuery, state: FSMContext):
    with_kids = "Yes" if callback_query.data == "kids_yes" else "No"
    await state.update_data(with_kids=with_kids)
    
    lang = (await state.get_data()).get("lang", "en")
    await callback_query.message.answer(PROBLEM_PROMPTS[lang])
    await state.set_state(FSMAdminAddEng.problem)



@router_eng.message(FSMAdminAddEng.problem)
async def load_problem(message: types.Message, state: FSMContext):
    await state.update_data(problem=message.text)

    lang = (await state.get_data()).get("lang", "en")
    await message.answer(f"{message.from_user.full_name}, {LOCATION_PROMPTS[lang]}",  
        reply_markup=menu if lang == "ru" 
        else menu_eng if lang == "en" 
        else menu_germ if lang == "de" 
        else menu_kyrg)

    await state.set_state(FSMAdminAddEng.latitude)




@router_eng.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    required_fields = ["name", "age", "gender", "ph_num"]
    for field in required_fields:
        if field not in user_data:
            await message.answer(f"ERROR: {field} - no existing field. Register again.")
            await state.clear()  
            return

    
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

    SUCCESS_MSGS = {
    "ru": "Ваши данные успешно добавлены! Спасибо за регистрацию, можете воспользоваться функциями бота",
    "en": "The data has been saved successfully! Thank you for the registration, now you can use bot functions",
    "de": "Die Daten wurden erfolgreich gespeichert! Vielen Dank für die Registrierung, jetzt können Sie die Bot-Funktionen nutzen",
    "kg": "Дайындарыңыз ийгиликтүү кошулду! Каттоодон өткөнүңүз үчүн рахмат, боттун мүмкүнчүлүктөрүн колдоно аласыз"
    }
    lang = (await state.get_data()).get("lang", "en")
    await message.answer(
    SUCCESS_MSGS[lang], 
    reply_markup=menu_2 if lang == "ru" 
    else menu_2_eng if lang == "en" 
    else menu_2_germ if lang == "de" 
    else menu_2_kyrg
    )
    await state.clear()





@router_eng.message(Command("info"))
async def info_command(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "en")
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




@router_eng.message(Command("list_users"))
async def list_users_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("You do not have access to this command.")
        return
    users = list_users()
    if not users:
        await message.answer("There are no users in the database.")
        return

    response_lines = []
    for id, name, age, gender, ph_num, with_kids, problem, latitude, longitude, user_id, first_name, last_name, username, registration_date in users:
        location_str = get_address_from_coords(latitude, longitude)
        formatted_date = format_date(registration_date, "en")
        response_lines.append(f"""                              
№ {id}. {name}
Registration date: {formatted_date}      
1. Age: {age}
2. Gender: {gender}
3. Phone number: {ph_num}
4. Children: {with_kids}
5. Problem: {problem}
6. Username: @{username if username else '-'}
7. Full name in Telegram: {first_name} {last_name}
8. User ID: {user_id}
9. Location: {location_str}
10. Location: latitude: {latitude}, longitude: {longitude}
""") 
    await message.answer(f"📋List of users:\n{''.join(response_lines)}")



@router_eng.message(Command("remove_user"))
async def start_remove_user(message: types.Message, state: FSMContext):
    users = list_users()

    if not users:
        await message.answer("There is no user in data base to remove.")
        return

    kb_eng = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{user[0]}. {user[1]}", callback_data=f"remove_{user[0]}")]
            for user in users
        ]
    )

    await message.answer("Choose the user to remove:", reply_markup=kb_eng)


@router_eng.callback_query(lambda query: query.data and query.data.startswith("remove_"))
async def process_remove_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])
    remove_user(user_id)

    data = await state.get_data()
    lang = data.get("lang", "en")  


    del_resp = (f"✅ Пользователь {user_id} удалён." if lang == "ru" 
                else f"✅ The user: {user_id} was removed." if lang == "en" 
                else f"✅ Der Benutzer: {user_id} wurde entfernt." if lang == "de"  
                else f"✅ Колдонуучу {user_id} жок кылынды.")

    await callback_query.message.edit_text(del_resp)
    await state.clear() 




@router_eng.message(F.text == "🍽️ Free meals and food")
async def cmd_food_en(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("You have to register for the purpose of using bot functions.", reply_markup=keyboard_3_eng)
        return
    await message.answer(
        f"""
1. **Social Store "Khadija"**  
Description: A store where low-income families can receive free food and clothing.  
Address: Microdistrict "Amir-Timur", Territorial Administration No. 9, Osh City.  
Note: A certificate from the local neighborhood committee may be required to receive assistance.  
[More on Vesti.kg](https://vesti.kg/obshchestvo/item/102644-v-oshe-otkroyut-sotsialnye-magaziny-dlya-maloobespechennykh-sloev-naseleniya.html)  
[More on News Asia](https://www.news-asia.ru/view/5/10322)  

2. **Public Foundation "Kyrgyzstan Zhashstar Yntymagy"**  
Description: Provides charitable assistance to needy families, including essential food items.  
Address: Osh City (exact address not specified).  
Note: The foundation actively works in the Kulatov, Anar, and Toloykon microdistricts.  
[More on Media Center](https://media-center.kg/ru/news/Kirgizstan-ZHashtar-Intimagi-okazal-pomoshch-nuzhdayushchimsya-semyam-v-Oshe-foto-920431711)  

3. **Public Foundation "Blagodat"**  
Description: A community foundation providing assistance to those in need.  
Address: 205 Lenin St., Rooms 211, 213, 214; 2nd Floor, Frunze District, Osh City.  
Social Media: [Instagram](https://www.instagram.com/).  

4. **Charitable Foundation "Sunterra-South"**  
Description: A foundation for parents of children with Down syndrome, offering support and aid.  
Address: 10/1 Askara Shakirov St., Osh City.  
Website: [sunterra.kg](https://sunterra.kg/).  

5. **Social Stores at Municipal Territorial Administrations**  
Description: Stores where low-income residents can purchase meat and dairy products at 10% below market prices.  
Address: Across all seven municipal territorial administrations in Osh City.  
Note: The project is implemented with support from the city mayor’s office.  
[More on Vesti.kg](https://vesti.kg/obshchestvo/item/102644-v-oshe-otkroyut-sotsialnye-magaziny-dlya-maloobespechennykh-sloev-naseleniya.html)  

6. **Osh City Social Fund Administration**  
Description: A government agency providing social assistance to those in need.  
Address: 130 Kurmanjan Datka St., Osh City.  
Contact: +996 (3222) 2-28-70.  
"""
    )


@router_eng.message(F.text == "🏠 Free housing and hostels")
async def cmd_house_en(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("You have to register for the purpose of using bot functions.", reply_markup=keyboard_3_eng)
        return
    await message.answer(
        f"""
1. **Shelter by NGO "Mussada"**  
Description: The only known shelter for homeless people in Osh, accommodating up to 15 individuals. Established in collaboration with the city mayor’s office.  
Address: Osh City (exact address not specified).  
Note: Provides temporary housing for the homeless.  
[More on interbilimosh.kg](https://www.interbilimosh.kg/a-vy-znali-chto-v-oshe-chislo-bezdomnyh-variruetsya-ot-56-do-70/)  

2. **Budget Hostels**  
While not free, some hostels in Osh offer affordable accommodation:  
- **Wood Hostel**: from 297 KGS/night.  
- **Hostel Visit**: from 459 KGS/night.  
- **ABS Guest House**: from 350 KGS/night.  
- **Sunny Hostel**: from 297 KGS/night.  
- **Ocean Hostel**: from 297 KGS/night.  
[View hostels on hostelz.com](https://www.hostelz.com/hostels/Kyrgyzstan/Osh)  

3. **NGOs and Initiatives**  
Some NGOs in Osh may provide temporary housing assistance:  
- **Public Foundation "Blagodat"**  
  - Address: 205 Lenin St., Rooms 211, 213, 214; 2nd Floor, Frunze District, Osh City.  
  - Social Media: [Instagram](https://www.instagram.com/)  
  - [More on 2GIS](https://2gis.kg/osh/firm/70000001030680206)  

- **Charitable Foundation "Sunterra-South"**  
  - Address: 10/1 Askara Shakirov St., Osh City.  
  - Website: [sunterra.kg](https://sunterra.kg/)  
  - [More on 2GIS](https://2gis.kg/osh/firm/70000001069418449)  
"""
    )


@router_eng.message(F.text == "🌸 Support for women")
async def cmd_help_en(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("You have to register for the purpose of using bot functions.", reply_markup=keyboard_3_eng)
        return
    await message.answer(
        f"""
1. **Crisis Center "Ak-Zhurok"**  
Description: Operating since 2002, it provides free psychological, legal, and social support to women and children affected by violence. A shelter was opened in 2009.  
Address: 205 Lenin St., Osh City.  
Phone: +996 (3222) 4-59-76  
Email: kjurok01@gmail.com  
Website: [crisis-center-osh.org](https://crisis-center-osh.org/)  
Social Media: [Facebook](https://www.facebook.com/akjurokcrisiscenter/?locale=ru_RU), [Instagram](https://www.instagram.com/p/CiQTqYhLdih/)  

2. **Crisis Center "Aruulan" (NGO "Ayalzat")**  
Description: Offers psychological, legal, and medical aid to women and girls affected by domestic violence.  
Address: 205 Lenin St., Osh City.  
Phone: +996 (3222) 5-56-08  
Email: ayalzat@netmail.kg  
Social Media: [Instagram](https://www.instagram.com/ayalzat.osh/p/Csv3Fr5Mqdc/)  

3. **NGO "Meerban"**  
Description: Provides psychological support and advocacy for women affected by violence.  
Address: 312/23 Lenin St., Osh City.  
Phone: +996 (3222) 7-40-06, +996 (3222) 7-40-17  
Email: meerban.osh@mail.ru  
"""
    )