from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio
import time
import random
import json
import threading
from datetime import datetime
import os

# === НАСТРОЙКИ ===
BOT_TOKEN = "8028065845:AAHuXMq19dNNjXfJBrSLcC3F5-5uBAsF0CE"  # Токен от @BotFather

# Здесь будем хранить chat_id пользователя
user_chat_id = None

# Список сообщений (можно менять)
MESSAGES = [
    "Привет, котик! 😊 Пора принять таблетки!",
    "Эй, солнышко! 🌞 Напоминаю про таблетки!",
    "Котик, время пить таблетки! 💊 Ты справишься!",
    "Мур-мур! 🐱 Таблетки ждут!",
    "Любимая, не пропусти приём таблеток! 💖"
]

# === ФУНКЦИИ БОТА ===

# Обработчик команды /start
async def start_command(update: Update, context: CallbackContext):
    global user_chat_id
    user_chat_id = update.effective_chat.id
    
    # Создаем клавиатуру с кнопкой
    keyboard = [[KeyboardButton("Выпила! ✅")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "Привет! Я твой бот-напоминатель о таблетках! 💊\n"
        "Теперь я буду присылать тебе напоминания в нужное время.\n"
        "Просто нажимай кнопку 'Выпила! ✅', когда примёшь таблетки!"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    print(f"✅ Пользователь активирован! Chat ID: {user_chat_id}")

# Обработчик кнопки "Выпила!"
async def handle_pill_taken(update: Update, context: CallbackContext):
    responses = [
        "Да ты моя зая❤️ Продолжай в том же духе :)",
        "Умничка ты моя🎉 Продолжаем заботиться о себе.",
        "Киса выпила таблеточку❤️ Ты у меня такая ответственная =)",
        "Супер! 😊 Я тобой горжусь!",
        "Спасибо, что не забыла выпить таблеточку. Я люблю тебя❤️",
    ]
    
    await update.message.reply_text(random.choice(responses))

# Функция отправки напоминания
async def send_reminder():
    if user_chat_id is None:
        print("❌ Chat ID не установлен. Попросите написать /start")
        return
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Создаем клавиатуру
        keyboard = [[KeyboardButton("Выпила! ✅")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        message = random.choice(MESSAGES)
        
        await application.bot.send_message(
            chat_id=user_chat_id,
            text=message,
            reply_markup=reply_markup
        )
        print(f"✅ Напоминание отправлено!")
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

# Функция для запуска расписания
def run_scheduler():
    # НАСТРОЙТЕ ВРЕМЯ ЗДЕСЬ
    schedule.every().day.at("22:00").do(lambda: asyncio.run(send_reminder()))  # Вечер
    
    print("⏰ Расписание настроено на 21:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# Основная функция
def main():
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.Text("Выпила! ✅"), handle_pill_taken))
    
    print("🚀 Бот запускается...")
    print("📝 Попросите девушку написать боту команду /start")
    
    # Запускаем расписание в отдельном потоке
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()