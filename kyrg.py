import os, sys, math,logging
from contextlib import closing
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from database import init_db, is_registered, add_user, list_users, remove_user
from reply_keyboard import menu_eng, menu, menu_germ, menu_kyrg, keyboard_3_kyrg
from reply_keyboard import response_menu, response_menu_eng, response_menu_germ, response_menu_kyrg
from reply_keyboard import menu_2, menu_2_eng, menu_2_kyrg, menu_2_germ
from russ import get_address_from_coords
from dotenv import load_dotenv
load_dotenv()



router_kyrg = Router()

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

class FSMAdminAddKyrg(StatesGroup):
    name = State()
    age = State()
    gender = State()
    ph_num = State()
    with_kids = State()
    problem = State()
    latitude = State()
    longitude = State()

class FSMAdminDelKyrg(StatesGroup):
    choose_user = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID



keyboard_kyrg = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Колдонуучу кошуу")],
            [KeyboardButton(text="📋 Колдонуучулардын тизмеси")],
            [KeyboardButton(text="❌ Колдонуучуну жок кылуу")],
            [KeyboardButton(text="🍽️ акысыз тамак-аш")],
            [KeyboardButton(text="🏠 Акысыз жашай турган жайлар жана хостелдер")],
            [KeyboardButton(text="🌸 Аялдарга жардам")],
        ],
        resize_keyboard=True
    )
keyboard_2_kyrg = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Админ панель")],
            [KeyboardButton(text="➕ Катталуу")]
        ],
        resize_keyboard=True
    )


@router_kyrg.message(Command("start_kyrg"))
async def cmd_start_kyrg(message: types.Message):

    await message.answer(
            f"""👋 Саламатсызбы, {message.from_user.first_name}! Биздин колдоо кызматы сизге жардам берүүгө даяр. Боттун функцияларын колдонуудан мурун, каттоодон өтүңүз. Ал эми сиз буга чейин катталган болсоңуз, /info басыңыз.

Тилди өзгөртүүнү кааласаңыз, /start баскычын басыңыз            

Бардык кошумча суроолор боюнча боттун жаратуучусуна кайрылыңыз: @vulpes_07.

Функцияны тандаңыз:""",
            reply_markup=keyboard_2_kyrg
        )


@router_kyrg.message(Command("admin"))
async def admin_greeting(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            f"👋 Саламатсызбы, администратор {message.from_user.first_name}!\n"
            "🛠 Сизге бардык административдик функциялар жеткиликтүү:",
            reply_markup=keyboard_kyrg
        )
    else:
        await message.answer(
            "⛔ Бул буйрукка кирүү укугуңуз жок",
            reply_markup=keyboard_2_kyrg
        )

@router_kyrg.message(F.text == "🛠 Админ панель")
async def admin_panel_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Бул функцияга кирүү укугуңуз жок")
        return
    else:
        await message.answer(
            f"👋 Саламатсызбы, администратор {message.from_user.first_name}!\n"
            "🛠 Сизге бардык административдик функциялар жеткиликтүү:",
            reply_markup=keyboard_kyrg)




@router_kyrg.message(F.text == "➕ Колдонуучу кошуу")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="kg")  
    await start_add_user(message, state)

@router_kyrg.message(F.text == "➕ Катталуу")
async def handle_add_user_button(message: types.Message, state: FSMContext):
    await state.update_data(lang="kg")  
    await start_add_user(message, state)

@router_kyrg.message(F.text == "📋 Колдонуучулардын тизмеси")
async def handle_list_users_button(message: types.Message):
    await list_users_command(message)

@router_kyrg.message(F.text == "❌ Колдонуучуну жок кылуу")
async def handle_remove_user_button(message: types.Message, state: FSMContext):
    await start_remove_user(message, state)

@router_kyrg.message(Command("add_user"))
async def start_add_user(message: types.Message, state: FSMContext):
    await message.answer("Атыңызды жазыңыз:")
    await state.set_state(FSMAdminAddKyrg.name)


@router_kyrg.message(FSMAdminAddKyrg.name)
async def load_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Жашынызды жазыңыз:")
    await state.set_state(FSMAdminAddKyrg.age)

