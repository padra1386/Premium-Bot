from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_connection
from utils import push_menu
import requests
from currencyapi import buy_self_text

BUY_PREMIUM_TEXT = "🛍️ خرید پرمیوم تلگرام"
BUY_FOR_SELF_TEXT = "🙋‍♂️ خرید برای خودم"
BUY_FOR_FRIENDS_TEXT = "🙋‍♂️🙋‍♂️🙋‍♂️ خرید برای دوستان"
BUY_SUCCESS = "✅ خرید با موفقیت انجام شد"
LOREM = "لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ، و با استفاده از طراحان گرافیک است، چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است، و برای شرایط فعلی تکنولوژی مورد نیاز، و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد، کتابهای زیادی در شصت و سه درصد گذشته حال و آینده، شناخت فراوان جامعه و متخصصان را می طلبد، تا با نرم افزارها شناخت بیشتری را برای طراحان رایانه ای علی الخصوص طراحان خلاقی، و فرهنگ پیشرو در زبان فارسی ایجاد کرد، در این صورت می توان امید داشت که تمام و دشواری موجود در ارائه راهکارها، و شرایط سخت تایپ به پایان رسد و زمان مورد نیاز شامل حروفچینی دستاوردهای اصلی، و جوابگوی سوالات پیوسته اهل دنیای موجود طراحی اساسا مورد استفاده قرار گیرد."
FAQ_TEXT = "❓ سوالات پر تکرار"
MY_PURCHASES_TEXT = "❇️ درخواست های من"
GO_BACK_TEXT = "🔙 بازگشت"


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
        chat_id=update.effective_chat.id, text="This is a test", reply_markup=markup
    )


async def buy_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, start)

    buy_keys = [
        [
            KeyboardButton(text=BUY_FOR_SELF_TEXT),
        ],
        [
            KeyboardButton(text=BUY_FOR_FRIENDS_TEXT),
        ],
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(buy_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="انتخاب کنید :", reply_markup=markup
    )


async def buy_for_self(update: Update, context: ContextTypes.DEFAULT_TYPE):
    push_menu(context, buy_sub)

    buy_self_keys = [
        [
            KeyboardButton(text=buy_self_text),
        ],
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(buy_self_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="انتخاب کنید :", reply_markup=markup
    )


async def buy_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.effective_message.text

    user_data = update.message.from_user
    user_id = user_data["id"]
    user_username = user_data["username"]
    user_sub = text

    conn = get_db_connection()
    cur = conn.cursor()

    if user_username:
        cur.execute(
            "INSERT INTO users (id, username, sub) VALUES (%s, %s, %s)",
            (user_id, user_username, user_sub),
        )
        conn.commit()
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="لطفا برای حساب خود یوزرنیم انتخاب کنید",
        )

    cur.close()
    conn.close()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=BUY_SUCCESS)


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

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT username, sub, created FROM users WHERE id = %s", (str(user_id),)
    )
    user_data = cur.fetchall()
    cur.close()
    conn.close()

    if user_data:
        subs_list = "\n".join(
            [
                f"- @{username}: {sub} Premium (Created on: {created.strftime('%Y-%m-%d %H:%M:%S')})"
                for username, sub, created in user_data
            ]
        )
        response_message = f"اشتراک‌های شما:\n{subs_list}"
    else:
        response_message = "شما اشتراکی ندارید."

    my_subs_keys = [
        [
            KeyboardButton(text=GO_BACK_TEXT),
        ],
    ]
    markup = ReplyKeyboardMarkup(my_subs_keys, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=response_message, reply_markup=markup
    )
