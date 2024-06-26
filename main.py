from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from config import TOKEN
from handlers import start, buy_sub, buy_for_self, buy_success, faq, my_subs, go_back
from currencyapi import buy_self_text


def main():
    app = Application.builder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    buy_sub_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^🛍️ خرید پرمیوم تلگرام$"), buy_sub
    )
    buy_self_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^🙋‍♂️ خرید برای خودم$"), buy_for_self
    )
    buy_success_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^خرید اشتراک یک ماهه 300 ت$")
        | filters.Regex(f"^{buy_self_text}$"),
        buy_success,
    )
    faq_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^❓ سوالات پر تکرار$"),
        faq,
    )
    my_subs_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^❇️ درخواست های من$"),
        my_subs,
    )
    go_back_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^🔙 بازگشت$"),
        go_back,
    )

    app.add_handlers(
        [
            start_handler,
            buy_sub_handler,
            buy_self_handler,
            buy_success_handler,
            faq_handler,
            my_subs_handler,
            go_back_handler,
        ]
    )

    app.run_polling()


if __name__ == "__main__":
    main()
