# handlers.py — с проверкой данных перед генерацией
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import DEFAULT_LANGUAGE
from db import is_premium, increment_request, get_user, save_article, set_premium
from writer import generate_article
from yookassa_handler import create_payment_link

TEXTS = {
    "ru": {
        "start": "Привет! 🤖 Что будем писать?",
        "choose_type": "Выбери тип статьи:",
        "enter_keywords": "🔑 Введи ключевые слова через запятую:",
        "choose_length": "📏 Выбери длину текста:",
        "enter_custom_length": "📝 Введи нужную длину (от 100 до 4000 символов):",
        "wrong_length": "❌ Введи число от 100 до 4000.",
        "choose_style": "🎨 Выбери стиль текста:",
        "wait": "⏳ Подожди, генерирую текст...",
        "ready": "✅ Готово! Вот твой текст:",
        "limit": "🔒 Ты использовал 2 бесплатных запроса. Купи премиум, чтобы продолжить.",
        "language_choice": "🌍 Выбери язык / Choose language",
        "new_prompt": "🆕 Хочешь создать новый текст?",
        "missing_data": "⚠️ Данные неполные. Пожалуйста, начни сначала."
    },
    "en": {
        "start": "Hi! 🤖 What do you want to write?",
        "choose_type": "Choose article type:",
        "enter_keywords": "🔑 Enter keywords (comma-separated):",
        "choose_length": "📏 Choose text length:",
        "enter_custom_length": "📝 Enter custom length (100-4000):",
        "wrong_length": "❌ Enter a number between 100 and 4000.",
        "choose_style": "🎨 Choose article style:",
        "wait": "⏳ Please wait, generating text...",
        "ready": "✅ Done! Here’s your text:",
        "limit": "🔒 You've used 2 free requests. Buy premium to continue.",
        "language_choice": "🌍 Choose language / Выбери язык",
        "new_prompt": "🆕 Want to create another text?",
        "missing_data": "⚠️ Incomplete data. Please start again."
    }
}

def translate(key, lang):
    return TEXTS.get(lang, TEXTS[DEFAULT_LANGUAGE]).get(key, key)

async def check_limit_and_offer_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_premium(user_id):
        increment_request(user_id)
        count, _ = get_user(user_id)
        if count > 2:
            lang = context.user_data.get("lang", DEFAULT_LANGUAGE)
            link = create_payment_link(user_id)
            await update.callback_query.message.reply_text(
                translate("limit", lang),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💎 Купить премиум за 300₽", url=link)]
                ])
            )
            return False
    return True

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_data.clear()
    user_data["lang"] = DEFAULT_LANGUAGE
    user_id = update.effective_user.id

    args = context.args
    if args and args[0].startswith("paid_"):
        set_premium(user_id)
        await update.message.reply_text("🎉 Спасибо за оплату! Премиум активирован на 7 дней.")
        return

    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    await update.message.reply_text(translate("language_choice", DEFAULT_LANGUAGE), reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_data["lang"] = lang
        await query.message.reply_text(translate("choose_type", lang), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍 Рекламная", callback_data="type_ad")],
            [InlineKeyboardButton("🔍 SEO-текст", callback_data="type_seo")],
            [InlineKeyboardButton("🎉 Поздравление", callback_data="type_congrats")],
        ]))

    elif data.startswith("type_"):
        user_data["type"] = data.replace("type_", "")
        await query.message.reply_text(translate("enter_keywords", user_data["lang"]))

    elif data.startswith("length_"):
        lengths = {"500": 500, "1000": 1000, "1500": 1500}
        user_data["length"] = lengths.get(data.replace("length_", ""))
        await query.message.reply_text(translate("choose_style", user_data["lang"]), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Продающий", callback_data="style_sell")],
            [InlineKeyboardButton("😊 Дружелюбный", callback_data="style_friendly")],
            [InlineKeyboardButton("📚 Информационный", callback_data="style_info")],
        ]))

    elif data == "length_custom":
        user_data["awaiting_custom_length"] = True
        await query.message.reply_text(translate("enter_custom_length", user_data["lang"]))

    elif data.startswith("style_"):
        if not all(key in user_data for key in ["type", "keywords", "length"]):
            await query.message.reply_text(translate("missing_data", user_data.get("lang", DEFAULT_LANGUAGE)))
            return

        user_data["style"] = data.replace("style_", "")

        if not await check_limit_and_offer_premium(update, context):
            return

        wait_msg = await query.message.reply_text(translate("wait", user_data["lang"]))
        text = await generate_article(user_data)
        await wait_msg.delete()
        await query.message.reply_text(translate("ready", user_data["lang"]))
        await query.message.reply_text(text)
        save_article(update.effective_user.id, text)

        await query.message.reply_text(
            translate("new_prompt", user_data["lang"]),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Написать новый текст", callback_data="new_article")]
            ])
        )

    elif data == "new_article":
        if not await check_limit_and_offer_premium(update, context):
            return

        lang = user_data.get("lang", DEFAULT_LANGUAGE)
        user_data.clear()
        user_data["lang"] = lang
        await query.message.reply_text(
            translate("choose_type", lang),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍 Рекламная", callback_data="type_ad")],
                [InlineKeyboardButton("🔍 SEO-текст", callback_data="type_seo")],
                [InlineKeyboardButton("🎉 Поздравление", callback_data="type_congrats")],
            ])
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    lang = user_data.get("lang", DEFAULT_LANGUAGE)
    text = update.message.text.strip()

    if "awaiting_custom_length" in user_data:
        if text.isdigit():
            val = int(text)
            if 100 <= val <= 4000:
                user_data["length"] = val
                user_data.pop("awaiting_custom_length")
                await update.message.reply_text(translate("choose_style", lang), reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔥 Продающий", callback_data="style_sell")],
                    [InlineKeyboardButton("😊 Дружелюбный", callback_data="style_friendly")],
                    [InlineKeyboardButton("📚 Информационный", callback_data="style_info")],
                ]))
            else:
                await update.message.reply_text(translate("wrong_length", lang))
        else:
            await update.message.reply_text(translate("wrong_length", lang))

    elif "type" in user_data and "keywords" not in user_data:
        user_data["keywords"] = text
        await update.message.reply_text(translate("choose_length", lang), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ До 500", callback_data="length_500")],
            [InlineKeyboardButton("📄 До 1000", callback_data="length_1000")],
            [InlineKeyboardButton("📜 До 1500", callback_data="length_1500")],
            [InlineKeyboardButton("📝 Другая длина", callback_data="length_custom")],
        ]))
