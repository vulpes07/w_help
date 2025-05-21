import os, sys, math,logging
from contextlib import closing
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from database import init_db, is_registered, add_user, list_users, remove_user
from reply_keyboard import menu_eng, menu, menu_germ, menu_kyrg, keyboard_3_germ
from reply_keyboard import menu_2, menu_2_eng, menu_2_kyrg, menu_2_germ
from reply_keyboard import response_menu, response_menu_eng, response_menu_germ, response_menu_kyrg
from russ import get_address_from_coords
from dotenv import load_dotenv
load_dotenv()



router_germ = Router()

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


KIDS_PROMPTS = {
    "ru": "У вас есть дети?",  
    "kg": "Сизде балдар барбы?",  
    "en": "Do you have children?",  
    "de": "Haben Sie Kinder?"  
}

KIDS_BUTTONS = {
    "ru": {"yes": "Да", "no": "Нет"},
    "kg": {"yes": "Ооба", "no": "Жок"},
    "en": {"yes": "Yes", "no": "No"},
    "de": {"yes": "Ja", "no": "Nein"}
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

class FSMAdminAddGerm(StatesGroup):
    name = State()
    age = State()
    gender = State()
    ph_num = State()
    with_kids = State()
    problem = State()
    latitude = State()
    longitude = State()

class FSMAdminDelGerm(StatesGroup):
    choose_user = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

keyboard_germ = ReplyKeyboardMarkup(
        keyboard=[        
            [KeyboardButton(text="➕ Benutzer hinzufügen")],
            [KeyboardButton(text="📋 Benutzerliste")],
            [KeyboardButton(text="❌ Benutzer entfernen")],
            [KeyboardButton(text="🍽️ Kostenlose Verpflegung")],
            [KeyboardButton(text="🏠 Kostenlose Unterkünfte und Hostels")],
            [KeyboardButton(text="🌸 Hilfe für Frauen")],
    ],
    resize_keyboard = True

    )
keyboard_2_germ = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Admin panel")],
            [KeyboardButton(text="➕ Registrieren")]
        ],
        resize_keyboard=True
    )


@router_germ.message(Command("start_germ"))
async def cmd_start_germ(message: types.Message):

    await message.answer(
            f"""👋 Guten Tag, {message.from_user.first_name}! Wir sind Ihr Support-Team und helfen Ihnen gerne weiter. Sie müssen sich registrieren, bevor Sie diesen Bot nutzen können. Sofern Sie sich bereits registriert haben, drücken Sie /info.

Falls Sie Fragen haben, schreiben Sie an den Bot-Ersteller: @vulpes_07.

Wenn Sie die Sprache ändern möchten, drücken Sie /start

Wählen Sie die Funktion:""",
            reply_markup=keyboard_2_germ
        )

@router_germ.message(Command("admin"))
async def admin_greeting(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Willkommen, Administrator {message.from_user.first_name}!\n"
            "🛠 Alle administrativen Funktionen stehen zur Verfügung:",
            reply_markup=keyboard_germ
        )
    else:
        await message.answer(
            "⛔ Sie haben keinen Zugriff auf diesen Befehl",
            reply_markup=keyboard_2_germ
        )

@router_germ.message(F.text == "🛠 Admin panel")
async def admin_panel_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Sie haben keine Berechtigung für diese Funktion")
        return
    else:
        await message.answer(
            f"👋 Willkommen zurück, Administrator {message.from_user.first_name}!\n"
            "🛠 Alle administrativen Funktionen sind bereit:",
            reply_markup=keyboard_germ)




@router_germ.message(F.text == "➕ Benutzer hinzufügen")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="de") 
    await start_add_user(message, state)

    
@router_germ.message(F.text == "➕ Registrieren")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="de") 
    await start_add_user(message, state)

@router_germ.message(F.text == "📋 Benutzerliste")
async def handle_list_users_button(message: types.Message):
    await list_users_command(message)

@router_germ.message(F.text == "❌ Benutzer entfernen")
async def handle_remove_user_button(message: types.Message, state: FSMContext):
    await start_remove_user(message, state)

@router_germ.message(Command("add_user"))
async def start_add_user(message: types.Message, state: FSMContext):
    await message.answer("Geben Sie Ihren Namen ein:")
    await state.set_state(FSMAdminAddGerm.name)


