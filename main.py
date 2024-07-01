from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    TypeHandler,
    ContextTypes,
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
    handle_text_message,
    handle_username_choice,
    handle_sub_choice,
    add_user,
)
from texts import (
    THREE_M_SUB_TEXT,
    SIX_M_SUB_TEXT,
    TWELVE_M_SUB_TEXT,
    BUY_FOR_SELF_TEXT,
    BUY_PREMIUM_TEXT,
    FAQ_TEXT,
    MY_PURCHASES_TEXT,
    GO_BACK_TEXT,
    START_TEXT,
)
from dbconn import conn, cur


async def process_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_user(update, context)


def main():
    app = Application.builder().token(TOKEN).build()

    start_handler = CommandHandler(START_TEXT, start)
    buy_sub_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{BUY_PREMIUM_TEXT}$"), buy_sub
    )
    subs_list_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{BUY_FOR_SELF_TEXT}$"), subs_list
    )
    buy_self_handler = MessageHandler(
        filters.TEXT
        & (
            filters.Regex(f"^{THREE_M_SUB_TEXT}$")
            | filters.Regex(f"^{SIX_M_SUB_TEXT}$")
            | filters.Regex(f"^{TWELVE_M_SUB_TEXT}$")
        ),
        buy_for_self,
    )
    buy_success_handler = MessageHandler(
        filters.PHOTO,
        buy_success,
    )
    faq_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{FAQ_TEXT}$"),
        faq,
    )
    my_subs_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{MY_PURCHASES_TEXT}$"),
        my_subs,
    )
    go_back_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{GO_BACK_TEXT}$"),
        go_back,
    )
    status_handler = CallbackQueryHandler(update_status, pattern="^status:")

    handle_text_message_handler = MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_text_message
    )
    handle_username_choice_handler = CallbackQueryHandler(
        handle_username_choice, pattern="^use_telegram_username|go_back$"
    )
    sub_choice_handler = CallbackQueryHandler(handle_sub_choice, pattern=r"^sub:\d+m")

    app.add_handler(TypeHandler(Update, process_update), group=-1)

    app.add_handlers(
        [
            start_handler,
            buy_sub_handler,
            subs_list_handler,
            buy_self_handler,
            buy_success_handler,
            faq_handler,
            my_subs_handler,
            go_back_handler,
            status_handler,
            handle_text_message_handler,
            handle_username_choice_handler,
            sub_choice_handler,
        ]
    )

    app.run_polling()


if __name__ == "__main__":
    main()

    cur.close()
    conn.close()