@router_kyrg.message(FSMAdminAddKyrg.age)
async def load_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Жашынызды жазыңыз.")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(FSMAdminAddKyrg.gender) 
    await message.answer("Жынысыңызды тандаңыз:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Эркек", callback_data="gender_male")],
        [InlineKeyboardButton(text="Аял", callback_data="gender_female")]
    ]))
    await state.set_state(FSMAdminAddKyrg.gender)

@router_kyrg.callback_query(lambda call: call.data.startswith("gender_"))
async def load_gender(callback_query: types.CallbackQuery, state: FSMContext):
    gender = "Эркек" if callback_query.data == "gender_male" else "Аял"
    await state.update_data(gender=gender)
    await callback_query.message.answer("Телефон номериңизди жазыңыз:")
    await state.set_state(FSMAdminAddKyrg.ph_num)


@router_kyrg.message(FSMAdminAddKyrg.ph_num)
async def load_ph_num(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Телефон номериңизди жазыңыз.")
        return
    await state.update_data(ph_num=int(message.text))
    
    lang = (await state.get_data()).get("lang", "kg")
    buttons = KIDS_BUTTONS.get(lang, KIDS_BUTTONS["kg"])
    
    await message.answer(KIDS_PROMPTS[lang], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=buttons["yes"], callback_data="kids_yes")],
        [InlineKeyboardButton(text=buttons["no"], callback_data="kids_no")]
    ]))
    await state.set_state(FSMAdminAddKyrg.with_kids)


@router_kyrg.callback_query(lambda call: call.data in ["kids_yes", "kids_no"])
async def load_with_kids(callback_query: types.CallbackQuery, state: FSMContext):
    with_kids = "Ооба" if callback_query.data == "kids_yes" else "Жок"
    await state.update_data(with_kids=with_kids)
    
    lang = (await state.get_data()).get("lang", "kg")
    await callback_query.message.answer(PROBLEM_PROMPTS[lang])
    await state.set_state(FSMAdminAddKyrg.problem)



@router_kyrg.message(FSMAdminAddKyrg.problem)
async def load_problem(message: types.Message, state: FSMContext):
    await state.update_data(problem=message.text)

    lang = (await state.get_data()).get("lang", "kg")
    await message.answer(f"{message.from_user.full_name}, {LOCATION_PROMPTS[lang]}",  
        reply_markup=menu if lang == "ru" 
        else menu_eng if lang == "en" 
        else menu_germ if lang == "de" 
        else menu_kyrg)

    await state.set_state(FSMAdminAddKyrg.latitude)



@router_kyrg.message(F.location)
async def location_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    required_fields = ["name", "age", "gender", "ph_num"]
    for field in required_fields:
        if field not in user_data:
            await message.answer(f"Ката кетти: {field} талаасы жок. Каттоону кайра баштоого аракет кылыңыз.")
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

    lang = (await state.get_data()).get("lang", "kg")
    await message.answer(
    SUCCESS_MSGS[lang], 
    reply_markup=menu_2 if lang == "ru" 
    else menu_2_eng if lang == "en" 
    else menu_2_germ if lang == "de" 
    else menu_2_kyrg
    )
    await state.clear()





@router_kyrg.message(Command("info"))
async def info_command(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "kg")
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




@router_kyrg.message(Command("list_users"))
async def list_users_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Сиз бул буйрукка кире албайсыз.")
        return
    users = list_users()
    if not users:
        await message.answer("Маалыматтар базасында колдонуучулар жок.")
        return

    response_lines = []
    for id, name, age, gender, ph_num, with_kids, problem, latitude, longitude, user_id, first_name, last_name, username, registration_date in users:
        location_str = get_address_from_coords(latitude, longitude)
        formatted_date = format_date(registration_date, "kg")
        response_lines.append(f"""                              
№ {id}. {name}
Каттоо күнү: {formatted_date} 
1. Жашы: {age}
2. Жынысы: {gender}
3. Телефон номери: {ph_num}
4. Балдары: {with_kids}
5. Көйгөйү: {problem}
6. Колдонуучу аты: @{username if username else '-'}
7. Telegramдагы аты-жөнү: {first_name} {last_name}
8. Колдонуучу ID: {user_id}
9. Локация: {location_str}
10. Локация: туурасы: {latitude}, узундугу: {longitude}
""") 
    await message.answer(f"📋Колдонуучулардын тизмеси:\n{''.join(response_lines)}")



