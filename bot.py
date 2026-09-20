import telebot
from telebot import types
from telebot.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
import json
import os
import time
import logging
from datetime import datetime

# ====================== ЛОГИРОВАНИЕ ======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

def log_user_action(user, action, extra=""):
    """Корректный лог: имя + @username + ID + действие"""
    username = f"@{user.username}" if user.username else "без username"
    name = (user.first_name or "") + (f" {user.last_name}" if user.last_name else "")
    name = name.strip() or "Без имени"
    line = f"👤 {name} ({username}) | ID: {user.id} | {action}"
    if extra:
        line += f" | {extra}"
    logger.info(line)
    if user.id != ADMIN_ID:
        try:
            bot.send_message(ADMIN_ID, line)
        except Exception as e:
            logger.warning(f"Не удалось отправить лог админу: {e}")

# ====================== НАСТРОЙКИ ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Переменная окружения BOT_TOKEN не задана! Установите её в Railway → Variables")
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

ADMIN_ID = 8588778253

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

WELCOME_IMAGE = 'https://ibb.co/JFCdJG15'

MODELS_FILE = 'models.json'
FAVORITES_FILE = 'favorites.json'
USERS_FILE = 'users.json'
PROMO_FILE = 'promocodes.json'
BLOCKED_FILE = 'blocked.json'

# Дефолтное описание модели
DEFAULT_DESCRIPTION = (
    "Страстная и утончённая красотка, которая знает, чего хочет. "
    "Мягкий голос, горячий взгляд и тело, от которого перехватывает дыхание. "
    "Умеет быть нежной и крайне развязной — всё зависит от твоего настроения. "
    "С ней время останавливается, а после встречи хочется вернуться снова."
)

# ====================== КАСТОМНЫЕ ЭМОДЗИ (пак hythohty) ======================
# ID из https://t.me/addemoji/hythohty
EMOJI = {
    "msg_check":     "5330532504325627349",  # сообщение + галочка
    "msg_stack":     "5330250986399244468",  # сообщение поверх другого
    "refresh":       "5330371455936925090",  # 🔄
    "wave":          "5327998881642878671",  # 👋
    "pen":           "5327814949668426911",  # 🖊
    "heart":         "5328012045717646006",  # ❤️
    "phone":         "5330234317631164422",  # 📞
    "exclaim":       "5330240665592827101",  # ❗️
    "adult":         "5330149960178506226",  # 🔞
    "plus":          "5330266559950656963",  # ➕
    "cross":         "5330348928833460746",  # ❌
    "check":         "5328253964045556790",  # ✅
    "link":          "5330454576439009903",  # 🔗
    "search":        "5328279055244499146",  # 🔍
    "money_fly":     "5330396018854893885",  # 💸
    "lock":          "5328091876274773724",  # 🔒
    "camera":        "5330190676468471215",  # 📷
    "news":          "5330561263426640654",  # 📰
    "book":          "5330167024083571618",  # 📖
    "wallet":        "5330259494729455410",  # 👛
    "timer":         "5330410896621611681",  # ⏱️
    "bot":           "5330181395044147028",  # 🤖
    "camera2":       "5327873614626726321",  # 📷
    "star":          "5328098116862251040",  # ⭐️
    "user":          "5328202759445452024",  # 👤
    "users":         "5328010804472092077",  # 👥
    "card":          "5330377305682385409",  # 💳
    "home":          "5330515552089707798",  # 🏠
    "idea":          "5327784348026443840",  # 💡
    "settings":      "5330499609171105603",  # ⚙️
    "moon":          "5330161333251904418",  # 🌙
    "grid":          "5327932155030966631",  # ⚙️ 4 квадратика
    "money_fly2":    "5328013836719002683",  # 💸
    "party":         "5330454434705084292",  # 🎉
    "arrow_right":   "5330378435258785686",  # ➡️
    "arrow_left":    "5330288730571839538",  # ⬅️
    "chart":         "5327906453946688703",  # 📊
    "sparkles":      "5330217885086292561",  # ✨
    "kiss":          "5328055888743798817",  # 💋
    "butterfly":     "5328049317443836138",  # 🦋
    "dance":         "5328222305841614729",  # 💃
}

# ====================== ЗАГРУЗКА / СОХРАНЕНИЕ ======================
def load_json(filename, default=None):
    if default is None:
        default = {}
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Ошибка при загрузке {filename}: {e}")
    return default

def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении {filename}: {e}")

def load_models():
    data = load_json(MODELS_FILE, None)
    if data is None:
        return {
            "65103": {
                "photos": ["https://picsum.photos/600/800"],
                "name": "Алина",
                "city": "Москва",
                "contact": "Москва",
                "text": (
                    "✨ **АНКЕТА МОДЕЛИ #65103** ✨\n\n"
                    "👤 **Имя:** Алина\n"
                    "📍 **Город:** Москва\n\n"
                    "💸 **Прайс:**\n"
                    "├ 1 час 4.500₽\n"
                    "├ 3 часа 9.000₽\n"
                    "└ Ночь 17.000₽\n\n"
                    "🔥 **Допы:**\n"
                    "├ МБР — 3.500₽\n"
                    "├ МЖМ — 4.500₽\n"
                    "├ АНАЛ — 1.500₽\n"
                    "├ Массаж — 1.000₽\n"
                    "└ Стриптиз — 2.500₽\n\n"
                    "🔍 **Описание:**\n"
                    + DEFAULT_DESCRIPTION
                ),
                "services": "Секс классический, Секс анальный, Секс групповой, Минет без резинки, Минет глубокий"
            }
        }
    # Миграция старого формата photo → photos
    for code, m in data.items():
        if "photo" in m and "photos" not in m:
            m["photos"] = [m["photo"]]
            del m["photo"]
        elif "photos" not in m:
            m["photos"] = ["https://picsum.photos/600/800"]
    return data

