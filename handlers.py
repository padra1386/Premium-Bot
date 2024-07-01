from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from database import get_db_connection
from utils import push_menu
import requests
from currencyapi import three_month_price, six_month_price, twelve_month_price
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
)
from config import ADMIN_CHAT_ID
import uuid
from dbconn import conn, cur


def push_menu(context: ContextTypes.DEFAULT_TYPE, menu_function):
    if "menu_stack" not in context.user_data:
        context.user_data["menu_stack"] = []
    context.user_data["menu_stack"].append(menu_function)


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "menu_stack" in context.user_data and context.user_data["menu_stack"]:
        menu_function = context.user_data["menu_stack"].pop()
        await menu_function(update, context)
    else:
        await start(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    push_menu(context, start)

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
    push_menu(context, start)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=SUB_HELP_TEXT,
    )

    buy_keys = [
        [
            InlineKeyboardButton(
                text=BUY_FOR_SELF_TEXT, callback_data="use_telegram_username"
            ),
        ],
    ]
    markup = InlineKeyboardMarkup(buy_keys)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=CHOOSE_OPTION_TEXT,
        reply_markup=markup,
    )
    context.user_data["awaiting_username"] = (
        True  # Flag to indicate that we are waiting for the username
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_username"):
        username = update.message.text
        context.user_data["entered_username"] = username
        context.user_data["awaiting_username"] = False
        await subs_list(update, context)  # Proceed to the subscription list
    else:
        # Handle other text messages here
        pass


async def subs_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, buy_sub)

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
    print("Subs list sent with buttons: ", subs_list_keys)  # Debugging line


async def handle_sub_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    print(f"Received callback data: {data}")  # Debugging line

    if data == "sub:3m":
        context.user_data["sub_choice"] = THREE_M_SUB_TEXT
        context.user_data["sub_price"] = three_month_price
    elif data == "sub:6m":
        context.user_data["sub_choice"] = SIX_M_SUB_TEXT
        context.user_data["sub_price"] = six_month_price
    elif data == "sub:12m":
        context.user_data["sub_choice"] = TWELVE_M_SUB_TEXT
        context.user_data["sub_price"] = twelve_month_price
    else:
        print(f"Invalid option received: {data}")  # Debugging line
        await query.edit_message_text(text=INVALID_OPTION_TEXT)
        return

    await buy_for_self(update, context)


async def buy_for_self(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, subs_list)
    user_data = (
        update.callback_query.from_user
        if update.callback_query
        else update.message.from_user
    )

    invoice_title = context.user_data.get("sub_choice")
    invoice_price = context.user_data.get("sub_price")

    if not invoice_title or not invoice_price:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="خطا")
        return

    username = context.user_data.get("entered_username", user_data.username)

    invoice_description = f"@{username} اشتراک یک ماهه برای نام کاربری"

    # Process the invoice creation
    invoice_details = {
        "title": invoice_title,
        "description": invoice_description,
        "price": invoice_price,
    }

    context.user_data["invoice_details"] = invoice_details

    # Send the invoice or next steps here
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"""**Invoice**

Title: {invoice_title}
Description: {invoice_description}
Price: {invoice_price} ت

Please wait while we process your subscription.""",
    )

    # Proceed with the rest of the invoice creation and processing steps...


async def handle_username_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "use_telegram_username":
        # Retrieve username from Telegram user data
        user_data = update.effective_user
        username = user_data.username
        context.user_data["entered_username"] = username
        context.user_data["awaiting_username"] = False
        await subs_list(update, context)  # Proceed to the subscription list
    elif data == "go_back":
        await go_back(update, context)
    else:
        await query.edit_message_text(text=INVALID_OPTION_TEXT)


async def update_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")
    if len(data) == 3 and data[0] == "status":
        invoice_id = data[1]
        new_status = data[2]

        try:

            cur.execute(
                "UPDATE invoice SET status = %s WHERE invoice_id = %s",
                (new_status, invoice_id),
            )
            conn.commit()

            # Get the existing caption
            existing_caption = query.message.caption if query.message.caption else ""

            # Append the status update to the existing caption
            updated_caption = f"{existing_caption}\n\nUpdated status to: {new_status}"

            # Update the message caption without removing inline buttons
            await query.edit_message_caption(
                caption=updated_caption,
                reply_markup=query.message.reply_markup,
            )

        except Exception as e:
            print(f"Error updating status: {e}")
            await query.edit_message_caption(
                caption=FAILED_UPDATE_STATUS_TEXT,
                reply_markup=query.message.reply_markup,
            )
    else:
        await query.edit_message_caption(
            caption="Invalid action.", reply_markup=query.message.reply_markup
        )


# Add this to the function that sends the invoice to the admin
async def buy_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text
    photo = update.message.photo

    if photo:
        admin_chat_id = ADMIN_CHAT_ID

        try:
            invoice_details = context.user_data.get("invoice_details", {})
            invoice_id = str(uuid.uuid4())[:8]  # Generate a random invoice_id

            user_data = update.message.from_user
            print(user_data)
            user_id = user_data["id"]
            user_username = user_data["username"]
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

            invoice_text = f"""**Invoice**

Title: {invoice_details.get('title', 'N/A')}
Description: {invoice_details.get('description', 'N/A')}
Price: {invoice_details.get('price', 'N/A')} ت
Invoice ID: {invoice_id}"""

            inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text=PENDING_APPROVAL_TEXT,
                        callback_data=f"status:{invoice_id}:Pending Approval",
                    ),
                    InlineKeyboardButton(
                        text=REVIEWING_TEXT,
                        callback_data=f"status:{invoice_id}:Reviewing",
                    ),
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
            reply_markup = InlineKeyboardMarkup(inline_keyboard)

            await context.bot.send_photo(
                chat_id=admin_chat_id,
                photo=file_id,
                caption=invoice_text,
                reply_markup=reply_markup,
            )

        except Exception as e:
            print(f"Error sending photo to admin: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ERROR_SENDING_PHOTO,
            )


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, start)

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
    push_menu(context, start)

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
