import json
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes
from utilities.utils import (
    push_menu,
    is_valid_username,
    gregorian_to_solar,
    get_total_users,
    get_daily_new_users,
    get_weekly_new_users,
    format_with_commas,
    get_user_purchased,
    sanitize_username,
    get_sell_stats,
    solar_to_gregorian,
    format_solar_date
)
from currencyapi import (
    three_m_price,
    six_m_price,
    twelve_m_price,
    last_price,
    fee_amount,
    profit_amount
)
from utilities.texts import (
    BUY_PREMIUM_TEXT,
    BUY_FOR_SELF_TEXT,
    FAQ_TEXT,
    FAQ_FULL_TEXT,
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
    USERNAME_LIMITS_TEXT,
    STATUS_UPDATED_TEXT,
    ADMIN_PANEL_TEXT,
    cancelled_payment_text,
    cancelled_username_text,
    approved_payment,
    approved,
    USERS_STATS,
    SELL_STATS,
    PHOTO_SENT_SUCCESSFULLY,
    PAY_APPROVED_TEXT,
    SELL_INFO
)
from config import ADMIN_CHAT_ID, PROFIT_AMOUNT, THREE_M_USD_PRICE, NINE_M_USD_PRICE, TWELVE_M_USD_PRICE, FEE_AMOUNT
import uuid
from db.dbconn import conn, cur
from redis_files.redis_connection import redis_conn
from redis_files.states import set_user_state, get_user_state, BotState
from redis_files.session import set_session, get_session, delete_session
from datetime import datetime


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
    set_user_state(user_id, BotState.START)

    start_keys = [
        [
            KeyboardButton(text=BUY_PREMIUM_TEXT),
            KeyboardButton(text=MY_PURCHASES_TEXT),
        ],
        [
            KeyboardButton(text=FAQ_TEXT),
        ],
    ]

    if user_id == ADMIN_CHAT_ID:
        start_keys = [[KeyboardButton(text=ADMIN_PANEL_TEXT)]]

    markup = ReplyKeyboardMarkup(start_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=WELCOME_TEXT, reply_markup=markup
    )


async def buy_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    buy_keys = [
        [KeyboardButton(text=BUY_FOR_SELF_TEXT)],
    ]
    markup = ReplyKeyboardMarkup(
        buy_keys, resize_keyboard=True, one_time_keyboard=True)

    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=SUB_HELP_TEXT,
        reply_markup=markup,
    )
    set_session(user_id, "awaiting_username", "true")
    set_session(user_id, "last_message", message.message_id)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    user_data = update.effective_user
    user_state = get_user_state(user_id)
    last_message_id = get_session(user_id, "last_message")
    if user_state == BotState.BUY_PREMIUM:
        if get_session(user_id, "awaiting_username") == "true":
            if text == BUY_FOR_SELF_TEXT:
                if not user_data.username:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=CHOOSE_USERNAME_ERROR_TEXT,
                    )
                else:
                    username = user_data.username
                    set_session(user_id, "entered_username", username)
                    set_session(user_id, "awaiting_username", "false")
                    set_user_state(user_id, BotState.SUBS_LIST)

                    # Remove the keyboard
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=int(last_message_id),
                    )
                    await subs_list(update, context)
            else:
                if is_valid_username(sanitize_username(text)):
                    text = sanitize_username(text)
                    set_session(user_id, "entered_username", text)
                    set_session(user_id, "awaiting_username", "false")
                    set_user_state(user_id, BotState.SUBS_LIST)

                    # Remove the keyboard
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=int(last_message_id),
                    )

                    # Proceed to the subscription list
                    await subs_list(update, context)
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=USERNAME_LIMITS_TEXT,
                    )
        else:
            # Handle other text messages here
            pass
    else:
        await start(update, context)


