from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from config import TOKEN
from handlers import (
    start,
    buy_sub,
    buy_for_self,
    buy_success,
    faq,
    my_subs,
    go_back,
    subs_list,
    update_status,
)
from currencyapi import three_month_price
from texts import THREE_M_SUB_TEXT, SIX_M_SUB_TEXT, TWELVE_M_SUB_TEXT, BUY_FOR_SELF_TEXT


def main():
    app = Application.builder().token(TOKEN).build()

    start_handler = CommandHandler("start", start)
    buy_sub_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^🛍️ خرید پرمیوم تلگرام$"), buy_sub
    )
    subs_list_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{BUY_FOR_SELF_TEXT}$"), subs_list
    )
    buy_self_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{THREE_M_SUB_TEXT}$")
        | filters.Regex(f"^{SIX_M_SUB_TEXT}$")
        | filters.Regex(f"^{TWELVE_M_SUB_TEXT}$"),
        buy_for_self,
    )
    buy_success_handler = MessageHandler(
        filters.PHOTO,
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
    status_handler = CallbackQueryHandler(update_status, pattern="^status:")

    app.add_handlers(
        [
            start_handler,
            buy_sub_handler,
            buy_self_handler,
            buy_success_handler,
            faq_handler,
            my_subs_handler,
            go_back_handler,
            subs_list_handler,
            status_handler,
        ]
    )

    app.run_polling()


if __name__ == "__main__":
    main()
