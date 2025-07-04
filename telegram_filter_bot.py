import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Bot configuration
token = "7761588983:AAEUBpkOxAS9g4yrXbNQifSUlRq9BTpkBPg"
owner_id = 7461521365

# List of forbidden words
swears = [
    "sik", "amcıx", "peyser", "qəhbə", "qehbe", "oğlum", "pidr", "gey",
    "gicdilaağ", "gicdilax", "petux", "sikimi", "ata", "atan", "oglum",
    "oğlumsan", "anandi", "atandi", "bic", "bicbala", "skdir", "skm",
    "bləə", "aybile", "aybilət", "yobana", "siktir", "pidaras", "pedaras",
    "piç", "s.k.m", "blee", "geysən", "gaysan", "peysərsən", "ayble",
    "petuxsan", "vizqirt", "vzt", "siç", "sic", "siçibsan", "pıç", "skim",
    "yiyəsən", "oqlum", "orospu", "çocuğu", "sg", "sk", "sikdir",
    "siydir", "p", "anen", "ana", "seks", "sex", "sikerim",
    "amk", "aq", "oq", "abla", "bacin", "sikərəm", "anavı", "anavi"
]

# In-memory user warning counts
user_warnings = {}

def start_keyboard(bot_username: str):
    contact_button = KeyboardButton("Telefon nömrəmi paylaş", request_contact=True)
    username = bot_username.lstrip('@')
    invite_button = InlineKeyboardButton(
        text="Məni qrupa əlavə et",
        url=f"https://t.me/{username}?startgroup=true"
    )
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
    inline_markup = InlineKeyboardMarkup([[invite_button]])
    return reply_markup, inline_markup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reply_markup, inline_markup = start_keyboard(context.bot.username)
    await update.message.reply_text(
        f"Salam {user.first_name}! Botumuza xoş gəlmisiniz.",
        reply_markup=reply_markup
    )
    await update.message.reply_text(
        "Botu qrupunuza əlavə etmək üçün aşağıdakı düyməni istifadə edin:",
        reply_markup=inline_markup
    )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.effective_user
    phone = contact.phone_number if contact else "(paylaşılmayıb)"
    await context.bot.send_message(
        chat_id=owner_id,
        text=(
            f"Yeni istifadəçi: {user.full_name}\n"
            f"ID: {user.id}\n"
            f"Telefon: {phone}"
        )
    )

async def filter_swears(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.text or ""
    user_id = message.from_user.id
    found = []
    for word in swears:
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            found.append(word)
    if not found:
        return
    try:
        await message.delete()
    except Exception:
        logging.warning(f"Couldn't delete message from {user_id}")
    count = user_warnings.get(user_id, 0) + len(found)
    user_warnings[user_id] = count
    if count >= 5:
        await context.bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply_text(
            f"{message.from_user.first_name}, 5 söyüş xəbərdarlığından sonra susduruldunuz."
        )
    else:
        await message.reply_text(
            f"{message.from_user.first_name}, bu sizin {count}. xəbərdarlığınızdır. Maksimum 5 xəbərdarlıq var."
        )

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_swears))
    app.run_polling()