def save_models():
    save_json(MODELS_FILE, models_db)

def load_favorites():
    return load_json(FAVORITES_FILE, {})

def save_favorites():
    save_json(FAVORITES_FILE, favorites_db)

def load_users():
    return load_json(USERS_FILE, {})

def save_users():
    save_json(USERS_FILE, users_db)

def load_promos():
    return load_json(PROMO_FILE, {})

def save_promos():
    save_json(PROMO_FILE, promos_db)

def load_blocked():
    return set(load_json(BLOCKED_FILE, []))

def save_blocked():
    save_json(BLOCKED_FILE, list(blocked_users))

models_db = load_models()
favorites_db = load_favorites()
users_db = load_users()
promos_db = load_promos()
blocked_users = load_blocked()
temp_model_creation = {}
temp_promo_creation = {}
temp_balance_edit = {}

logger.info(f"Загружено моделей: {len(models_db)}")
logger.info(f"Загружено пользователей: {len(users_db)}")
logger.info(f"Загружено промокодов: {len(promos_db)}")
logger.info(f"Заблокировано: {len(blocked_users)}")

# ====================== ПОЛЬЗОВАТЕЛИ ======================
def ensure_user(user):
    """Создаёт/обновляет запись пользователя"""
    uid = str(user.id)
    if uid not in users_db:
        users_db[uid] = {
            "id": user.id,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "balance": 0,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "actions": 0,
            "last_action": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_users()
    else:
        # Обновляем имя/username на актуальные
        users_db[uid]["username"] = user.username or users_db[uid].get("username", "")
        users_db[uid]["first_name"] = user.first_name or users_db[uid].get("first_name", "")
        users_db[uid]["last_name"] = user.last_name or users_db[uid].get("last_name", "")
        users_db[uid]["last_action"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        users_db[uid]["actions"] = users_db[uid].get("actions", 0) + 1
        save_users()
    return users_db[uid]

def is_blocked(user_id):
    return str(user_id) in blocked_users or user_id in blocked_users

def get_balance(user_id):
    uid = str(user_id)
    if uid in users_db:
        return users_db[uid].get("balance", 0)
    return 0

# ====================== КОМАНДЫ ======================
def set_default_commands():
    default_commands = [
        BotCommand("start", "🚀 Запустить / В главное меню"),
        BotCommand("menu", "🏠 Главное меню"),
        BotCommand("help", "❓ Помощь / Поддержка"),
        BotCommand("balance", "💰 Баланс"),
    ]
    bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())

    admin_commands = default_commands + [
        BotCommand("worker", "⚙️ Панель воркера")
    ]
    try:
        bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=ADMIN_ID))
    except Exception as e:
        logger.warning(f"Не удалось установить команды для админа: {e}")

# ====================== КЛАВИАТУРЫ ======================
def get_model_keyboard(code):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_order = types.InlineKeyboardButton("💃 Оформить", callback_data=f"order_model_{code}")
    btn_photo = types.InlineKeyboardButton("📷 Другое фото", callback_data=f"photo_{code}")
    btn_full_photo = types.InlineKeyboardButton("🔞 Фото", callback_data=f"photo_{code}")
    btn_video = types.InlineKeyboardButton("🔞 Видео", callback_data=f"video_{code}")
    btn_private = types.InlineKeyboardButton("🔒 Приватка", callback_data=f"private_{code}")
    btn_fav = types.InlineKeyboardButton("⭐️ В избранные", callback_data=f"fav_{code}")
    btn_reviews = types.InlineKeyboardButton("💬 Отзывы", url="https://t.me/ls_reviews")
    btn_services = types.InlineKeyboardButton("💋 Услуги", callback_data=f"services_{code}")
    btn_back = types.InlineKeyboardButton("🏠 Назад", callback_data="main_menu")

    markup.add(btn_order, btn_photo)
    markup.add(btn_full_photo, btn_video)
    markup.add(btn_private, btn_fav)
    markup.add(btn_reviews, btn_services)
    markup.add(btn_back)
    return markup

def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💃 Оформить модель", callback_data="order"),
        types.InlineKeyboardButton("💸 Баланс", callback_data="balance"),
        types.InlineKeyboardButton("💳 Ввести промокод", callback_data="enter_promo"),
        types.InlineKeyboardButton("⭐️ Мои избранные", callback_data="my_favorites"),
        types.InlineKeyboardButton("✨ О проекте LuxuryMuse", callback_data="about"),
        types.InlineKeyboardButton("💋 Наши услуги", callback_data="services"),
        types.InlineKeyboardButton("📞 Связаться с нами / Поддержка", callback_data="contact")
    )
    return markup

def get_back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu"))
    return markup

def get_worker_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ Создать анкету", callback_data="w_create_model"),
        types.InlineKeyboardButton("📋 Список всех моделей", callback_data="w_list_models"),
        types.InlineKeyboardButton("❌ Удалить анкету", callback_data="w_delete_model"),
        types.InlineKeyboardButton("💳 Создать промокод", callback_data="w_create_promo"),
        types.InlineKeyboardButton("🖊 Изменить промокод", callback_data="w_edit_promo"),
        types.InlineKeyboardButton("👥 Пользователи / Логи", callback_data="w_users"),
        types.InlineKeyboardButton("🔒 Заблокировать пользователя", callback_data="w_block_user"),
        types.InlineKeyboardButton("✅ Разблокировать пользователя", callback_data="w_unblock_user"),
        types.InlineKeyboardButton("📊 Статистика бота", callback_data="w_stats")
    )
    return markup

