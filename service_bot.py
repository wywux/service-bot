import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------- НАСТРОЙКИ (заполни своими данными) ----------

BOT_TOKEN = os.getenv("BOT_TOKEN", "8842439967:AAGVc8_EGZ7B04d-mx9OT1SWerJt7sh3MXk")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "8545303049")
PORTFOLIO_LINK = "https://t.me/ivan_porfolio"

SERVICES_TEXT = (
    "🤖 *Услуги по разработке Telegram-ботов*\n\n"
    "*Простые боты* — 1000–3000₽\n"
    "Меню, опросы, приём заявок, простые рассылки\n\n"
    "*Боты средней сложности* — 3000–10000₽\n"
    "Интеграции с базами данных, приём оплат, запись на услуги, каталоги\n\n"
    "*Сложные боты* — 10000–25000₽\n"
    "Нейросетевые функции, комплексные системы, интеграции с внешними API\n\n"
    "Работаю «под ключ»: от идеи до запуска и поддержки."
)

ABOUT_TEXT = (
    "👋 Привет! Я делаю Telegram-ботов под задачи бизнеса и частных клиентов.\n"
    "Пишу код сам, помогаю с идеей и запуском, даю консультацию перед стартом проекта."
)

# состояния диалога заявки
DESCRIBING, CONTACT = range(2)

logging.basicConfig(level=logging.INFO)


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Услуги и цены", callback_data="services")],
        [InlineKeyboardButton("👤 Обо мне", callback_data="about")],
        [InlineKeyboardButton("🗂 Портфолио", url=PORTFOLIO_LINK)],
        [InlineKeyboardButton("✉️ Оставить заявку", callback_data="order")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать! Выберите, что вас интересует:",
        reply_markup=main_menu_keyboard(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "services":
        await query.edit_message_text(
            SERVICES_TEXT, parse_mode="Markdown", reply_markup=main_menu_keyboard()
        )
    elif query.data == "about":
        await query.edit_message_text(
            ABOUT_TEXT, reply_markup=main_menu_keyboard()
        )
    elif query.data == "order":
        await query.edit_message_text(
            "Опишите, пожалуйста, задачу: что должен делать бот, "
            "и любые пожелания по срокам и бюджету."
        )
        return DESCRIBING


async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    await update.message.reply_text(
        "Спасибо! Теперь оставьте контакт для связи (телефон, @username или e-mail)."
    )
    return CONTACT


async def receive_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.text
    description = context.user_data.get("description", "—")
    user = update.effective_user

    order_text = (
        f"📩 *Новая заявка*\n\n"
        f"От: {user.full_name} (@{user.username})\n"
        f"Описание задачи: {description}\n"
        f"Контакт: {contact}"
    )

    if ADMIN_CHAT_ID and "ВСТАВЬ" not in ADMIN_CHAT_ID:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=order_text, parse_mode="Markdown")

    await update.message.reply_text(
        "Заявка принята! Я свяжусь с вами в ближайшее время. 🙌",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заявка отменена.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^order$")],
        states={
            DESCRIBING: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
