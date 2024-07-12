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
from config.config import TOKEN
from handlers.handlers import (
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
    handle_sub_choice,
    add_user,
    admin_panel,
    cancelled_handle_back_button,
    handle_states
)
from utilities.texts import (
    THREE_M_SUB_TEXT,
    SIX_M_SUB_TEXT,
    TWELVE_M_SUB_TEXT,
    BUY_FOR_SELF_TEXT,
    BUY_PREMIUM_TEXT,
    FAQ_TEXT,
    MY_PURCHASES_TEXT,
    GO_BACK_TEXT,
    START_TEXT,
    ADMIN_PANEL_TEXT,
)
from db.dbconn import conn, cur


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
    sub_choice_handler = CallbackQueryHandler(handle_sub_choice, pattern=r"^sub:\d+m")
    admin_panel_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{ADMIN_PANEL_TEXT}$"),
        admin_panel,
    )
    inline_keyboard_go_back_handler = CallbackQueryHandler(
        cancelled_handle_back_button, pattern="^go_back$"
    )
    handle_states_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_states)
    app.add_handler(TypeHandler(Update, process_update), group=-1)

    app.add_handlers(
        [
            handle_states_handler,
            start_handler,
            # admin_panel_handler,
            # show_users_handler,
            # toggle_status_handler,
            # buy_sub_handler,
            # subs_list_handler,
            # buy_self_handler,
            buy_success_handler,
            # faq_handler,
            # my_subs_handler,
            go_back_handler,
            status_handler,
            # handle_text_message_handler,
            sub_choice_handler,
            inline_keyboard_go_back_handler,
        ]
    )

    app.run_polling()


if __name__ == "__main__":
    main()

    cur.close()
    conn.close()