# ====================== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ======================
def send_or_edit_photo(chat_id, message_id, caption, reply_markup, photo=WELCOME_IMAGE):
    try:
        bot.edit_message_media(
            media=types.InputMediaPhoto(photo, caption=caption, parse_mode="Markdown"),
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup
        )
    except Exception:
        try:
            bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception:
            bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup, parse_mode="Markdown")

def check_blocked(message_or_call):
    """Проверка блокировки. Возвращает True если заблокирован."""
    user = message_or_call.from_user
    if is_blocked(user.id):
        try:
            if hasattr(message_or_call, 'message'):
                bot.answer_callback_query(message_or_call.id, "Вы заблокированы ❌", show_alert=True)
            else:
                bot.send_message(message_or_call.chat.id, "❌ Вы заблокированы и не можете пользоваться ботом.")
        except Exception:
            pass
        return True
    return False

# ====================== ОБРАБОТЧИКИ ======================
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    if check_blocked(message):
        return
    ensure_user(message.from_user)
    log_user_action(message.from_user, "/start или /menu", f"chat_id={message.chat.id}")
    welcome_text = (
        f"Приветствуем вас, {message.from_user.first_name}! ✨\n\n"
        "Добро пожаловать в **LuxuryMuse** — пространство роскоши, красоты и наслаждения.\n\n"
        "Выберите интересующий вас раздел в меню ниже:"
    )
    bot.send_photo(
        message.chat.id,
        WELCOME_IMAGE,
        caption=welcome_text,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    if check_blocked(message):
        return
    ensure_user(message.from_user)
    log_user_action(message.from_user, "/help")
    help_text = (
        "❓ **Справка по использованию бота**\n\n"
        "• Для перехода в главное меню используйте кнопку или команду /menu\n"
        "• Баланс: /balance или кнопка «Баланс»\n"
        "• Промокоды активируются через кнопку «Ввести промокод»\n"
        "• По всем вопросам и для связи с техподдержкой пишите: @mengersalon\n"
        "• Воркеры могут открыть свою панель через команду /worker"
    )
    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=help_text, reply_markup=get_back_button(), parse_mode="Markdown")

@bot.message_handler(commands=['balance'])
def balance_command(message):
    if check_blocked(message):
        return
    ensure_user(message.from_user)
    log_user_action(message.from_user, "/balance")
    bal = get_balance(message.from_user.id)
    text = (
        f"💰 **Ваш баланс**\n\n"
        f"Текущий баланс: **{bal} ₽**\n\n"
        f"Чтобы пополнить — напишите менеджеру @mengersalon\n"
        f"Или активируйте промокод через меню."
    )
    bot.send_message(message.chat.id, text, reply_markup=get_back_button(), parse_mode="Markdown")