@router_kyrg.message(Command("remove_user"))
async def start_remove_user(message: types.Message, state: FSMContext):
    users = list_users()

    if not users:
        await message.answer("Маалымат базасында жок кылуу үчүн колдонуучулар жок.")
        return

    kb_kyrg = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{user[0]}. {user[1]}", callback_data=f"remove_{user[0]}")]
            for user in users
        ]
    )

    await message.answer("Жок кылуу үчүн колдонуучуну тандаңыз:", reply_markup=kb_kyrg)


@router_kyrg.callback_query(lambda query: query.data and query.data.startswith("remove_"))
async def process_remove_user(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[1])
    remove_user(user_id)

    data = await state.get_data()
    lang = data.get("lang", "kg") 


    del_resp = (f"✅ Пользователь {user_id} удалён." if lang == "ru" 
                else f"✅ The user: {user_id} was removed." if lang == "en" 
                else f"✅ Der Benutzer: {user_id} wurde entfernt." if lang == "de"  
                else f"✅ Колдонуучу {user_id} жок кылынды.")

    await callback_query.message.edit_text(del_resp)
    await state.clear() 












@router_kyrg.message(F.text == "🍽️ акысыз тамак-аш")
async def cmd_food_kg(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Боттун мүмкүнчүлүктөрүн пайдалануу үчүн катталыңыз.", reply_markup=keyboard_3_kyrg)
        return
    await message.answer(
        f"""
1. __«Хадия» коомдук дүкөнү__  
Сүрөттөмө: Жакыр үй-бүлөлөр акысыз тамак-аш жана кийим ала алышат.  
Дарек: «Амир-Тимур» микрорайону, №9 аймактык башкармалык, Ош шаары.  
Эскертүү: Жардам алуу үчүн квартал комитетинен справка керек болушу мүмкүн.  
Кененирээк: https://vesti.kg/obshchestvo/item/102644-v-oshe-otkroyut-sotsialnye-magaziny-dlya-maloobespechennykh-sloev-naseleniya.html  
Кененирээк: https://www.news-asia.ru/view/5/10322  

2. __«Кыргызстан Жаштар Ынтымагы» коомдук фонду__  
Сүрөттөмө: Жардамга муктаж үй-бүлөлөргө тамак-аштын негизги өнүмдөрүн бөлүштүрөт.  
Дарек: Ош шаары (так дареги көрсөтүлгөн эмес).  
Эскертүү: Кулатов, Анар жана Толойкон микрорайондорунда иштейт.  
Кененирээк: https://media-center.kg/ru/news/Kirgizstan-ZHashtar-Intimagi-okazal-pomoshch-nuzhdayushchimsya-semyam-v-Oshe-foto-920431711  

3. __«Благодать» коомдук фонду__  
Сүрөттөмө: Жардамга муктаж адамдарга колдоң көрсөтөт.  
Дарек: Ленин көч., 205, 211, 213, 214 бөлмөлөр; 2-кабат, Фрунзе м-н, Ош шаары.  
Instagram: https://www.instagram.com/  

4. __«Сантерра-Юг» коомдук кайрымдуулук фонду__  
Сүрөттөмө: Даун синдрому бар балдардын ата-энелеринин фонду, жардам көрсөтөт.  
Дарек: Аскар Шакиров көч., 10/1, Ош шаары.  
Вебсайт: https://sunterra.kg/  

5. __Аймактык башкармалыктардын коомдук дүкөндөрү__  
Сүрөттөмө: Жакыр адамдар эт жана сүт өнүмдөрүн базардык баадан 10% арзандык менен сатып алышат.  
Дарек: Ош шаарындагы жети аймактык башкармалыктарда.  
Эскертүү: Шаардын мэриясы колдоого алат.  
Кененирээк: https://vesti.kg/obshchestvo/item/102644-v-oshe-otkroyut-sotsialnye-magaziny-dlya-maloobespechennykh-sloev-naseleniya.html  

6. __Ош шаардык социалдык фонд башкармалыгы__  
Сүрөттөмө: Мамлекеттик мекеме, жардамга муктаж адамдарга социалдык колдоң көрсөтөт.  
Дарек: Курманжан-Датка көч., 130, Ош шаары.  
Байланыш: +996 (3222) 2-28-70  
"""
    )


@router_kyrg.message(F.text == "🏠 Акысыз жашай турган жайлар жана хостелдер")
async def cmd_house_kg(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Боттун мүмкүнчүлүктөрүн пайдалануу үчүн катталыңыз.", reply_markup=keyboard_3_kyrg)
        return
    await message.answer(
        f"""
1. __«Мусаада» коомдук уюмунун шелтери__  
Сүрөттөмө: Ошто үйдөн жок адамдар үчүн жалгыз белгилүү панакана, 15 адамга ылайыкталган. Шаардык мэрия менен бирге түзүлгөн.  
Дарек: Ош шаары (так дареги көрсөтүлгөн эмес).  
Эскертүү: Убактылуу жашоо мүмкүнчүлүгүн камсыз кылат.  
Кененирээк: https://www.interbilimosh.kg/a-vy-znali-chto-v-oshe-chislo-bezdomnyh-variruetsya-ot-56-do-70/  

2. __Арзан хостелдер__  
Бул акысыз эмес, бирок Ошто кээ бир хостелдер арзан баа менен убактылуу туруш үчүн ылайыктуу болушу мүмкүн:  
- __Wood Hostel__: бир түнү 297 сомдон  
- __Hostel Visit__: бир түнү 459 сомдон  
- __ABS Guest House__: бир түнү 350 сомдон  
- __Sunny Hostel__: бир түнү 297 сомдон  
- __Ocean Hostel__: бир түнү 297 сомдон  
Хостелдер: https://www.hostelz.com/hostels/Kyrgyzstan/Osh  

3. __Коомдук уюмдар жана демилгелер__  
Ошто кээ бир уюмдар убактылуу жашоо мүмкүнчүлүгүн камсыз кылышы мүмкүн:  
- __«Благодать» коомдук фонду__  
  - Дарек: Ленин көч., 205, 211, 213, 214 бөлмөлөр; 2-кабат, Фрунзе м-н, Ош  
  - Instagram: https://www.instagram.com/  
  - Кененирээк: https://2gis.kg/osh/firm/70000001030680206  

- __«Сантерра-Юг» коомдук фонду__  
  - Дарек: Аскар Шакиров көч., 10/1, Ош  
  - Вебсайт: https://sunterra.kg/  
  - Кененирээк: https://2gis.kg/osh/firm/70000001069418449  
"""
    )


@router_kyrg.message(F.text == "🌸 Аялдарга жардам")
async def cmd_help_kg(message: types.Message):
    if not (is_admin(message.from_user.id) or is_registered(message.from_user.id)):
        await message.answer("Боттун мүмкүнчүлүктөрүн пайдалануу үчүн катталыңыз.", reply_markup=keyboard_3_kyrg)
        return
    await message.answer(
        f"""
1. __«Ак-Журок» кризистик борбору__  
Сүрөттөмө: 2002-жылдан бери иштеп келет, зордук-зомбулуктан жапа чеккен аялдарга жана балдарга акысыз психологиялык, юридикалык жана социалдык жардам көрсөтөт. 2009-жылы убактылуу жашоо үчүн шелтер ачылган.  
Дарек: Ош, Ленин көч., 205  
Телефон: +996 (3222) 4-59-76  
Электрондук почта: kjurok01@gmail.com  
Вебсайт: https://crisis-center-osh.org/  
Facebook: https://www.facebook.com/akjurokcrisiscenter/?locale=ru_RU  
Instagram: https://www.instagram.com/p/CiQTqYhLdih/  

2. __«Аруулан» кризистик борбору (ОО «Аялзат»)__  
Сүрөттөмө: Үй-бүлөлүк зордук-зомбулуктан жапа чеккен аялдарга психологиялык, юридикалык жана медициналык жардам көрсөтөт.  
Дарек: Ош, Ленин көч., 205  
Телефон: +996 (3222) 5-56-08  
Электрондук почта: ayalzat@netmail.kg  
Instagram: https://www.instagram.com/ayalzat.osh/p/Csv3Fr5Mqdc/  

3. __«Мээрбан» коомдук бирикмеси__  
Сүрөттөмө: Зордук-зомбулуктан жапа чеккен аялдарга психологиялык жана маалыматтык колдоң көрсөтөт, ошондой эле адвокациялык иштерди жүргүзөт.  
Дарек: Ош, Ленин көч., 312/23  
Телефондор: +996 (3222) 7-40-06, +996 (3222) 7-40-17  
Электрондук почта: meerban.osh@mail.ru  
"""
    )