@router_germ.message(FSMAdminAddGerm.name)
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Geben Sie Ihr aktuelles Alter ein:")
    await state.set_state(FSMAdminAddGerm.age)

@router_germ.message(FSMAdminAddGerm.age)
async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Geben Sie Ihr aktuelles Alter ein.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(FSMAdminAddGerm.gender) 
    await message.answer("Was ist Ihr Geschlecht:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Mann", callback_data="gender_male")],
        [InlineKeyboardButton(text="Frau", callback_data="gender_female")]
    ]))
    await state.set_state(FSMAdminAddGerm.gender)

@router_germ.callback_query(lambda call: call.data.startswith("gender_"))
async def load_gender(callback_query: types.CallbackQuery, state: FSMContext):
    gender = "Mann" if callback_query.data == "gender_male" else "Frau"
    await state.update_data(gender=gender)
    await callback_query.message.answer("Geben Sie Ihre Telefonnummer ein:")
    await state.set_state(FSMAdminAddGerm.ph_num)

@router_germ.message(FSMAdminAddGerm.ph_num)
async def load_ph_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Geben Sie Ihre Telefonnummer ein.")
        return
    await state.update_data(ph_num=int(message.text))
    
    lang = (await state.get_data()).get("lang", "de")
    buttons = KIDS_BUTTONS.get(lang, KIDS_BUTTONS["de"])
    
    await message.answer(KIDS_PROMPTS[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buttons["yes"], callback_data="kids_yes")],
        [InlineKeyboardButton(text=buttons["no"], callback_data="kids_no")]
    ]))
    await state.set_state(FSMAdminAddGerm.with_kids)


@router_germ.callback_query(lambda call: call.data in ["kids_yes", "kids_no"])
async def load_with_kids(callback_query: types.CallbackQuery, state: FSMContext):
    with_kids = "Ja" if callback_query.data == "kids_yes" else "Nein"
    await state.update_data(with_kids=with_kids)
    
    lang = (await state.get_data()).get("lang", "de")
    await callback_query.message.answer(PROBLEM_PROMPTS[lang])
    await state.set_state(FSMAdminAddGerm.problem)



@router_germ.message(FSMAdminAddGerm.problem)
async def load_problem(message: types.Message, state: FSMContext):
    await state.update_data(problem=message.text)

    lang = (await state.get_data()).get("lang", "de")
    await message.answer(f"{message.from_user.full_name}, {LOCATION_PROMPTS[lang]}",  
        reply_markup=menu if lang == "ru" 
        else menu_eng if lang == "en" 
        else menu_germ if lang == "de" 
        else menu_kyrg)

    await state.set_state(FSMAdminAddGerm.latitude)





@router_germ.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    required_fields = ["name", "age", "gender", "ph_num"]
    for field in required_fields:
        if field not in user_data:
            await message.answer(f"ERROR: {field} - Kein vorhandenes Feld. Erneut registrieren.")
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
    lang = (await state.get_data()).get("lang", "de")
    await message.answer(
    SUCCESS_MSGS[lang], 
    reply_markup=menu_2 if lang == "ru" 
    else menu_2_eng if lang == "en" 
    else menu_2_germ if lang == "de" 
    else menu_2_kyrg
    )
    await state.clear()




@router_germ.message(Command("info"))
async def info_command(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "de")
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



@router_germ.message(Command("list_users"))
async def list_users_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Sie haben keinen Zugriff auf diesen Befehl.")
        return
    users = list_users()
    if not users:
        await message.answer("Es gibt keine Benutzer in der Datenbank.")
        return

    response_lines = []
    for id, name, age, gender, ph_num, with_kids, problem, latitude, longitude, user_id, first_name, last_name, username, registration_date in users:
        location_str = get_address_from_coords(latitude, longitude)
        formatted_date = format_date(registration_date, "de")
        response_lines.append(f"""                              
№ {id}. {name}
Registrierungsdatum: {formatted_date} 
1. Alter: {age}
2. Geschlecht: {gender}
3. Telefonnummer: {ph_num}
4. Kinder: {with_kids}
5. Problem: {problem}
6. Benutzername: @{username if username else '-'}
7. Vor- und Nachname in Telegram: {first_name} {last_name}
8. Benutzer-ID: {user_id}
9. Standort: {location_str}
10. Standort: Breite: {latitude}, Länge: {longitude}
""") 
    await message.answer(f"📋Benutzerliste:\n{''.join(response_lines)}")


