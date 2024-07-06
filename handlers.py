import json
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from database import get_db_connection
from utils import push_menu, is_valid_username
import requests
from currencyapi import (
    three_month_price,
    six_month_price,
    twelve_month_price,
    update_data,
)
from texts import (
    BUY_PREMIUM_TEXT,
    BUY_FOR_SELF_TEXT,
    BUY_FOR_FRIENDS_TEXT,
    BUY_SUCCESS_TEXT,
    LOREM,
    FAQ_TEXT,
    MY_PURCHASES_TEXT,
    GO_BACK_TEXT,
    THREE_M_SUB_TEXT,
    SIX_M_SUB_TEXT,
    TWELVE_M_SUB_TEXT,
    PENDING_APPROVAL_TEXT,
    APPROVED_TEXT,
    CANCELLED_TEXT,
    REVIEWING_TEXT,
    CHOOSE_USERNAME_ERROR_TEXT,
    SUB_HELP_TEXT,
    WELCOME_TEXT,
    CHOOSE_OPTION_TEXT,
    INVALID_OPTION_TEXT,
    FAILED_UPDATE_STATUS_TEXT,
    ERROR_SENDING_PHOTO,
    UNKNOWN_TEXT,
    NO_SUB_TEXT,
    USERNAME_LIMITS_TEXT,
    STATUS_UPDATED_TEXT,
)
from config import ADMIN_CHAT_ID
import uuid
from dbconn import conn, cur
from ridi import redis_conn


from session import set_session, get_session, delete_session


def push_menu(user_id: str, menu_function):
    redis_conn.rpush(f"menu_stack:{user_id}", menu_function.__name__)


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    menu_stack_key = f"menu_stack:{user_id}"

    if redis_conn.llen(menu_stack_key) > 0:
        menu_function_name = redis_conn.rpop(menu_stack_key)
        if menu_function_name:
            menu_function = globals().get(menu_function_name)
            if menu_function:
                await menu_function(update, context)
    else:
        await start(update, context)


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = update.effective_user
    user_id = str(user_data.id)  # Cast to string
    user_username = user_data.username
    user_first_name = user_data.first_name
    user_last_name = user_data.last_name

    # Check if the user already exists
    cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    existing_user = cur.fetchone()

    if not existing_user:
        cur.execute(
            "INSERT INTO users (id, username, first_name, last_name) VALUES (%s, %s,%s,%s)",
            (user_id, user_username, user_first_name, user_last_name),
        )
        conn.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    push_menu(user_id, start)
    update_data()

    start_keys = [
        [
            KeyboardButton(text=BUY_PREMIUM_TEXT),
            KeyboardButton(text=MY_PURCHASES_TEXT),
        ],
        [
            KeyboardButton(text=FAQ_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(start_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=WELCOME_TEXT, reply_markup=markup
    )


async def buy_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    buy_keys = [
        [KeyboardButton(text=BUY_FOR_SELF_TEXT)],
    ]
    markup = ReplyKeyboardMarkup(buy_keys, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=SUB_HELP_TEXT,
        reply_markup=markup,
    )
    set_session(user_id, "awaiting_username", "true")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if get_session(user_id, "awaiting_username") == "true":
        if text == BUY_FOR_SELF_TEXT:
            user_data = update.effective_user
            username = user_data.username
            set_session(user_id, "entered_username", username)
            delete_session(user_id, "awaiting_username")
            await subs_list(update, context)  # Proceed to the subscription list
        else:
            if is_valid_username(text):
                set_session(user_id, "entered_username", text)
                delete_session(user_id, "awaiting_username")
                await subs_list(update, context)  # Proceed to the subscription list
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=USERNAME_LIMITS_TEXT,
                )
    else:
        # Handle other text messages here
        pass


async def subs_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    push_menu(user_id, buy_sub)

    subs_list_keys = [
        [
            InlineKeyboardButton(text=THREE_M_SUB_TEXT, callback_data="sub:3m"),
        ],
        [
            InlineKeyboardButton(text=SIX_M_SUB_TEXT, callback_data="sub:6m"),
        ],
        [
            InlineKeyboardButton(text=TWELVE_M_SUB_TEXT, callback_data="sub:12m"),
        ],
    ]
    markup = InlineKeyboardMarkup(subs_list_keys)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=CHOOSE_OPTION_TEXT, reply_markup=markup
    )


async def handle_sub_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "sub:3m":
        set_session(user_id, "sub_choice", THREE_M_SUB_TEXT)
        set_session(user_id, "sub_price", str(three_month_price))  # Store as string
    elif data == "sub:6m":
        set_session(user_id, "sub_choice", SIX_M_SUB_TEXT)
        set_session(user_id, "sub_price", str(six_month_price))  # Store as string
    elif data == "sub:12m":
        set_session(user_id, "sub_choice", TWELVE_M_SUB_TEXT)
        set_session(user_id, "sub_price", str(twelve_month_price))  # Store as string
    else:
        await query.edit_message_text(text=INVALID_OPTION_TEXT)
        return

    await buy_for_self(update, context)


async def buy_for_self(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    push_menu(user_id, subs_list)

    user_data = (
        update.callback_query.from_user
        if update.callback_query
        else update.message.from_user
    )

    invoice_title = get_session(user_id, "sub_choice")
    invoice_price = get_session(user_id, "sub_price")

    if not invoice_title or not invoice_price:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="خطا")
        return

    # Check if the username was entered earlier; if not, use the Telegram username
    username = get_session(user_id, "entered_username")
    if not username:
        username = user_data.username
    else:
        # Clear the custom username after using it
        delete_session(user_id, "entered_username")

    invoice_username = f"@{username}"

    # Process the invoice creation
    invoice_details = {
        "title": invoice_title,
        "description": invoice_username,
        "price": invoice_price,
    }

    set_session(user_id, "invoice_details", json.dumps(invoice_details))

    # Send the invoice or next steps here
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"""🧾 فاکتور شما ایجاد شد. 

    💢 درخواست: {invoice_title} 

    🛍 مبلغ فاکتور: {invoice_price} تومان

    ✅ قابل پرداخت: {invoice_price} تومان
    🔸 شماره کارت: 
    12345678998765432

    برای یوزر نیم : {invoice_username}


    📌 لطفا اسکرین شات واریزی را برای ربات ارسال نمایید""",
    )