async def subs_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    push_menu(user_id, buy_sub)
    user_state = get_user_state(user_id)

    subs_list_keys = [
        [
            InlineKeyboardButton(text=THREE_M_SUB_TEXT,
                                 callback_data="sub:3m"),
        ],
        [
            InlineKeyboardButton(text=SIX_M_SUB_TEXT, callback_data="sub:6m"),
        ],
        [
            InlineKeyboardButton(text=TWELVE_M_SUB_TEXT,
                                 callback_data="sub:12m"),
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
    three_m_invoice_price = int(three_m_price) + \
        int(profit_amount) + int(fee_amount)
    six_m_invoice_price = int(six_m_price) + \
        int(profit_amount) + int(fee_amount)
    twelve_m_invoice_price = int(twelve_m_price) + \
        int(profit_amount) + int(fee_amount)

    if get_user_state(user_id) == BotState.SUBS_LIST:
        if data == "sub:3m":
            set_session(user_id, "sub_choice", THREE_M_SUB_TEXT)
            set_session(user_id, "sub_price", str(
                three_m_invoice_price))  # Store as string
        elif data == "sub:6m":
            set_session(user_id, "sub_choice", SIX_M_SUB_TEXT)
            set_session(user_id, "sub_price", str(
                six_m_invoice_price))  # Store as string
        elif data == "sub:12m":
            set_session(user_id, "sub_choice", TWELVE_M_SUB_TEXT)
            set_session(user_id, "sub_price", str(
                twelve_m_invoice_price))  # Store as string
        else:
            await query.edit_message_text(text=INVALID_OPTION_TEXT)
            return
        set_user_state(user_id, BotState.INVOICE_LIST)
        # Delete the original subs_list message after state change
        await context.bot.delete_message(
            chat_id=update.effective_chat.id, message_id=query.message.message_id
        )
        await buy_for_self(update, context)
    else:
        await start(update, context)


async def buy_for_self(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_state = get_user_state(user_id)
    push_menu(user_id, subs_list)

    if user_state == BotState.INVOICE_LIST:

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
        formatted_price = format_with_commas(float(invoice_price))
        # Send the invoice or next steps here
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"""🧾 فاکتور شما ایجاد شد. 

💢 درخواست:{invoice_title} 

🛍 مبلغ فاکتور:{formatted_price} تومان

✅ قابل پرداخت:{formatted_price} تومان

🔸 شماره کارت:

12345678998765432
به نام پادرا آهنی

👤 برای ایدی تلگرام :{invoice_username}

📌 لطفا اسکرین شات واریزی را برای ربات ارسال نمایید""",
        )
    else:
        await start(update, context)


# async def handle_username_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.effective_user.id)
#     query = update.callback_query
#     await query.answer()
#     data = query.data

#     if data == "use_telegram_username":
#         # Retrieve username from Telegram user data
#         user_data = update.effective_user
#         username = user_data.username
#         redis_files.set(f"entered_username:{user_id}", username)
#         redis_files.set(f"awaiting_username:{user_id}", "false")
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
    ex_btn = None
    if new_status == "Canceled":
        ex_btn = data[3]

    if new_status == "Reviewing":
        persian_new_status = REVIEWING_TEXT
    elif new_status == "Pay Approved":
        persian_new_status = PAY_APPROVED_TEXT
    elif new_status == "Approved":
        persian_new_status = APPROVED_TEXT
    else:
        persian_new_status = CANCELLED_TEXT

    try:
        # Fetch the invoice to check if it exists
        cur.execute(
            "SELECT id, sub FROM invoice WHERE invoice_id = %s", (invoice_id,))
        result = cur.fetchall()
        user_chat_id, sub_name = result[0]

        if result:
            # Update the status in the db
            cur.execute(
                "UPDATE invoice SET status = %s WHERE invoice_id = %s",
                (new_status, invoice_id),
            )
            conn.commit()

            # Get the existing caption and remove any existing status update
            existing_caption = query.message.caption if query.message.caption else ""
            if STATUS_UPDATED_TEXT in existing_caption:
                existing_caption = existing_caption.split(
                    f"\n{STATUS_UPDATED_TEXT}")[0]

            updated_caption = (
                f"{existing_caption}\n\n{STATUS_UPDATED_TEXT}{persian_new_status}"
            )

            # Define the inline keyboard based on the new status
            inline_keyboard = []
            if new_status == "Pay Approved":
                cur.execute(
                    "UPDATE invoice SET is_paid = %s WHERE invoice_id = %s",
                    ("true", invoice_id),
                )
                conn.commit()
                inline_keyboard = [
                    [
                        InlineKeyboardButton(
                            text=APPROVED_TEXT,
                            callback_data=f"status:{invoice_id}:Approved",
                        ),
                        InlineKeyboardButton(
                            text=CANCELLED_TEXT,
                            callback_data=f"status:{invoice_id}:Canceled:ex_Approved",
                        ),
                    ]
                ]
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=approved_payment(sub_name),
                )
            # elif new_status == "Reviewing":
            #     inline_keyboard = [
            #         [
            #             InlineKeyboardButton(
            #                 text=PAY_APPROVED_TEXT,
            #                 callback_data=f"status:{invoice_id}:Pay Approved",
            #             ),
            #             InlineKeyboardButton(
            #                 text=CANCELLED_TEXT,
            #                 callback_data=f"status:{invoice_id}:Canceled:ex_Pay Approved",
            #             ),
            #         ]
            #     ]
            elif new_status == "Approved":
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=approved(sub_name),
                )
                delete_session(user_chat_id, "invoice_details")
                inline_keyboard = []
            elif new_status == "Canceled" and ex_btn == "ex_Approved":
                in_keyboard = [
                    [
                        InlineKeyboardButton(
                            text=ADMIN_PANEL_TEXT,
                            url="https://t.me/padraahani1386",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=GO_BACK_TEXT, callback_data="go_back_cancelled"
                        ),
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(in_keyboard)
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=cancelled_username_text(sub_name=sub_name),
                    reply_markup=reply_markup,
                )
                delete_session(user_chat_id, "invoice_details")
            elif new_status == "Canceled" and ex_btn == "ex_Pay Approved":
                in_keyboard = [
                    [
                        InlineKeyboardButton(
                            text="ادمین",
                            url="https://t.me/padraahani1386",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=GO_BACK_TEXT, callback_data="go_back_cancelled"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(in_keyboard)
                await context.bot.send_message(
                    chat_id=user_chat_id,
                    text=cancelled_payment_text(sub_name=sub_name),
                    reply_markup=reply_markup,
                )
                delete_session(user_chat_id, "invoice_details")

            reply_markup = (
                InlineKeyboardMarkup(
                    inline_keyboard) if inline_keyboard else None
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


async def cancelled_message_go_back_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    data = await query.answer()
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=query.message.message_id,
    )
    await start(update, context)


async def cancelled_handle_back_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    await start(update, context)


async def buy_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.effective_message.text
    chat_id = update.effective_chat.id
    photo = update.message.photo
    user_state = get_user_state(user_id)

    if photo and user_state == BotState.INVOICE_LIST:
        admin_chat_id = ADMIN_CHAT_ID

        try:
            invoice_details_str = get_session(user_id, "invoice_details")
            if not invoice_details_str:
                raise ValueError("Invoice details not found in Redis")

            # Deserialize the invoice details
            invoice_details = json.loads(invoice_details_str)

            invoice_id = str(uuid.uuid4())[:8]

            user_data = update.message.from_user
            user_id = user_data.id
            user_username = user_data.username
            user_sub = invoice_details.get("title", "N/A")
            sub_price = invoice_details.get("price", "N/A")
            default_sub_status = "Reviewing"

            if user_username:
                cur.execute(
                    "INSERT INTO invoice (id, username, sub, status, invoice_id, price) VALUES (%s, %s, %s, %s, %s, "
                    "%s)",
                    (user_id, user_username, user_sub,
                     default_sub_status, invoice_id, str(sub_price)),
                )
                conn.commit()
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=CHOOSE_USERNAME_ERROR_TEXT,
                )
                return

            file_id = photo[-1].file_id
            # cur.execute(
            #     "SELECT first_name, last_name FROM users WHERE id = %s", user_id
            # )
            # user_data = cur.fetchall()
            user_data = update.message.from_user
            first_name = user_data["first_name"]
            last_name = user_data["last_name"]
            invoice_text = f"""**فاکتور**

درخواست : {invoice_details.get('title', 'N/A')}
نام : {first_name}
نام خانوادگی : {last_name}
ایدی کاربر : {user_id}
ایدی تلگرام اصلی : @{user_username}
ایدی تلگرام وارد شده : {invoice_details.get('description', 'N/A')}
قیمت تتر : {format_with_commas(int(float(last_price)))}
قیمت فاکتور : {invoice_details.get('price', 'N/A')} ت
کارمزد فاکتور : {format_with_commas(fee_amount)}
سود فاکتور : {format_with_commas(profit_amount)}
شماره فاکتور : {invoice_id}"""

            inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text=PAY_APPROVED_TEXT,
                        callback_data=f"status:{invoice_id}:Pay Approved",
                    ),
                    InlineKeyboardButton(
                        text=CANCELLED_TEXT,
                        callback_data=f"status:{invoice_id}:Canceled:ex_Pay Approved",
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(inline_keyboard)

            sent_keyboard = [
                [
                    InlineKeyboardButton(
                        text=GO_BACK_TEXT,
                        callback_data="go_back_cancelled",
                    ),
                ]
            ]
            sent_reply_markup = InlineKeyboardMarkup(sent_keyboard)

            await context.bot.send_photo(
                chat_id=admin_chat_id,
                photo=file_id,
                caption=invoice_text,
                reply_markup=reply_markup,
            )

            set_user_state(user_id, BotState.START)
            await context.bot.send_message(
                chat_id=chat_id,
                text=PHOTO_SENT_SUCCESSFULLY,
                reply_markup=sent_reply_markup,
            )

        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=e,
            )


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(q[0], callback_data=f"faq_{i}")]
        for i, q in enumerate(FAQ_FULL_TEXT)
    ]
    keyboard.append(
        [
            InlineKeyboardButton(
                text=ADMIN_PANEL_TEXT, url="https://t.me/padraahani1386"
            ),
            InlineKeyboardButton(
                GO_BACK_TEXT, callback_data="go_back_cancelled"),
        ],
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(FAQ_TEXT, reply_markup=reply_markup)


async def faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "go_back_faq":
        keyboard = [
            [InlineKeyboardButton(q[0], callback_data=f"faq_{i}")]
            for i, q in enumerate(FAQ_FULL_TEXT)
        ]
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=ADMIN_PANEL_TEXT, url="https://t.me/padraahani1386"
                ),
                InlineKeyboardButton(
                    GO_BACK_TEXT, callback_data="go_back_cancelled"),
            ],
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(FAQ_TEXT, reply_markup=reply_markup)
    else:
        index = int(query.data.split("_")[1])
        question, answer = FAQ_FULL_TEXT[index]
        keyboard = [[InlineKeyboardButton(
            GO_BACK_TEXT, callback_data="go_back_faq")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"{question}\n\n{answer}", reply_markup=reply_markup
        )


async def my_subs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    push_menu(user_id, start)

    user_data = update.message.from_user
    user_id = user_data["id"]

    cur.execute(
        "SELECT username, sub, created, status FROM invoice WHERE id = %s ORDER BY created DESC",
        (str(user_id),),
    )
    user_data = cur.fetchall()

    if user_data:
        status_translation = {
            "Reviewing": REVIEWING_TEXT,
            "Pay Approved": PAY_APPROVED_TEXT,
            "Approved": APPROVED_TEXT,
            "Canceled": CANCELLED_TEXT,
            None: "نامشخص",
        }
        subs_list = "\n".join(
            [
                f"""
💢 درخواست: {sub}
👤 برای ایدی تلگرام : @{username}
📅 ساخته شده : {format_solar_date(gregorian_to_solar(created))}
⭐️ وضعیت : {status_translation.get(status)}
                """
                # f"- @{username}: اشتراک {sub} (تاریخ ایجاد: {created.strftime('%Y-%m-%d %H:%M:%S')}) - وضعیت: {status_translation.get(status, 'نامشخص')}"
                for username, sub, created, status in user_data
            ]
        )
        response_message = f"اشتراک‌های شما:\n{subs_list}"
    else:
        response_message = "شما هیچ اشتراکی ندارید."

    my_subs_keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(my_subs_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=response_message, reply_markup=markup
    )


# Admin handler only


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    admin_keys = [
        [
            KeyboardButton(text=USERS_STATS),
            KeyboardButton(text=SELL_STATS),
        ],
        [
            KeyboardButton(text=SELL_INFO),
        ],
        [KeyboardButton(text=GO_BACK_TEXT),
         ]
    ]

    markup = ReplyKeyboardMarkup(admin_keys, resize_keyboard=True)
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID, text=WELCOME_TEXT, reply_markup=markup
    )


