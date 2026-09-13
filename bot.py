import telebot
from telebot import types
from telebot.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
import json
import os
import time
import logging

# ====================== ЛОГИРОВАНИЕ ======================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ====================== НАСТРОЙКИ ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Переменная окружения BOT_TOKEN не задана! Установите её в Railway → Variables")
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# ВАШ TELEGRAM ID (для приватных логов)
ADMIN_ID = 8588778253 

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

WELCOME_IMAGE = 'https://picsum.photos/600/800'

MODELS_FILE = 'models.json'
FAVORITES_FILE = 'favorites.json'

# ====================== ФУНКЦИЯ ПРИВАТНЫХ ЛОГОВ (ТОЛЬКО ДЛЯ АДМИНА) ======================
def send_admin_log(message_text):
    """Отправляет лог действия только админу в ЛС"""
    try:
        bot.send_message(ADMIN_ID, f"📜 **Системный лог:**\n{message_text}", parse_mode="Markdown")
    except Exception as e:
        # Если бот заблокирован админом или ошибка сети, просто пишем в обычный лог
        logger.warning(f"Не удалось отправить приватный лог админу: {e}")

# ====================== ЗАГРУЗКА / СОХРАНЕНИЕ ======================
def load_models():
    if os.path.exists(MODELS_FILE):
        try:
            with open(MODELS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Ошибка при загрузке models.json: {e}. Используем дефолтные данные.")
    return {
        "65103": {
            "photo": "https://picsum.photos/600/800",
            "name": "Алина",
            "contact": "@alina_model",  # ИЗМЕНЕНО: было city, стало contact
            "text": (
                "✨ **АНКЕТА МОДЕЛИ #65103** ✨\n\n"
                "👤 **Имя:** Алина\n"
                "📞 **Контакт:** @alina_model\n\n"
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
                "Нежная и уверенная в себе девушка."
            ),
            "services": "Секс классический, Секс анальный, Секс групповой, Минет без резинки, Минет глубокий"
        }
    }

def save_models():
    try:
        with open(MODELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(models_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении models.json: {e}")

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Ошибка при загрузке favorites.json: {e}. Создаём пустой файл.")
    return {}

def save_favorites():
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении favorites.json: {e}")

models_db = load_models()
favorites_db = load_favorites()
temp_model_creation = {}

logger.info(f"Загружено моделей: {len(models_db)}")
logger.info(f"Загружено избранных пользователей: {len(favorites_db)}")

# ====================== КОМАНДЫ ======================
def set_default_commands():
    default_commands = [
        BotCommand("start", "🚀 Запустить / В главное меню"),
        BotCommand("menu", "🏠 Главное меню"),
        BotCommand("help", "❓ Помощь / Поддержка"),
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
    btn_order = types.InlineKeyboardButton("🤝 Оформить", callback_data=f"order_model_{code}")
    btn_photo = types.InlineKeyboardButton("🖼️ Другое фото", callback_data=f"photo_{code}")
    btn_full_photo = types.InlineKeyboardButton("🔞 Фото", callback_data=f"photo_{code}")
    btn_video = types.InlineKeyboardButton("🔞 Видео", callback_data=f"video_{code}")
    btn_fav = types.InlineKeyboardButton("⭐ Добавить в избранные", callback_data=f"fav_{code}")
    btn_reviews = types.InlineKeyboardButton("💬 Отзывы", url="https://t.me/ls_reviews")
    btn_services = types.InlineKeyboardButton("🔲 Услуги", callback_data=f"services_{code}")
    btn_back = types.InlineKeyboardButton("🏠 Назад", callback_data="main_menu")

    markup.add(btn_order, btn_photo)
    markup.add(btn_full_photo, btn_video)
    markup.add(btn_fav)
    markup.add(btn_reviews, btn_services)
    markup.add(btn_back)
    return markup

def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🛍️ Оформить заказ", callback_data="order"),
        types.InlineKeyboardButton("⭐ Мои избранные", callback_data="my_favorites"),
        types.InlineKeyboardButton("✨ О проекте LuxuryMuse", callback_data="about"),
        types.InlineKeyboardButton("💎 Наши услуги", callback_data="services"),
        types.InlineKeyboardButton("📩 Связаться с нами / Поддержка", callback_data="contact")
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
        types.InlineKeyboardButton("🗑 Удалить анкету", callback_data="w_delete_model"),
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

# ====================== ОБРАБОТЧИКИ ======================
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    # ЛОГ: кто зашел
    send_admin_log(f"Пользователь {message.from_user.first_name} (@{message.from_user.username}) нажал /start")
    
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
    send_admin_log(f"Пользователь {message.from_user.first_name} нажал /help")
    help_text = (
        "❓ **Справка по использованию бота**\n\n"
        "• Для перехода в главное меню используйте кнопку или команду /menu\n"
        "• По всем вопросам и для связи с техподдержкой пишите: @mengersalon\n"
        "• Воркеры могут открыть свою панель через команду /worker"
    )
    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=help_text, reply_markup=get_back_button(), parse_mode="Markdown")

@bot.message_handler(commands=['worker'])
def worker_menu(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "Неизвестная команда. Введите /start для начала работы.")
        return

    send_admin_log(f"Админ {message.from_user.first_name} открыл панель воркера")
    
    worker_text = (
        "⚙️ **Панель управления воркера (Владельца)**\n\n"
        "Здесь вы можете создавать, удалять анкеты и управлять ботом."
    )
    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=worker_text, reply_markup=get_worker_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = str(call.from_user.id)
    user_name = call.from_user.first_name
    user_username = call.from_user.username or "Нет юзернейма"
    
    # ЛОГ: какое действие нажал пользователь
    send_admin_log(f"Пользователь {user_name} (@{user_username}) нажал кнопку: {call.data}")

    if call.data.startswith("services_"):
        code = call.data.split("_")
        if code in models_db:
            services_text = models_db[code].get("services", "Секс классический, Секс анальный, Секс групповой, Минет без резинки, Минет глубокий")
            bot.answer_callback_query(call.id, text=services_text, show_alert=True)
        return

    elif call.data.startswith(("photo_", "video_")):
        bot.answer_callback_query(call.id, text="Информация обновляется...", show_alert=False)
        return

    elif call.data.startswith("fav_"):
        code = call.data.split("_")
        if code not in models_db:
            bot.answer_callback_query(call.id, "Модель не найдена", show_alert=True)
            return

        if user_id not in favorites_db:
            favorites_db[user_id] = 

        if code in favorites_db[user_id]:
            bot.answer_callback_query(call.id, "Уже в избранном ⭐", show_alert=True)
        else:
            favorites_db[user_id].append(code)
            save_favorites()
            bot.answer_callback_query(call.id, "Добавлено в избранные ⭐", show_alert=True)
        return

    elif call.data.startswith("order_model_"):
        code = call.data.split("_")
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

    elif call.data == "my_favorites":
        bot.answer_callback_query(call.id)
        user_favs = favorites_db.get(user_id, )

        if not user_favs:
            bot.send_message(call.message.chat.id, "У вас пока нет избранных моделей.", reply_markup=get_back_button())
            return

        text = "⭐ **Ваши избранные модели:**\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)

        for code in user_favs:
            if code in models_db:
                name = models_db[code].get("name", "Без имени")
                contact = models_db[code].get("contact", "—") # ИЗМЕНЕНО: было city
                text += f"• `{code}` — {name} ({contact})\n"
                markup.add(types.InlineKeyboardButton(f"Открыть {name} ({code})", callback_data=f"open_fav_{code}"))

        markup.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu"))
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
        return

    elif call.data.startswith("open_fav_"):
        code = call.data.split("_")
        bot.answer_callback_query(call.id)
        if code in models_db:
            model = models_db[code]
            try:
                bot.send_photo(
                    call.message.chat.id,
                    model["photo"],
                    caption=model["text"],
                    reply_markup=get_model_keyboard(code),
                    parse_mode="Markdown"
                )
            except Exception:
                bot.send_message(call.message.chat.id, model["text"], reply_markup=get_model_keyboard(code), parse_mode="Markdown")
        return

    if call.data == "order":
        order_markup = types.InlineKeyboardMarkup(row_width=1)
        order_markup.add(
            types.InlineKeyboardButton("🔍 Найти девушку (Ввести код модели)", callback_data="find_model"),
            types.InlineKeyboardButton("👨‍💻 Написать менеджеру напрямую", url="https://t.me/mengersalon"),
            types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu")
        )
        order_text = (
            "🛍️ **Оформление заказа в LuxuryMuse**\n\n"
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
            list_text += f"• `{code}` — {data.get('name', 'Без имени')} ({data.get('contact', '—')})\n" # ИЗМЕНЕНО: было city
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
        code = call.data.split("_")
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
            "Здесь вы можете создавать, удалять анкеты и управлять ботом."
        )
        bot.send_photo(call.message.chat.id, WELCOME_IMAGE, caption=worker_text, reply_markup=get_worker_markup(), parse_mode="Markdown")

    elif call.data == "w_stats":
        if call.from_user.id != ADMIN_ID:
            return
        stats_text = (
            f"📊 **Статистика бота**\n\n"
            f"Всего анкет: **{len(models_db)}**\n"
            f"Админ ID: `{ADMIN_ID}`"
        )
        bot.send_photo(call.message.chat.id, WELCOME_IMAGE, caption=stats_text, parse_mode="Markdown", reply_markup=get_back_button())

# ====================== ПОИСК МОДЕЛИ ======================
def process_model_code(message):
    send_admin_log(f"Пользователь {message.from_user.first_name} ищет модель по коду: {message.text}")
    code = message.text.strip()
    if code in models_db:
        model = models_db[code]
        try:
            bot.send_photo(
                message.chat.id,
                model["photo"],
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
    temp_model_creation[message.from_user.id] = {"code": code}
    msg = bot.send_message(message.chat.id, "Шаг 2/7: Введите **имя** модели:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, admin_input_name)

def admin_input_name(message):
    if message.from_user.id != ADMIN_ID:
        return
    temp_model_creation[message.from_user.id]["name"] = message.text.strip()
    # ИЗМЕНЕНО: Вместо города теперь контакт
    msg = bot.send_message(message.chat.id, "Шаг 3/7: Введите **контакт модели** (например, @username):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, admin_input_contact)

def admin_input_contact(message):
    if message.from_user.id != ADMIN_ID:
        return
    temp_model_creation[message.from_user.id]["contact"] = message.text.strip()
    msg = bot.send_message(
        message.chat.id,
        "Шаг 4/7: Отправьте **ссылку на фото** модели\n(или напишите `пропустить`):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, admin_input_photo)

def admin_input_photo(message):
    if message.from_user.id != ADMIN_ID:
        return
    photo = message.text.strip()
    if photo.lower() == "пропустить":
        photo = "https://picsum.photos/600/800"
    temp_model_creation[message.from_user.id]["photo"] = photo
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
    msg = bot.send_message(message.chat.id, "Шаг 7/7: Введите **описание** модели:", parse_mode="Markdown")
    bot.register_next_step_handler(msg, admin_input_description)

def admin_input_description(message):
    if message.from_user.id != ADMIN_ID:
        return
    data = temp_model_creation[message.from_user.id]
    data["description"] = message.text.strip()

    text = (
        f"✨ **АНКЕТА МОДЕЛИ #{data['code']}** ✨\n\n"
        f"👤 **Имя:** {data['name']}\n"
        f"📞 **Контакт:** {data['contact']}\n\n"  # ИЗМЕНЕНО: было город
        f"💸 **Прайс:**\n"
        f"{data['price']}\n\n"
        f"🔥 **Допы:**\n"
        f"{data['extras']}\n\n"
        f"🔍 **Описание:**\n"
        f"{data['description']}"
    )

    services = "Секс классический, Секс анальный, Секс групповой, Минет без резинки, Минет глубокий"

    models_db[data["code"]] = {
        "photo": data["photo"],
        "name": data["name"],
        "contact": data["contact"],  # ИЗМЕНЕНО: было city
        "text": text,
        "services": services
    }

    save_models()
    del temp_model_creation[message.from_user.id]

    bot.send_message(
        message.chat.id,
        f"✅ Анкета **#{data['code']}** успешно создана и сохранена!\n\n"
        f"Имя: {data['name']}\n"
        f"Контакт: {data['contact']}",
        parse_mode="Markdown"
    )
    send_admin_log(f"Админ создал новую анкету: #{data['code']} ({data['name']})")

# ====================== ЗАПУСК ======================
if __name__ == '__main__':
    logger.info("🚀 Бот LuxuryMuse запускается...")

    try:
        set_default_commands()
        logger.info("✅ Команды бота установлены.")
    except Exception as e:
        logger.warning(f"Не удалось установить команды (не критично): {e}")

    logger.info(f"📊 Моделей в базе: {len(models_db)}")
    logger.info("✅ Бот запущен и ожидает сообщения...")

    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            logger.error(f"Ошибка соединения: {e}")
            logger.info("Перезапуск через 5 секунд...")
            time.sleep(5)
