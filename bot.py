import os
import time
import random
import json
import threading
from datetime import datetime
import schedule

# Для новой версии библиотеки
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# === НАСТРОЙКИ ===
BOT_TOKEN = os.environ['BOT_TOKEN']

# Файл для хранения настроек
SETTINGS_FILE = "bot_settings.json"

def load_settings():
    default_settings = {
        "reminder_times": ["22:00"],
        "messages": [
            "Привет, котик! 😊 Пора принять таблетки!",
            "Эй, солнышко! 🌞 Напоминаю про таблетки!",
            "Котик, время пить таблетки! 💊 Ты справишься!",
            "Мур-мур! 🐱 Таблетки ждут!",
            "Любимая, не пропусти приём таблеток! 💖"
        ],
        "user_chat_id": None
    }
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# Загружаем настройки
settings = load_settings()

# === КОМАНДЫ БОТА ===
async def start_command(update: Update, context: CallbackContext):
    settings["user_chat_id"] = update.effective_chat.id
    save_settings(settings)
    
    keyboard = [[KeyboardButton("Выпила! ✅")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "Привет! Я твой бот-напоминатель о таблетках! 💊\n"
        f"Напоминания в: {', '.join(settings['reminder_times'])}\n"
        "Нажимай кнопку когда примешь таблетки!"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    print(f"✅ Пользователь активирован! Chat ID: {settings['user_chat_id']}")

async def settime_command(update: Update, context: CallbackContext):
    if context.args:
        new_times = context.args
        valid_times = []
        for time_str in new_times:
            try:
                datetime.strptime(time_str, "%H:%M")
                valid_times.append(time_str)
            except ValueError:
                await update.message.reply_text(f"❌ Неверный формат: {time_str}. Используйте ЧЧ:ММ")
                return
        
        settings["reminder_times"] = valid_times
        save_settings(settings)
        
        await update.message.reply_text(f"✅ Новое время: {', '.join(valid_times)}")
        print(f"⏰ Время изменено: {valid_times}")

async def addmessage_command(update: Update, context: CallbackContext):
    if context.args:
        new_message = " ".join(context.args)
        settings["messages"].append(new_message)
        save_settings(settings)
        await update.message.reply_text(f"✅ Сообщение добавлено!")
    else:
        await update.message.reply_text("Напишите: /addmessage Ваш текст")

async def handle_pill_taken(update: Update, context: CallbackContext):
    responses = ["Да ты моя зая❤️", "Умничка. Люблю тебя❤️", "Какая молодец💪", "Киса молодец😊"]
    await update.message.reply_text(random.choice(responses))

async def send_reminder():
    if not settings.get("user_chat_id"):
        print("❌ Chat ID не установлен")
        return
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        keyboard = [[KeyboardButton("Выпила! ✅")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        message = random.choice(settings["messages"])
        
        await application.bot.send_message(
            chat_id=settings["user_chat_id"],
            text=message,
            reply_markup=reply_markup
        )
        print(f"✅ Напоминание отправлено!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def run_reminder():
    """Запускает отправку напоминания в event loop"""
    import asyncio
    asyncio.run(send_reminder())

def check_time_and_remind():
    print("⏰ Таймер запущен...")
    
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M")
            
            # Перезагружаем настройки
            global settings
            settings = load_settings()
            
            if current_time in settings["reminder_times"]:
                run_reminder()
                time.sleep(60)  # Ждем минуту чтобы не отправить повторно
            
            time.sleep(30)  # Проверяем каждые 30 секунд
        except Exception as e:
            print(f"❌ Ошибка в таймере: {e}")
            time.sleep(60)

def main():
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("settime", settime_command))
    application.add_handler(CommandHandler("addmessage", addmessage_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Выпила! ✅$"), handle_pill_taken))
    
    print("🚀 Бот запускается на Railway...")
    
    # Запускаем проверку времени в отдельном потоке
    timer_thread = threading.Thread(target=check_time_and_remind)
    timer_thread.daemon = True
    timer_thread.start()
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()