async def user_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = get_total_users()
    daily_new_users = get_daily_new_users()
    weekly_new_users = get_weekly_new_users()
    user_w_paid_invoice = get_user_purchased()

    keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ]
    ]

    markup = ReplyKeyboardMarkup(keys, resize_keyboard=True)

    message_text = f"""
📊 آمار کاربران

تعداد کل کاربران : {total_users}

تعداد کاربران جدید امروز : {daily_new_users}

تعداد کاربران جدید این هفته : {weekly_new_users}

تعداد کاربرانی که حداقل یک خرید انجام دادند : {user_w_paid_invoice} 

"""

    await context.bot.send_message(update.effective_chat.id, message_text, reply_markup=markup)


async def sell_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result, first_day, last_day = get_sell_stats()

    total_paid_invoices = result[0]
    total_sales = result[1]
    total_profit = total_paid_invoices * profit_amount
    if total_sales and total_profit:
        formatted_sales = format_with_commas(total_sales)
        formatted_profit = format_with_commas(total_profit)
    else:
        formatted_sales = 0
        formatted_profit = 0
    print("First Day :", first_day)
    print("last Day :", last_day)

    keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ]
    ]

    markup = ReplyKeyboardMarkup(keys, resize_keyboard=True)

    message_text = f"""
📊 آمار فروش

از تاریخ {format_solar_date(first_day)} تا تاریخ {format_solar_date(last_day)}

تعداد کل خرید ها : {total_paid_invoices}

مقدار فروش کل : {formatted_sales}

مقدار سود کل : {formatted_profit}

"""

    await context.bot.send_message(update.effective_chat.id, message_text, reply_markup=markup)


