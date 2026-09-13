import telebot
from telebot import types
from telebot.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
import json
import os
import time
import logging

# ====================== ЛОГИРОВАНИЕ ======================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ====================== НАСТРОЙКИ ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Переменная окружения BOT_TOKEN не задана!")
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

ADMIN_ID = 8588778253 
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
WELCOME_IMAGE = 'https://picsum.photos'
MODELS_FILE = 'models.json'
FAVORITES_FILE = 'favorites.json'

# ====================== ЛОГИ ИДЕНТИФИКАЦИИ ======================
def send_admin_log(message_text):
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
        except Exception as e:
            logger.warning(f"Ошибка при загрузке models.json: {e}")
    return {
        "65103": {
            "photo": "https://picsum.photos",
            "name": "Алина",
            "contact": "@alina_model",
            "text": "✨ **АНКЕТА МОДЕЛИ #65103** ✨\n\n👤 **Имя:** Алина\n📞 **Контакт:** @alina_model\n\n💸 **Прайс:**\n├ 1 час 4.500₽\n├ 3 часа 9.000₽\n└ Ночь 17.000₽",
            "services": "Секс классический"
        }
    }

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Ошибка при загрузке favorites.json: {e}")
    return {}

def save_favorites():
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites_db, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении favorites.json: {e}")

models_db = load_models()
favorites_db = load_favorites()

# ====================== КЛАВИАТУРЫ ======================
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

def get_model_keyboard(code):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🤝 Оформить", callback_data=f"order_model_{code}"), types.InlineKeyboardButton("🖼️ Другое фото", callback_data=f"photo_{code}"))
    markup.add(types.InlineKeyboardButton("🔞 Фото", callback_data=f"photo_{code}"), types.InlineKeyboardButton("🔞 Видео", callback_data=f"video_{code}"))
    markup.add(types.InlineKeyboardButton("⭐ Добавить в избранные", callback_data=f"fav_{code}"))
    markup.add(types.InlineKeyboardButton("💬 Отзывы", url="https://t.me"), types.InlineKeyboardButton("🔲 Услуги", callback_data=f"services_{code}"))
    markup.add(types.InlineKeyboardButton("🏠 Назад", callback_data="main_menu"))
    return markup

def get_back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="main_menu"))
    return markup

def send_or_edit_photo(chat_id, message_id, caption, reply_markup, photo=WELCOME_IMAGE):
    try:
        bot.edit_message_media(media=types.InputMediaPhoto(photo, caption=caption, parse_mode="Markdown"), chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)
    except Exception:
        try:
            bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=caption, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception:
            bot.send_photo(chat_id, photo, caption=caption, reply_markup=reply_markup, parse_mode="Markdown")

# ====================== ОБРАБОТЧИКИ КОМАНД ======================
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    welcome_text = f"Приветствуем вас, {message.from_user.first_name}! ✨\n\nДобро пожаловать в **LuxuryMuse**.\n\nВыберите интересующий вас раздел:"
    bot.send_photo(message.chat.id, WELCOME_IMAGE, caption=welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "❓ **Поддержка LuxuryMuse**\n\nСвяжитесь с администратором.", reply_markup=get_back_button())

# ====================== ИЗОЛИРОВАННЫЕ ОБРАБОТЧИКИ КНОПОК ======================
@bot.callback_query_handler(func=lambda call: call.data == "main_menu")
def menu_callback(call):
    bot.answer_callback_query(call.id)
    txt = "Приветствуем вас! ✨\n\nДобро пожаловать в **LuxuryMuse**.\n\nВыберите раздел:"
    send_or_edit_photo(call.message.chat.id, call.message.message_id, txt, get_main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "order")
def order_callback(call):
    bot.answer_callback_query(call.id)
    if not models_db:
        bot.send_message(call.message.chat.id, "😔 В базе пока нет доступных моделей.", reply_markup=get_back_button())
        return
    first_code = list(models_db.keys())[0]
    model = models_db[first_code]
    send_or_edit_photo(call.message.chat.id, call.message.message_id, model["text"], get_model_keyboard(first_code), photo=model["photo"])

@bot.callback_query_handler(func=lambda call: call.data == "about")
def about_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "✨ **LuxuryMuse** — это премиальное агентство.", reply_markup=get_back_button())

@bot.callback_query_handler(func=lambda call: call.data == "services")
def services_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "💎 **Наши услуги:**\n\nИндивидуальный подход.", reply_markup=get_back_button())

@bot.callback_query_handler(func=lambda call: call.data == "contact")
def contact_callback(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📩 **Связь с нами:** @luxury_manager", reply_markup=get_back_button())

@bot.callback_query_handler(func=lambda call: call.data == "my_favorites")
def favorites_callback(call):
    bot.answer_callback_query(call.id)
    user_id = str(call.from_user.id)
    user_favs = favorites_db.get(user_id, [])
    if not user_favs:
        bot.send_message(call.message.chat.id, "⭐ Ваша вкладка 'Избранное' пуста.", reply_markup=get_back_button())
        return
    bot.send_message(call.message.chat.id, f"⭐ Ваши избранные модели ID: {', '.join(user_favs)}", reply_markup=get_back_button())

@bot.callback_query_handler(func=lambda call: call.data.startswith("fav_"))
def add_to_fav_callback(call):
    bot.answer_callback_query(call.id)
    code = call.data.replace("fav_", "")
    user_id = str(call.from_user.id)
    if user_id not in favorites_db:
        favorites_db[user_id] = []
    if code not in favorites_db[user_id]:
        favorites_db[user_id].append(code)
        save_favorites()
        bot.send_message(call.message.chat.id, f"✅ Модель #{code} добавлена в избранное!")
    else:
        bot.send_message(call.message.chat.id, f"ℹ️ Модель #{code} уже в избранном.")

# ====================== ЗАПУСК БОТА ======================
if __name__ == "__main__":
    default_commands = [BotCommand("start", "🚀 Запуск"), BotCommand("menu", "🏠 Меню"), BotCommand("help", "❓ Помощь")]
    bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())
    logger.info("Бот запускается...")
    bot.infinity_polling()