# async def handle_username_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.effective_user.id)
#     query = update.callback_query
#     await query.answer()
#     data = query.data

#     if data == "use_telegram_username":
#         # Retrieve username from Telegram user data
#         user_data = update.effective_user
#         username = user_data.username
#         redis_conn.set(f"entered_username:{user_id}", username)
#         redis_conn.set(f"awaiting_username:{user_id}", "false")
#         await subs_list(update, context)  # Proceed to the subscription list
#     elif data == "go_back":
#         await go_back(update, context)
#     else:
#         await query.edit_message_text(text=INVALID_OPTION_TEXT)


async def update_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")

    invoice_id = data[1]
    new_status = data[2]

    if new_status == "Pending Approval":
        persian_new_status = PENDING_APPROVAL_TEXT
    elif new_status == "Reviewing":
        persian_new_status = REVIEWING_TEXT
    elif new_status == "Approved":
        persian_new_status = APPROVED_TEXT
    else:
        persian_new_status = CANCELLED_TEXT

    try:
        # Fetch the invoice to check if it exists
        cur.execute("SELECT id, sub FROM invoice WHERE invoice_id = %s", (invoice_id,))
        result = cur.fetchall()
        print(result)
        user_chat_id, sub_name = result[0]

        if result:
            # Update the status in the database
            cur.execute(
                "UPDATE invoice SET status = %s WHERE invoice_id = %s",
                (new_status, invoice_id),
            )
            conn.commit()

            # Get the existing caption and remove any existing status update
            existing_caption = query.message.caption if query.message.caption else ""
            if STATUS_UPDATED_TEXT in existing_caption:
                existing_caption = existing_caption.split(f"\n{STATUS_UPDATED_TEXT}")[0]

            updated_caption = (
                f"{existing_caption}\n\n{STATUS_UPDATED_TEXT}{persian_new_status}"
            )

            # Define the inline keyboard based on the new status
            inline_keyboard = []
            if new_status == "Pending Approval":
                inline_keyboard = [
                    [
                        InlineKeyboardButton(
                            text=REVIEWING_TEXT,
                            callback_data=f"status:{invoice_id}:Reviewing",
                        ),
                        InlineKeyboardButton(
                            text=CANCELLED_TEXT,
                            callback_data=f"status:{invoice_id}:Canceled",
                        ),
                    ]
                ]
            elif new_status == "Reviewing":
                inline_keyboard = [
                    [
                        InlineKeyboardButton(
                            text=APPROVED_TEXT,
                            callback_data=f"status:{invoice_id}:Approved",
                        ),
                        InlineKeyboardButton(
                            text=CANCELLED_TEXT,
                            callback_data=f"status:{invoice_id}:Canceled",
                        ),
                    ]
                ]
            elif new_status == "Approved":
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=f"مشتری گرامی درخواست '{sub_name}' شما تایید شد",
                )
                delete_session(user_chat_id, "invoice_details")
                inline_keyboard = []
            elif new_status == "Canceled":
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=f"مشتری گرامی درخواست '{sub_name}' شما لغو شد",
                )
                delete_session(user_chat_id, "invoice_details")

                inline_keyboard = []

            reply_markup = (
                InlineKeyboardMarkup(inline_keyboard) if inline_keyboard else None
            )

            # Update the message caption and buttons
            await query.edit_message_caption(
                caption=updated_caption,
                reply_markup=reply_markup,
            )
        else:
            await query.edit_message_caption(
                caption="Invoice not found.", reply_markup=query.message.reply_markup
            )
    except Exception as e:
        await query.edit_message_caption(
            caption=f"{FAILED_UPDATE_STATUS_TEXT}\nError: {str(e)}",
            reply_markup=query.message.reply_markup,
        )