@bot.message_handler(commands=['worker'])
def worker_menu(message):
    if check_blocked(message):
        return
    log_user_action(message.from_user, "/worker")
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Неизвестная команда. Введите /start для начала работы.")
        return

    worker_text = (
        "⚙️ **Панель управления воркера (Владельца)**\n\n"
        "Здесь вы можете создавать, удалять анкеты, промокоды, "
        "управлять пользователями и балансами."
    )
    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=worker_text, reply_markup=get_worker_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if check_blocked(call):
        return

    user_id = str(call.from_user.id)
    ensure_user(call.from_user)
    log_user_action(call.from_user, f"кнопка: {call.data}")

    # ---------- Услуги модели ----------
    if call.data.startswith("services_"):
        code = call.data.split("_")[1]
        if code in models_db:
            services_text = models_db[code].get("services", "Секс классический, Секс анальный, Секс групповой, Минет без резинки, Минет глубокий")
            bot.answer_callback_query(call.id, text=services_text, show_alert=True)
        return

    elif call.data.startswith(("photo_", "video_")):
        bot.answer_callback_query(
            call.id,
            text="⏳ Временно не работает\nРаздел в разработке",
            show_alert=True
        )
        return

    elif call.data.startswith("private_"):
        bot.answer_callback_query(
            call.id,
            text="🔒 Приватку можно приобрести у менеджера\nза 2000 ₽\n\n👉 @mengersalon",
            show_alert=True
        )
        return

    elif call.data.startswith("fav_"):
        code = call.data.split("_")[1]
        if code not in models_db:
            bot.answer_callback_query(call.id, "Модель не найдена", show_alert=True)
            return

        if user_id not in favorites_db:
            favorites_db[user_id] = []

        if code in favorites_db[user_id]:
            bot.answer_callback_query(call.id, "Уже в избранном ⭐", show_alert=True)
        else:
            favorites_db[user_id].append(code)
            save_favorites()
            bot.answer_callback_query(call.id, "Добавлено в избранные ⭐", show_alert=True)
        return

    elif call.data.startswith("order_model_"):
        code = call.data.split("_")[2]
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"🤝 **Оформление заказа**\n\n"
            f"Вы выбрали модель с кодом `{code}`.\n\n"
            f"Для оформления заказа напишите менеджеру:\n"
            f"👉 **@mengersalon**\n\n"
            f"Он перенаправит вас и поможет с выбором.",
            parse_mode="Markdown"
        )
        return

    # ---------- Баланс ----------
    elif call.data == "balance":
        bot.answer_callback_query(call.id)
        bal = get_balance(call.from_user.id)
        text = (
            f"💰 **Ваш баланс**\n\n"
            f"Текущий баланс: **{bal} ₽**\n\n"
            f"Чтобы пополнить — напишите менеджеру @mengersalon\n"
            f"Или активируйте промокод через меню."
        )
        send_or_edit_photo(call.message.chat.id, call.message.message_id, text, get_back_button())

    # ---------- Промокод (пользователь) ----------
    elif call.data == "enter_promo":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "🎟 **Введите промокод:**", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_promo_code)

    # ---------- Избранные ----------
    elif call.data == "my_favorites":
        bot.answer_callback_query(call.id)
        user_favs = favorites_db.get(user_id, [])

        if not user_favs:
            bot.send_message(call.message.chat.id, "У вас пока нет избранных моделей.", reply_markup=get_back_button())
            return

        text = "⭐ **Ваши избранные модели:**\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)

        for code in user_favs:
            if code in models_db:
                name = models_db[code].get("name", "Без имени")
                contact = models_db[code].get("contact", models_db[code].get("city", "—"))
                text += f"• `{code}` — {name} ({contact})\n"
                markup.add(types.InlineKeyboardButton(f"Открыть {name} ({code})", callback_data=f"open_fav_{code}"))

        markup.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu"))
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
        return

    elif call.data.startswith("open_fav_"):
        code = call.data.split("_")[2]
        bot.answer_callback_query(call.id)
        if code in models_db:
            model = models_db[code]
            photos = model.get("photos", [model.get("photo", WELCOME_IMAGE)])
            try:
                bot.send_photo(
                    call.message.chat.id,
                    photos[0],
                    caption=model["text"],
                    reply_markup=get_model_keyboard(code),
                    parse_mode="Markdown"
                )
            except Exception:
                bot.send_message(call.message.chat.id, model["text"], reply_markup=get_model_keyboard(code), parse_mode="Markdown")
        return

    # ---------- Главное меню ----------
    if call.data == "order":
        order_markup = types.InlineKeyboardMarkup(row_width=1)
        order_markup.add(
            types.InlineKeyboardButton("🔍 Найти девушку (Ввести код модели)", callback_data="find_model"),
            types.InlineKeyboardButton("👨‍💻 Написать менеджеру напрямую", url="https://t.me/mengersalon"),
            types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu")
        )
        order_text = (
            "🛍️ **Оформление модели в LuxuryMuse**\n\n"
            "Вы можете найти анкету конкретной модели по её коду или обратиться к нашему менеджеру напрямую."
        )
        send_or_edit_photo(call.message.chat.id, call.message.message_id, order_text, order_markup)

    elif call.data == "find_model":
        msg = bot.send_message(call.message.chat.id, "✏️ **Введите уникальный код модели**:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_model_code)

    elif call.data == "about":
        about_text = (
            "✨ **О проекте LuxuryMuse**\n\n"
            "LuxuryMuse — это закрытый премиальный сервис, созданный для тех, кто ценит красоту, "
            "стиль и настоящий комфорт.\n\n"
            "Мы предлагаем эксклюзивных моделей для встреч, выездов и особых случаев. "
            "Каждая анкета тщательно отобрана, а сервис работает быстро, дискретно и на высшем уровне.\n\n"
            "Здесь красота встречается с удовольствием."
        )
        send_or_edit_photo(call.message.chat.id, call.message.message_id, about_text, get_back_button())

    elif call.data == "services":
        services_text = (
            "💎 **Наши услуги**\n\n"
            "Наш салон предлагает возможность **заказать модель на выезд**.\n\n"
            "Вы выбираете девушку по коду, знакомитесь с анкетой и оформляете заказ через менеджера.\n\n"
            "Всё просто, быстро и конфиденциально."
        )
        send_or_edit_photo(call.message.chat.id, call.message.message_id, services_text, get_back_button())

    elif call.data == "contact":
        contact_text = (
            "📩 **Служба поддержки и связи**\n\n"
            "По любым вопросам, предложениям или для личной консультации пишите нашей поддержке напрямую:\n\n"
            "👉 Наш аккаунт: **@mengersalon**"
        )
        send_or_edit_photo(call.message.chat.id, call.message.message_id, contact_text, get_back_button())

    elif call.data == "main_menu":
        welcome_text = "Выберите интересующий вас раздел в меню ниже:"
        send_or_edit_photo(call.message.chat.id, call.message.message_id, welcome_text, get_main_menu())

    # ====================== ПАНЕЛЬ ВОРКЕРА ======================
    elif call.data == "w_create_model":
        if call.from_user.id != ADMIN_ID:
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True)
            return
        msg = bot.send_message(
            call.message.chat.id,
            "🔢 **Создание новой анкеты**\n\n"
            "Шаг 1/7: Введите уникальный **код** модели (например: 77102):",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, admin_input_code)

    elif call.data == "w_list_models":
        if call.from_user.id != ADMIN_ID:
            return
        if not models_db:
            bot.send_message(call.message.chat.id, "Список моделей пуст.")
            return
        list_text = "📋 **Список всех загруженных моделей:**\n\n"
        for code, data in models_db.items():
            list_text += f"• `{code}` — {data.get('name', 'Без имени')} ({data.get('contact', data.get('city', '—'))})\n"
        bot.send_photo(call.message.chat.id, WELCOME_IMAGE, caption=list_text, parse_mode="Markdown", reply_markup=get_back_button())

    elif call.data == "w_delete_model":
        if call.from_user.id != ADMIN_ID:
            return
        if not models_db:
            bot.send_message(call.message.chat.id, "Список моделей пуст.")
            return

        markup = types.InlineKeyboardMarkup(row_width=1)
        for code, data in models_db.items():
            name = data.get("name", "Без имени")
            markup.add(types.InlineKeyboardButton(f"🗑 Удалить {name} ({code})", callback_data=f"confirm_del_{code}"))
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="w_back_worker"))

        bot.send_message(call.message.chat.id, "Выберите анкету для удаления:", reply_markup=markup)

    elif call.data.startswith("confirm_del_"):
        if call.from_user.id != ADMIN_ID:
            return
        code = call.data.split("_")[2]
        if code in models_db:
            name = models_db[code].get("name", code)
            del models_db[code]
            save_models()

            for uid in list(favorites_db.keys()):
                if code in favorites_db[uid]:
                    favorites_db[uid].remove(code)
            save_favorites()

            bot.answer_callback_query(call.id, f"Анкета {name} удалена", show_alert=True)
            bot.send_message(call.message.chat.id, f"✅ Анкета **{name}** (`{code}`) успешно удалена.", parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "Анкета уже удалена", show_alert=True)

    elif call.data == "w_back_worker":
        if call.from_user.id != ADMIN_ID:
            return
        worker_text = (
            "⚙️ **Панель управления воркера (Владельца)**\n\n"
            "Здесь вы можете создавать, удалять анкеты, промокоды, "
            "управлять пользователями и балансами."
        )
        bot.send_photo(call.message.chat.id, WELCOME_IMAGE, caption=worker_text, reply_markup=get_worker_markup(), parse_mode="Markdown")

    elif call.data == "w_stats":
        if call.from_user.id != ADMIN_ID:
            return
        total_balance = sum(u.get("balance", 0) for u in users_db.values())
        stats_text = (
            f"📊 **Статистика бота**\n\n"
            f"Всего анкет: **{len(models_db)}**\n"
            f"Пользователей: **{len(users_db)}**\n"
            f"Промокодов: **{len(promos_db)}**\n"
            f"Заблокировано: **{len(blocked_users)}**\n"
            f"Сумма балансов: **{total_balance} ₽**\n"
            f"Админ ID: `{ADMIN_ID}`"
        )
        bot.send_photo(call.message.chat.id, WELCOME_IMAGE, caption=stats_text, parse_mode="Markdown", reply_markup=get_back_button())

    # ---------- Промокоды (воркер) ----------
    elif call.data == "w_create_promo":
        if call.from_user.id != ADMIN_ID:
            return
        msg = bot.send_message(
            call.message.chat.id,
            "🎟 **Создание промокода**\n\n"
            "Шаг 1/3: Введите **код** промокода (например: WELCOME500):",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, admin_promo_code)

    elif call.data == "w_edit_promo":
        if call.from_user.id != ADMIN_ID:
            return
        if not promos_db:
            bot.send_message(call.message.chat.id, "Промокодов пока нет.")
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for code, data in promos_db.items():
            used = data.get("used", 0)
            max_uses = data.get("max_uses", 0)
            amount = data.get("amount", 0)
            markup.add(types.InlineKeyboardButton(
                f"{code} | {amount}₽ | {used}/{max_uses}",
                callback_data=f"edit_promo_{code}"
            ))
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="w_back_worker"))
        bot.send_message(call.message.chat.id, "Выберите промокод для изменения:", reply_markup=markup)

    elif call.data.startswith("edit_promo_"):
        if call.from_user.id != ADMIN_ID:
            return
        code = call.data.replace("edit_promo_", "", 1)
        if code not in promos_db:
            bot.answer_callback_query(call.id, "Промокод не найден", show_alert=True)
            return
        temp_promo_creation[call.from_user.id] = {"edit_code": code}
        data = promos_db[code]
        msg = bot.send_message(
            call.message.chat.id,
            f"Редактирование `{code}`\n"
            f"Сейчас: {data.get('amount', 0)}₽, использований {data.get('used', 0)}/{data.get('max_uses', 0)}\n\n"
            f"Введите новую **сумму** (число):",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, admin_edit_promo_amount)

    # ---------- Пользователи ----------
    elif call.data == "w_users":
        if call.from_user.id != ADMIN_ID:
            return
        if not users_db:
            bot.send_message(call.message.chat.id, "Пользователей пока нет.")
            return

        # Показываем до 10000 пользователей
        markup = types.InlineKeyboardMarkup(row_width=1)
        sorted_users = sorted(users_db.items(), key=lambda x: x[1].get("last_action", ""), reverse=True)
        for uid, data in sorted_users[:10000]:
            uname = f"@{data.get('username')}" if data.get("username") else "без username"
            name = data.get("first_name", "") or "Без имени"
            bal = data.get("balance", 0)
            blocked = "🚫" if is_blocked(uid) else ""
            markup.add(types.InlineKeyboardButton(
                f"{blocked}{name} ({uname}) | {bal}₽",
                callback_data=f"user_{uid}"
            ))
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="w_back_worker"))
        bot.send_message(
            call.message.chat.id,
            f"👥 **Пользователи** (показано до 10000, всего {len(users_db)})\n"
            f"Нажмите на пользователя, чтобы изменить баланс / посмотреть статистику:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif call.data.startswith("user_"):
        if call.from_user.id != ADMIN_ID:
            return
        uid = call.data.replace("user_", "", 1)
        if uid not in users_db:
            bot.answer_callback_query(call.id, "Пользователь не найден", show_alert=True)
            return
        data = users_db[uid]
        uname = f"@{data.get('username')}" if data.get("username") else "без username"
        name = (data.get("first_name") or "") + (f" {data.get('last_name')}" if data.get("last_name") else "")
        bal = data.get("balance", 0)
        blocked = "Да 🚫" if is_blocked(uid) else "Нет"
        text = (
            f"👤 **Пользователь**\n\n"
            f"Имя: {name.strip() or '—'}\n"
            f"Username: {uname}\n"
            f"ID: `{uid}`\n"
            f"Баланс: **{bal} ₽**\n"
            f"Действий: {data.get('actions', 0)}\n"
            f"Присоединился: {data.get('joined', '—')}\n"
            f"Последнее действие: {data.get('last_action', '—')}\n"
            f"Заблокирован: {blocked}"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💰 Изменить баланс", callback_data=f"setbal_{uid}"),
            types.InlineKeyboardButton("🚫 Заблокировать" if not is_blocked(uid) else "✅ Разблокировать",
                                       callback_data=f"toggleblock_{uid}"),
            types.InlineKeyboardButton("⬅️ К списку", callback_data="w_users"),
            types.InlineKeyboardButton("🏠 В панель воркера", callback_data="w_back_worker")
        )
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

    elif call.data.startswith("setbal_"):
        if call.from_user.id != ADMIN_ID:
            return
        uid = call.data.replace("setbal_", "", 1)
        temp_balance_edit[call.from_user.id] = uid
        msg = bot.send_message(
            call.message.chat.id,
            f"Введите новый баланс для пользователя `{uid}` (число):",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, admin_set_balance)

    elif call.data.startswith("toggleblock_"):
        if call.from_user.id != ADMIN_ID:
            return
        uid = call.data.replace("toggleblock_", "", 1)
        if is_blocked(uid):
            blocked_users.discard(uid)
            blocked_users.discard(int(uid) if uid.isdigit() else uid)
            save_blocked()
            bot.answer_callback_query(call.id, "Пользователь разблокирован", show_alert=True)
            bot.send_message(call.message.chat.id, f"✅ Пользователь `{uid}` разблокирован.", parse_mode="Markdown")
        else:
            blocked_users.add(uid)
            save_blocked()
            bot.answer_callback_query(call.id, "Пользователь заблокирован", show_alert=True)
            bot.send_message(call.message.chat.id, f"🚫 Пользователь `{uid}` заблокирован.", parse_mode="Markdown")

    # ---------- Блокировка ----------
    elif call.data == "w_block_user":
        if call.from_user.id != ADMIN_ID:
            return
        msg = bot.send_message(call.message.chat.id, "🚫 Введите **ID пользователя** для блокировки:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_block_user)

    elif call.data == "w_unblock_user":
        if call.from_user.id != ADMIN_ID:
            return
        msg = bot.send_message(call.message.chat.id, "✅ Введите **ID пользователя** для разблокировки:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_unblock_user)

# ====================== ПРОМОКОД (ПОЛЬЗОВАТЕЛЬ) ======================
def process_promo_code(message):
    if check_blocked(message):
        return
    ensure_user(message.from_user)
    code = message.text.strip().upper()
    log_user_action(message.from_user, "ввод промокода", f"code={code}")

    if code not in promos_db:
        bot.send_message(message.chat.id, "❌ Промокод не найден.", reply_markup=get_back_button())
        return

    promo = promos_db[code]
    used = promo.get("used", 0)
    max_uses = promo.get("max_uses", 0)
    amount = promo.get("amount", 0)
    used_by = promo.get("used_by", [])

    uid = str(message.from_user.id)
    if uid in used_by:
        bot.send_message(message.chat.id, "❌ Вы уже использовали этот промокод.", reply_markup=get_back_button())
        return

    if max_uses > 0 and used >= max_uses:
        bot.send_message(message.chat.id, "❌ Промокод исчерпан (лимит использований).", reply_markup=get_back_button())
        return

    # Начисляем
    if uid not in users_db:
        ensure_user(message.from_user)
    users_db[uid]["balance"] = users_db[uid].get("balance", 0) + amount
    save_users()

    promo["used"] = used + 1
    if "used_by" not in promo:
        promo["used_by"] = []
    promo["used_by"].append(uid)
    save_promos()

    bot.send_message(
        message.chat.id,
        f"✅ Промокод **{code}** активирован!\n"
        f"Начислено: **+{amount} ₽**\n"
        f"Ваш баланс: **{users_db[uid]['balance']} ₽**",
        parse_mode="Markdown",
        reply_markup=get_back_button()
    )

# ====================== ПОИСК МОДЕЛИ ======================
def process_model_code(message):
    if check_blocked(message):
        return
    ensure_user(message.from_user)
    code = message.text.strip()
    log_user_action(message.from_user, "введён код модели", f"code={code}")
    if code in models_db:
        model = models_db[code]
        photos = model.get("photos", [model.get("photo", WELCOME_IMAGE)])
        try:
            bot.send_photo(
                message.chat.id,
                photos[0],
                caption=model["text"],
                reply_markup=get_model_keyboard(code),
                parse_mode="Markdown"
            )
        except Exception:
            bot.send_message(
                message.chat.id,
                model["text"],
                reply_markup=get_model_keyboard(code),
                parse_mode="Markdown"
            )
    else:
        bot.send_message(message.chat.id, "❌ Модель с таким кодом не найдена.\nПопробуйте ещё раз или вернитесь в меню /menu")

# ====================== СОЗДАНИЕ АНКЕТЫ ======================
def admin_input_code(message):
    if message.from_user.id != ADMIN_ID:
        return
    code = message.text.strip()
    if code in models_db:
        bot.send_message(message.chat.id, "❌ Такой код уже существует. Введите другой:")
        bot.register_next_step_handler(message, admin_input_code)
        return
    temp_model_creation[message.from_user.id] = {"code": code, "photos": []}
    msg = bot.send_message(message.chat.id, "Шаг 2/7: Введите **имя** модели:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, admin_input_name)

def admin_input_name(message):
    if message.from_user.id != ADMIN_ID:
        return
    temp_model_creation[message.from_user.id]["name"] = message.text.strip()
    msg = bot.send_message(message.chat.id, "Шаг 3/7: Введите **контакт модели** (например: @nasti1p):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, admin_input_contact)

def admin_input_contact(message):
    if message.from_user.id != ADMIN_ID:
        return
    temp_model_creation[message.from_user.id]["contact"] = message.text.strip()
    msg = bot.send_message(
        message.chat.id,
        "Шаг 4/7: **Отправьте фото** модели прямо в чат (можно несколько).\n\n"
        "После отправки всех фото напишите `готово`.\n"
        "Или напишите `пропустить`, чтобы использовать заглушку.",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, admin_input_photo)

def admin_input_photo(message):
    if message.from_user.id != ADMIN_ID:
        return

    data = temp_model_creation.get(message.from_user.id)
    if not data:
        return

    # Если отправили фото
    if message.photo:
        # Берём самое большое фото
        file_id = message.photo[-1].file_id
        data["photos"].append(file_id)
        bot.send_message(
            message.chat.id,
            f"✅ Фото добавлено ({len(data['photos'])} шт.).\n"
            f"Отправьте ещё или напишите `готово`."
        )
        bot.register_next_step_handler(message, admin_input_photo)
        return

    text = (message.text or "").strip().lower()

    if text == "пропустить":
        data["photos"] = ["https://picsum.photos/600/800"]
        msg = bot.send_message(
            message.chat.id,
            "Шаг 5/7: Введите **прайс** (можно скопировать шаблон):\n\n"
            "```\n"
            "├ 1 час 4.500₽\n"
            "├ 3 часа 9.000₽\n"
            "└ Ночь 17.000₽\n"
            "```",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, admin_input_price)
        return

    if text == "готово":
        if not data["photos"]:
            data["photos"] = ["https://picsum.photos/600/800"]
        msg = bot.send_message(
            message.chat.id,
            "Шаг 5/7: Введите **прайс** (можно скопировать шаблон):\n\n"
            "```\n"
            "├ 1 час 4.500₽\n"
            "├ 3 часа 9.000₽\n"
            "└ Ночь 17.000₽\n"
            "```",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, admin_input_price)
        return

    # Если прислали ссылку
    if text.startswith("http"):
        data["photos"].append(message.text.strip())
        bot.send_message(
            message.chat.id,
            f"✅ Ссылка на фото добавлена ({len(data['photos'])} шт.).\n"
            f"Отправьте ещё фото/ссылку или напишите `готово`."
        )
        bot.register_next_step_handler(message, admin_input_photo)
        return

    bot.send_message(
        message.chat.id,
        "Отправьте **фото** в чат, ссылку, `готово` или `пропустить`."
    )
    bot.register_next_step_handler(message, admin_input_photo)

def admin_input_price(message):
    if message.from_user.id != ADMIN_ID:
        return
    temp_model_creation[message.from_user.id]["price"] = message.text.strip()
    msg = bot.send_message(
        message.chat.id,
        "Шаг 6/7: Введите **допы** (можно скопировать шаблон):\n\n"
        "```\n"
        "├ МБР — 3.500₽\n"
        "├ МЖМ — 4.500₽\n"
        "├ АНАЛ — 1.500₽\n"
        "├ Массаж — 1.000₽\n"
        "└ Стриптиз — 2.500₽\n"
        "```",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, admin_input_extras)

def admin_input_extras(message):
    if message.from_user.id != ADMIN_ID:
        return
    temp_model_creation[message.from_user.id]["extras"] = message.text.strip()
    msg = bot.send_message(
        message.chat.id,
        "Шаг 7/7: Введите **описание** модели.\n\n"
        "Можете скопировать готовый текст:\n\n"
        f"`{DEFAULT_DESCRIPTION}`\n\n"
        "Или напишите своё:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, admin_input_description)

def admin_input_description(message):
    if message.from_user.id != ADMIN_ID:
        return
    data = temp_model_creation[message.from_user.id]
    data["description"] = message.text.strip()

    text = (
        f"✨ **АНКЕТА МОДЕЛИ #{data['code']}** ✨\n\n"
        f"👤 **Имя:** {data['name']}\n"
        f"📞 **Контакт модели:** {data['contact']}\n\n"
        f"💸 **Прайс:**\n"
        f"{data['price']}\n\n"
        f"🔥 **Допы:**\n"
        f"{data['extras']}\n\n"
        f"🔍 **Описание:**\n"
        f"{data['description']}"
    )

    services = "Секс классический, Секс анальный, Секс групповой, Минет без резинки, Минет глубокий"

    models_db[data["code"]] = {
        "photos": data["photos"],
        "name": data["name"],
        "contact": data["contact"],
        "text": text,
        "services": services
    }

    save_models()
    del temp_model_creation[message.from_user.id]

    bot.send_message(
        message.chat.id,
        f"✅ Анкета **#{data['code']}** успешно создана и сохранена!\n\n"
        f"Имя: {data['name']}\n"
        f"Контакт: {data['contact']}\n"
        f"Фото: {len(data['photos'])} шт.",
        parse_mode="Markdown"
    )

# ====================== ПРОМОКОДЫ (АДМИН) ======================
def admin_promo_code(message):
    if message.from_user.id != ADMIN_ID:
        return
    code = message.text.strip().upper()
    if code in promos_db:
        bot.send_message(message.chat.id, "❌ Такой промокод уже есть. Введите другой:")
        bot.register_next_step_handler(message, admin_promo_code)
        return
    temp_promo_creation[message.from_user.id] = {"code": code}
    msg = bot.send_message(message.chat.id, "Шаг 2/3: Введите **сумму** начисления (число, например 500):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, admin_promo_amount)

def admin_promo_amount(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число. Попробуйте ещё раз:")
        bot.register_next_step_handler(message, admin_promo_amount)
        return
    temp_promo_creation[message.from_user.id]["amount"] = amount
    msg = bot.send_message(
        message.chat.id,
        "Шаг 3/3: Введите **макс. количество использований** (0 = безлимит):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, admin_promo_max_uses)

def admin_promo_max_uses(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        max_uses = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число. Попробуйте ещё раз:")
        bot.register_next_step_handler(message, admin_promo_max_uses)
        return

    data = temp_promo_creation[message.from_user.id]
    code = data["code"]
    promos_db[code] = {
        "amount": data["amount"],
        "max_uses": max_uses,
        "used": 0,
        "used_by": []
    }
    save_promos()
    del temp_promo_creation[message.from_user.id]

    bot.send_message(
        message.chat.id,
        f"✅ Промокод **{code}** создан!\n"
        f"Сумма: **{data['amount']} ₽**\n"
        f"Макс. использований: **{max_uses if max_uses > 0 else '∞'}**",
        parse_mode="Markdown"
    )

def admin_edit_promo_amount(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число:")
        bot.register_next_step_handler(message, admin_edit_promo_amount)
        return
    temp_promo_creation[message.from_user.id]["amount"] = amount
    msg = bot.send_message(message.chat.id, "Введите новое **макс. количество использований** (0 = безлимит):")
    bot.register_next_step_handler(msg, admin_edit_promo_max)

def admin_edit_promo_max(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        max_uses = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число:")
        bot.register_next_step_handler(message, admin_edit_promo_max)
        return

    code = temp_promo_creation[message.from_user.id]["edit_code"]
    amount = temp_promo_creation[message.from_user.id]["amount"]
    if code in promos_db:
        promos_db[code]["amount"] = amount
        promos_db[code]["max_uses"] = max_uses
        save_promos()
        bot.send_message(
            message.chat.id,
            f"✅ Промокод **{code}** обновлён!\n"
            f"Сумма: **{amount} ₽**\n"
            f"Макс. использований: **{max_uses if max_uses > 0 else '∞'}**",
            parse_mode="Markdown"
        )
    del temp_promo_creation[message.from_user.id]

# ====================== БАЛАНС / БЛОКИРОВКА ======================
def admin_set_balance(message):
    if message.from_user.id != ADMIN_ID:
        return
    uid = temp_balance_edit.get(message.from_user.id)
    if not uid:
        return
    try:
        new_bal = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите число:")
        bot.register_next_step_handler(message, admin_set_balance)
        return

    if uid not in users_db:
        users_db[uid] = {
            "id": int(uid) if uid.isdigit() else uid,
            "username": "",
            "first_name": "",
            "last_name": "",
            "balance": new_bal,
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "actions": 0,
            "last_action": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    else:
        users_db[uid]["balance"] = new_bal
    save_users()
    del temp_balance_edit[message.from_user.id]

    bot.send_message(
        message.chat.id,
        f"✅ Баланс пользователя `{uid}` установлен: **{new_bal} ₽**",
        parse_mode="Markdown"
    )

def admin_block_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    uid = message.text.strip()
    blocked_users.add(uid)
    save_blocked()
    bot.send_message(message.chat.id, f"🚫 Пользователь `{uid}` заблокирован.", parse_mode="Markdown")

def admin_unblock_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    uid = message.text.strip()
    blocked_users.discard(uid)
    if uid.isdigit():
        blocked_users.discard(int(uid))
    save_blocked()
    bot.send_message(message.chat.id, f"✅ Пользователь `{uid}` разблокирован.", parse_mode="Markdown")

# ====================== ЗАПУСК ======================
if __name__ == '__main__':
    logger.info("🚀 Бот LuxuryMuse запускается...")

    try:
        set_default_commands()
        logger.info("✅ Команды бота установлены.")
    except Exception as e:
        logger.warning(f"Не удалось установить команды (не критично): {e}")

    logger.info(f"📊 Моделей в базе: {len(models_db)}")
    logger.info(f"👥 Пользователей: {len(users_db)}")
    logger.info("✅ Бот запущен и ожидает сообщения...")

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            logger.error(f"Ошибка соединения: {e}")
            logger.info("Перезапуск через 5 секунд...")
            time.sleep(5)
