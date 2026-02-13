#!/usr/bin/env python3
"""
Пример Telegram бота для работы с SQL Agent API
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from dotenv import load_dotenv
import os

load_dotenv('.env.db')

# Настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
SQL_AGENT_API = "http://localhost:8006/api/telegram"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = """
🎵 *Добро пожаловать в Музыкальную Аналитику!*

Я помогу вам получить статистику по артистам, трекам и платформам.

*Примеры команд:*

📊 *Общая статистика:*
• /stats Сколько заработал Yenlik?
• /stats Топ 10 треков
• /stats Топ 5 артистов

🎵 *По трекам:*
• /stats Топ 5 треков Yenlik
• /stats Какие треки у Ernar Amandyq?
• /stats Сколько стримов у трека Meili?

📱 *По платформам:*
• /stats Yenlik на Spotify
• /stats Топ 5 платформ
• /stats Средняя ставка на Apple Music

🌍 *География:*
• /stats Yenlik в Казахстане
• /stats Топ 10 стран

📅 *Динамика:*
• /stats Динамика Yenlik по месяцам

Или просто отправьте мне текстовое сообщение с вопросом!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stats"""
    # Получаем запрос пользователя
    query = ' '.join(context.args) if context.args else "Топ 10 треков"
    
    # Показываем индикатор "печатает..."
    await update.message.chat.send_action(action="typing")
    
    try:
        # Отправляем запрос в API
        response = requests.post(SQL_AGENT_API, json={"query": query}, timeout=30)
        data = response.json()
        
        if data['success']:
            # Отправляем отформатированное сообщение
            await update.message.reply_text(
                data['telegram_message'],
                parse_mode='Markdown'
            )
        else:
            error_msg = f"❌ *Ошибка*\n\n_{data.get('error', 'Неизвестная ошибка')}_"
            await update.message.reply_text(error_msg, parse_mode='Markdown')
    
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "⏱️ Запрос занял слишком много времени. Попробуйте упростить запрос."
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка: {str(e)}"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    query = update.message.text
    
    # Игнорируем команды
    if query.startswith('/'):
        return
    
    # Показываем индикатор "печатает..."
    await update.message.chat.send_action(action="typing")
    
    try:
        # Отправляем запрос в API
        response = requests.post(SQL_AGENT_API, json={"query": query}, timeout=30)
        data = response.json()
        
        if data['success']:
            await update.message.reply_text(
                data['telegram_message'],
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Не удалось обработать запрос. Попробуйте переформулировать."
            )
    
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            "⏱️ Запрос занял слишком много времени."
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка: {str(e)}"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_message = """
📚 *Справка*

*Команды:*
• /start - Начало работы
• /stats [запрос] - Получить статистику
• /help - Эта справка

*Примеры запросов:*

📊 Общее:
• Сколько заработал Yenlik?
• Топ 10 треков
• Топ 5 артистов

🎵 Треки:
• Топ 5 треков Yenlik
• Какие треки у Ernar Amandyq?

📱 Платформы:
• Yenlik на Spotify
• Топ 5 платформ

🌍 География:
• Топ 10 стран
• Yenlik в Казахстане

Просто отправьте мне вопрос!
    """
    await update.message.reply_text(help_message, parse_mode='Markdown')


def main():
    """Запуск бота"""
    print("🤖 Запуск Telegram бота...")
    print(f"📡 SQL Agent API: {SQL_AGENT_API}")
    
    # Проверка API
    try:
        response = requests.get("http://localhost:8006/health", timeout=5)
        if response.status_code == 200:
            print("✅ SQL Agent API доступен")
        else:
            print("⚠️  SQL Agent API недоступен")
    except:
        print("❌ SQL Agent API не запущен!")
        print("Запустите: python sql_agent_fastapi.py")
        return
    
    # Создание бота
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен!")
    print("Отправьте /start в Telegram для начала работы")
    
    # Запуск
    app.run_polling()


if __name__ == '__main__':
    main()