async def buy_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.effective_message.text
    chat_id = update.effective_chat.id
    photo = update.message.photo
    print(text)
    if photo:
        admin_chat_id = ADMIN_CHAT_ID

        try:
            invoice_details_str = get_session(user_id, "invoice_details")
            if not invoice_details_str:
                raise ValueError("Invoice details not found in Redis")

            # Deserialize the invoice details
            invoice_details = json.loads(invoice_details_str)

            invoice_id = str(uuid.uuid4())[:8]  # Generate a random invoice_id

            user_data = update.message.from_user
            user_id = user_data.id
            user_username = user_data.username
            user_sub = invoice_details.get("title", "N/A")

            if user_username:
                cur.execute(
                    "INSERT INTO invoice (id, username, sub, status, invoice_id) VALUES (%s, %s, %s, NULL, %s)",
                    (user_id, user_username, user_sub, invoice_id),
                )
                conn.commit()
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=CHOOSE_USERNAME_ERROR_TEXT,
                )
                return

            file_id = photo[-1].file_id

            invoice_text = f"""**فاکتور**

درخواست : {invoice_details.get('title', 'N/A')}
یوزر نیم : {invoice_details.get('description', 'N/A')}
قیمت : {invoice_details.get('price', 'N/A')} ت
شماره فاکتور : {invoice_id}"""

            inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text=PENDING_APPROVAL_TEXT,
                        callback_data=f"status:{invoice_id}:Pending Approval",
                    ),
                    InlineKeyboardButton(
                        text=CANCELLED_TEXT,
                        callback_data=f"status:{invoice_id}:Canceled",
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(inline_keyboard)

            await context.bot.send_photo(
                chat_id=admin_chat_id,
                photo=file_id,
                caption=invoice_text,
                reply_markup=reply_markup,
            )

        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ERROR_SENDING_PHOTO,
            )


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    push_menu(user_id, start)

    faq_keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(faq_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=LOREM, reply_markup=markup
    )


async def my_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    push_menu(user_id, start)

    user_data = update.message.from_user
    user_id = user_data["id"]

    cur.execute(
        "SELECT username, sub, created, status FROM invoice WHERE id = %s",
        (str(user_id),),
    )
    user_data = cur.fetchall()

    if user_data:
        status_translation = {
            "Pending Approval": PENDING_APPROVAL_TEXT,
            "Reviewing": REVIEWING_TEXT,
            "Approved": APPROVED_TEXT,
            "Canceled": CANCELLED_TEXT,
            None: UNKNOWN_TEXT,
        }
        subs_list = "\n".join(
            [
                f"- @{username}: {sub} Premium (Created on: {created.strftime('%Y-%m-%d %H:%M:%S')}) - Status: {status_translation.get(status, UNKNOWN_TEXT)}"
                for username, sub, created, status in user_data
            ]
        )
        response_message = f"اشتراک‌های شما:\n{subs_list}"
    else:
        response_message = NO_SUB_TEXT

    my_subs_keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(my_subs_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=response_message, reply_markup=markup
    )
