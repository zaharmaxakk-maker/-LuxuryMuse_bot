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

WELCOME_IMAGE = 'https://picsum.photos'

MODELS_FILE = 'models.json'
FAVORITES_FILE = 'favorites.json'

# ====================== ФУНКЦИЯ ПРИВАТНЫХ ЛОГОВ ======================
def send_admin_log(message_text):
    """Отправляет лог действия только админу в ЛС"""
    try:
        bot.send_message(ADMIN_ID, f"📜 **Системный лог:**\n{message_text}", parse_mode="Markdown")
    except Exception as e:
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
            "photo": "https://picsum.photos",
            "name": "Алина",
            "contact": "@alina_model",
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
    btn_reviews = types.InlineKeyboardButton("💬 Отзывы", url="https://t.me")
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

# ====================== ОБРАБОТЧИКИ КОМАНД ======================
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
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
    send_admin_log(f"Пользователь {message.from_user.first_name} открыл помощь.")
    help_text = "❓ **Поддержка LuxuryMuse**\n\nЕсли у вас возникли вопросы, свяжитесь с нашим администратором."
    bot.send_message(message.chat.id, help_text, reply_markup=get_back_button())

@bot.message_handler(commands=['worker'])
def worker_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "⚙️ **Панель воркера:**", reply_markup=get_worker_markup())
    else:
        bot.send_message(message.chat.id, "❌ У вас нет доступа к этой команде.")

# ====================== ОБРАБОТЧИК КНОПОК (CALLBACK) ======================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    # Сбрасываем анимацию загрузки на кнопке
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    if call.data == "main_menu":
        welcome_text = (
            f"Приветствуем вас! ✨\n\n"
            "Добро пожаловать в **LuxuryMuse** — пространство роскоши, красоты и наслаждения.\n\n"
            "Выберите интересующий вас раздел в меню ниже:"
        )
        send_or_edit_photo(chat_id, message_id, welcome_text, get_main_menu())
        
    elif call.data == "order":
        if models_db:
            first_code = list(models_db.keys())[0]
            model = models_db[first_code]
            send_or_edit_photo(chat_id, message_id, model["text"], get_model_keyboard(first_code), photo=model["photo"])
        else:
            bot.send_message(chat_id, "😔 В базе пока нет доступных моделей.", reply_markup=get_back_button())
            
    elif call.data == "about":
        bot.send_message(chat_id, "✨ **LuxuryMuse** — это премиальное агентство.\nМы предоставляем лучший сервис.", reply_markup=get_back_button())
        
    elif call.data == "services":
