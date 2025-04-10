from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers import start_handler, callback_handler, message_handler
from config import BOT_TOKEN
from db import init_db  # ← добавляем

if __name__ == "__main__":
    init_db()  # ← вызываем инициализацию базы

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("🤖 Бот запущен!")
    application.run_polling()
