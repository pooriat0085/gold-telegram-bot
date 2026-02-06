import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔹 توکن ربات از Environment Variable
TOKEN = os.environ.get("8284658183:AAHE1hWg-Mxa1npOFu96bwdlbQcFs0oE8f8")
SELLER_PROFIT = 0.07  # سود مغازه‌دار ثابت 7٪

# تابع گرفتن قیمت طلای 18 عیار
def get_gold_price():
    url = "https://api.tgju.org/v1/data/price"
    try:
        data = requests.get(url, timeout=10).json()
        return int(data["data"]["geram18"]["p"])
    except:
        # fallback اگر API مشکل داشت
        return 11470000

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 خوش آمدید به ربات محاسبه قیمت طلا!\n\n"
        "لطفاً وزن طلا (گرم) را وارد کنید:"
    )

# دریافت پیام کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # مرحله 1: وزن
    if "weight" not in context.user_data:
        try:
            context.user_data["weight"] = float(text)
            await update.message.reply_text(
                "درصد اجرت ساخت را وارد کنید (مثال: 18):"
            )
        except:
            await update.message.reply_text("❌ لطفاً وزن را به عدد وارد کنید")
        return

    # مرحله 2: اجرت + محاسبه
    if "wage" not in context.user_data:
        try:
            wage_percent = float(text)
            context.user_data["wage"] = wage_percent

            weight = context.user_data["weight"]
            gold_price = get_gold_price()

            base_price = weight * gold_price
            wage_price = base_price * (wage_percent / 100)
            subtotal = base_price + wage_price
            profit = subtotal * SELLER_PROFIT
            final_price = subtotal + profit

            await update.message.reply_text(
                f"💰 محاسبه قیمت طلا\n\n"
                f"🔹 وزن: {weight} گرم\n"
                f"🔹 قیمت روز ۱۸ عیار: {gold_price:,} تومان\n\n"
                f"➕ اجرت ({wage_percent}%): {int(wage_price):,} تومان\n"
                f"➕ سود فروشنده (7%): {int(profit):,} تومان\n"
                f"━━━━━━━━━━━━━━\n"
                f"✅ قیمت نهایی: {int(final_price):,} تومان"
            )

            context.user_data.clear()
        except:
            await update.message.reply_text("❌ لطفاً درصد اجرت را عددی وارد کنید")

# تابع main
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