async def sell_variables(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ]
    ]

    markup = ReplyKeyboardMarkup(keys, resize_keyboard=True)
    message_text = f"""
📊  متغیر های فروش

قیمت اشتراک سه ماهه : ${THREE_M_USD_PRICE}

قیمت اشتراک شش ماه : ${NINE_M_USD_PRICE}

قیمت اشتراک دوازده ماهه : ${TWELVE_M_USD_PRICE}

قیمت کارمزد : ${FEE_AMOUNT}

قیمت سود : ${PROFIT_AMOUNT}

"""

    await context.bot.send_message(update.effective_chat.id, message_text, reply_markup=markup)


async def handle_states(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.effective_chat.id
    user_state = get_user_state(user_id)
    text = update.message.text

    if user_state == BotState.START:
        if text == BUY_PREMIUM_TEXT:
            set_user_state(user_id, BotState.BUY_PREMIUM)
            await buy_sub(update, context)
            # Call appropriate handler
        elif text == MY_PURCHASES_TEXT:
            set_user_state(user_id, BotState.MY_SUBS_LIST)
            await my_subs(update, context)
        elif text == FAQ_TEXT:
            await faq(update, context)
        elif text == ADMIN_PANEL_TEXT:
            set_user_state(user_id, BotState.ADMIN_PANEL)
            await admin_panel(update, context)
        else:
            await start(update, context)
    elif user_state == BotState.BUY_PREMIUM:
        await handle_text_message(update, context)
    elif user_state == BotState.FAQ:
        if text:
            await start(update, context)
    elif user_state == BotState.MY_SUBS_LIST:
        if text == GO_BACK_TEXT:
            await start(update, context)
        else:
            await start(update, context)
    elif user_state == BotState.ADMIN_PANEL:
        if text == USERS_STATS:
            set_user_state(user_id, BotState.USERS_STATS)
            await user_stats_handler(update, context)
        elif text == SELL_STATS:
            set_user_state(user_id, BotState.SELL_STATS)
            await sell_stats_handler(update, context)
        elif text == SELL_INFO:
            set_user_state(user_id, BotState.SELL_VARIABLES)
            await sell_variables(update, context)
        elif text == GO_BACK_TEXT:
            set_user_state(user_id, BotState.START)
            await admin_panel(update, context)
    elif user_state == BotState.USERS_STATS:
        if text == GO_BACK_TEXT:
            set_user_state(user_id, BotState.ADMIN_PANEL)
            await admin_panel(update, context)
    elif user_state == BotState.SELL_STATS:
        if text == GO_BACK_TEXT:
            set_user_state(user_id, BotState.ADMIN_PANEL)
            await admin_panel(update, context)
    elif user_state == BotState.SELL_VARIABLES:
        if text == GO_BACK_TEXT:
            set_user_state(user_id, BotState.ADMIN_PANEL)
            await admin_panel(update, context)
