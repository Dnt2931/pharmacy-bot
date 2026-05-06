import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import database, models

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN      = os.getenv("BOT_TOKEN")
WEBAPP_URL     = os.getenv("WEBAPP_URL")        # Your hosted web app URL
PHARMACY_CHAT  = os.getenv("PHARMACY_CHAT_ID")

# ── /start ─────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [[
        InlineKeyboardButton(
            "🛒 Open Medicine Shop",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Welcome Dr. *{user.first_name}*!\n\n"
        f"🏥 *Pharmacy Ordering System*\n\n"
        f"Tap the button below to browse medicines,\n"
        f"check prices & profit margins, and place orders.\n\n"
        f"📦 Your orders will be processed and delivered promptly.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ── /orders ────────────────────────────────────────────────
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = database.SessionLocal()

    orders = db.query(models.Order).filter(
        models.Order.doctor_telegram_id == str(user.id)
    ).order_by(models.Order.created_at.desc()).limit(5).all()

    db.close()

    if not orders:
        await update.message.reply_text("📭 You have no orders yet.")
        return

    status_emoji = {
        "pending": "⏳",
        "processing": "🔄",
        "delivered": "✅",
        "cancelled": "❌"
    }

    msg = "📋 *Your Recent Orders:*\n\n"
    for o in orders:
        emoji = status_emoji.get(o.status, "📦")
        msg += f"{emoji} *Order #{o.id}* — Rs.{o.total_amount:,.0f}\n"
        msg += f"   Status: `{o.status}`\n"
        msg += f"   Date: {o.created_at.strftime('%d %b %Y %H:%M')}\n\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ── /help ──────────────────────────────────────────────────
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 *Available Commands:*\n\n"
        "/start — Open the medicine shop\n"
        "/orders — View your recent orders\n"
        "/help — Show this help message",
        parse_mode="Markdown"
    )

# ── MAIN ───────────────────────────────────────────────────
def main():
    database.create_tables()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("orders", my_orders))
    app.add_handler(CommandHandler("help", help_cmd))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
