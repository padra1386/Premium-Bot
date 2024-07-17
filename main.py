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
    go_back_handle,
    handle_states,
    faq_callback,
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
    buy_success_handler = MessageHandler(
        filters.PHOTO,
        buy_success,
    )
    go_back_handler = MessageHandler(
        filters.TEXT & filters.Regex(f"^{GO_BACK_TEXT}$"),
        go_back,
    )
    status_handler = CallbackQueryHandler(update_status, pattern="^status:")

    sub_choice_handler = CallbackQueryHandler(
        handle_sub_choice, pattern=r"^sub:\d+m")

    inline_keyboard_go_back_handler = CallbackQueryHandler(
        go_back_handle, pattern="^go_back$"
    )

    faq_callback_handler = CallbackQueryHandler(faq_callback, pattern="^faq_")
    faq_go_back_handler = CallbackQueryHandler(
        faq_callback, pattern="^go_back_faq$")
    cancelled_message_go_back = CallbackQueryHandler(
        go_back_handle, pattern="^go_back_cancelled$"
    )
    handle_states_handler = MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_states
    )
    app.add_handler(TypeHandler(Update, process_update), group=-1)

    app.add_handlers(
        [
            handle_states_handler,
            start_handler,
            buy_success_handler,
            go_back_handler,
            status_handler,
            sub_choice_handler,
            inline_keyboard_go_back_handler,
            faq_go_back_handler,
            faq_callback_handler,
            cancelled_message_go_back,
        ]
    )

    app.run_polling()


if __name__ == "__main__":
    main()

    cur.close()
    conn.close()
