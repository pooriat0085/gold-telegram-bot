import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

WEIGHT, FEE = range(2)

# توکن مستقیم
TOKEN = "8284658183:AAFgcMKcyVVUT0MwTsCrxqj6yF_pt8c8Yb8"  # <-- اینجا توکن خودت رو بذار

def fetch_gold_price():
    try:
        res = requests.get("https://goldpricez.com/ir/18k/gram")
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.find("div", {"class": "live-price"}).text
        price = int(text.replace(",", "").strip())
        return price
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! وزن طلای مورد نظرت رو به گرم بنویس:")
    return WEIGHT

async def get_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["weight"] = float(update.message.text)
        await update.message.reply_text("حالا درصد اجرت رو بگو:")
        return FEE
    except:
        await update.message.reply_text("لطفا عدد معتبر وارد کن!")
        return WEIGHT

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        fee = float(update.message.text)
        weight = context.user_data["weight"]
        price_per_gram = fetch_gold_price()
        if price_per_gram is None:
            await update.message.reply_text("مشکل در دریافت قیمت طلا 😕 لطفا بعداً امتحان کن.")
            return ConversationHandler.END

        base = price_per_gram * weight
        with_fee = base * (1 + fee / 100)
        final_price = with_fee * 1.07
        await update.message.reply_text(f"💰 قیمت نهایی: {final_price:,.0f} ریال")
        return ConversationHandler.END
    except:
        await update.message.reply_text("عدد معتبر وارد کن لطفاً!")
        return FEE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_weight)],
            FEE: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()
