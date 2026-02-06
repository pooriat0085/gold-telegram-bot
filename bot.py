import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("8508837678:AAEW52Cy28MoOM1Zw8-ARiZ0yqo8VYjshGE")
SELLER_PROFIT = 0.07


def get_gold_price():
    url = "https://api.tgju.org/v1/data/price"
    data = requests.get(url, timeout=10).json()
    return int(data["data"]["geram18"]["p"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "👋 خوش آمدید\n\nلطفاً وزن طلا (گرم) را وارد کنید:"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "weight" not in context.user_data:
        try:
            context.user_data["weight"] = float(text)
            await update.message.reply_text("درصد اجرت ساخت را وارد کنید:")
        except:
            await update.message.reply_text("❌ وزن باید عدد باشد")
        return

    try:
        wage_percent = float(text)
        weight = context.user_data["weight"]
        gold_price = get_gold_price()

        base = weight * gold_price
        wage = base * (wage_percent / 100)
        subtotal = base + wage
        profit = subtotal * SELLER_PROFIT
        final = subtotal + profit

        await update.message.reply_text(
            f"💰 محاسبه قیمت طلا\n\n"
            f"وزن: {weight} گرم\n"
            f"قیمت روز: {gold_price:,} تومان\n"
            f"اجرت ({wage_percent}%): {int(wage):,}\n"
            f"سود فروشنده (7%): {int(profit):,}\n"
            f"━━━━━━━━━━━━\n"
            f"قیمت نهایی:\n{int(final):,} تومان"
        )

        context.user_data.clear()

    except:
        await update.message.reply_text("❌ درصد اجرت باید عدد باشد")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