@router_germ.message(Command("remove_user"))
async def start_remove_user(message: types.Message, state: FSMContext):
    users = list_users()

    if not users:
        await message.answer("Es gibt keinen zu entfernenden Benutzer in der Datenbank.")
        return

    kb_germ = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{user[0]}. {user[1]}", callback_data=f"remove_{user[0]}")]
            for user in users
        ]
    )

    await message.answer("Wählen Sie den zu entfernenden Benutzer aus:", reply_markup=kb_germ)


@router_germ.callback_query(lambda query: query.data and query.data.startswith("remove_"))
async def process_remove_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])
    remove_user(user_id)

    data = await state.get_data()
    lang = data.get("lang", "de")  


    del_resp = (f"✅ Пользователь {user_id} удалён." if lang == "ru" 
                else f"✅ The user: {user_id} was removed." if lang == "en" 
                else f"✅ Der Benutzer: {user_id} wurde entfernt." if lang == "de"  
                else f"✅ Колдонуучу {user_id} жок кылынды.")

    await callback_query.message.edit_text(del_resp)
    await state.clear() 







@router_germ.message(F.text == "🍽️ Kostenlose Verpflegung")
async def cmd_food_de(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Für die Nutzung der Bot-Funktionen ist eine Registrierung erforderlich.", reply_markup=keyboard_3_germ)
        return
    await message.answer(
        f"""
1. __Sozialladen „Chadija“__  
Beschreibung: Ein Laden, in dem bedürftige Familien kostenlos Lebensmittel und Kleidung erhalten können.  
Adresse: Mikrobezirk „Amir-Timur“, Verwaltungsbezirk Nr. 9, Stadt Osch.  
Hinweis: Für die Inanspruchnahme der Hilfe kann eine Bescheinigung des Quartierskomitees erforderlich sein.  
Mehr auf Vesti.kg: https://vesti.kg/obshchestvo/item/102644-v-oshe-otkroyut-sotsialnye-magaziny-dlya-maloobespechennykh-sloev-naseleniya.html  
Mehr auf News Asia: https://www.news-asia.ru/view/5/10322  

2. __Gemeinnütziger Fonds „Kyrgyzstan Zhashstar Yntymagy“__  
Beschreibung: Bietet karitative Hilfe für bedürftige Familien, einschließlich Grundnahrungsmitteln.  
Adresse: Stadt Osch (genaue Adresse nicht angegeben).  
Hinweis: Der Fonds ist in den Mikrobezirken Kulatow, Anar und Toloykon aktiv.  
Mehr auf Media Center: https://media-center.kg/ru/news/Kirgizstan-ZHashtar-Intimagi-okazal-pomoshch-nuzhdayushchimsya-semyam-v-Oshe-foto-920431711  

3. __Gemeinnütziger Fonds „Blagodat“__  
Beschreibung: Hilfsorganisation, die Unterstützung für Bedürftige anbietet.  
Adresse: Lenina-Straße 205, Zimmer 211, 213, 214; 2. Stock, Frunse-Viertel, Stadt Osch.  
Soziale Medien: Instagram: https://www.instagram.com/  

4. __Wohltätigkeitsfonds „Sunterra-Süd“__  
Beschreibung: Fonds für Eltern von Kindern mit Down-Syndrom, bietet Unterstützung und Hilfe.  
Adresse: Askara Shakirov-Straße 10/1, Stadt Osch.  
Webseite: https://sunterra.kg/  

5. __Sozialläden der kommunalen Verwaltungsbezirke__  
Beschreibung: Läden, in denen einkommensschwache Bürger Fleisch- und Milchprodukte zu 10 % unter dem Marktpreis kaufen können.  
Adresse: In allen sieben kommunalen Verwaltungsbezirken der Stadt Osch.  
Hinweis: Das Projekt wird von der Stadtverwaltung unterstützt.  
Mehr auf Vesti.kg: https://vesti.kg/obshchestvo/item/102644-v-oshe-otkroyut-sotsialnye-magaziny-dlya-maloobespechennykh-sloev-naseleniya.html  

6. __Städtische Sozialfondsverwaltung Osch__  
Beschreibung: Staatliche Einrichtung, die Sozialhilfe für Bedürftige bereitstellt.  
Adresse: Kurmandjan-Datka-Straße 130, Stadt Osch.  
Kontakt: +996 (3222) 2-28-70  
"""
    )


@router_germ.message(F.text == "🏠 Kostenlose Unterkünfte und Hostels")
async def cmd_house_de(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Für die Nutzung der Bot-Funktionen ist eine Registrierung erforderlich.", reply_markup=keyboard_3_germ)
        return
    await message.answer(
        f"""
1. __Obdachlosenunterkunft der NGO „Mussada“__  
Beschreibung: Die einzige bekannte Unterkunft für Obdachlose in Osch, Platz für 15 Personen. Wurde in Zusammenarbeit mit der Stadtverwaltung eingerichtet.  
Adresse: Stadt Osch (genaue Adresse nicht angegeben).  
Hinweis: Bietet vorübergehende Unterkunft für Obdachlose.  
Mehr auf interbilimosh.kg: https://www.interbilimosh.kg/a-vy-znali-chto-v-oshe-chislo-bezdomnyh-variruetsya-ot-56-do-70/  

2. __Günstige Hostels__  
Zwar nicht kostenlos, aber einige Hostels in Osch bieten preiswerte Übernachtungsmöglichkeiten:  
- __Wood Hostel__: ab 297 SOM pro Nacht  
- __Hostel Visit__: ab 459 SOM pro Nacht  
- __ABS Guest House__: ab 350 SOM pro Nacht  
- __Sunny Hostel__: ab 297 SOM pro Nacht  
- __Ocean Hostel__: ab 297 SOM pro Nacht  
Hostels auf hostelz.com: https://www.hostelz.com/hostels/Kyrgyzstan/Osh  

3. __Hilfsorganisationen und Initiativen__  
Einige NGOs in Osch bieten möglicherweise vorübergehende Unterkünfte an:  

- __Gemeinnütziger Fonds „Blagodat“__  
  Adresse: Lenina-Straße 205, Zimmer 211, 213, 214; 2. Stock, Frunse-Viertel, Stadt Osch  
  Soziale Medien: Instagram: https://www.instagram.com/  
  Mehr auf 2GIS: https://2gis.kg/osh/firm/70000001030680206  

- __Gemeinnütziger Fonds „Sunterra-Süd“__  
  Adresse: Askara Shakirov-Straße 10/1, Stadt Osch  
  Webseite: https://sunterra.kg/  
  Mehr auf 2GIS: https://2gis.kg/osh/firm/70000001069418449  
"""
    )


@router_germ.message(F.text == "🌸 Hilfe für Frauen")
async def cmd_help_de(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Für die Nutzung der Bot-Funktionen ist eine Registrierung erforderlich.", reply_markup=keyboard_3_germ)
        return
    await message.answer(
        f"""
1. __Krisenzentrum „Ak-Zhurok“__  
Beschreibung: Seit 2002 bietet es kostenlose psychologische, rechtliche und soziale Hilfe für Frauen und Kinder, die Gewalt erfahren haben. 2009 wurde eine Schutzuunterkunft eröffnet.  
Adresse: Lenina-Straße 205, Stadt Osch  
Telefon: +996 (3222) 4-59-76  
E-Mail: kjurok01@gmail.com  
Webseite: https://crisis-center-osh.org/  
Soziale Medien: Facebook: https://www.facebook.com/akjurokcrisiscenter/?locale=ru_RU, Instagram: https://www.instagram.com/p/CiQTqYhLdih/  

2. __Krisenzentrum „Aruulan“ (NGO „Ayalzat“)__  
Beschreibung: Bietet psychologische, rechtliche und medizinische Hilfe für Frauen und Mädchen, die häusliche Gewalt erlebt haben.  
Adresse: Lenina-Straße 205, Stadt Osch  
Telefon: +996 (3222) 5-56-08  
E-Mail: ayalzat@netmail.kg  
Soziale Medien: Instagram: https://www.instagram.com/ayalzat.osh/p/Csv3Fr5Mqdc/  

3. __NGO „Meerban“__  
Beschreibung: Unterstützt gewaltbetroffene Frauen durch psychologische Beratung und Advocacy-Arbeit.  
Adresse: Lenina-Straße 312/23, Stadt Osch  
Telefon: +996 (3222) 7-40-06, +996 (3222) 7-40-17  
E-Mail: meerban.osh@mail.ru  
"""
)
